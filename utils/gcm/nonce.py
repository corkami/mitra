#!/usr/bin/env python3

# CTR/GCM nonce searching

from Crypto.Cipher import AES

import binascii
import datetime
import multiprocessing
from Crypto.Util.number import long_to_bytes,bytes_to_long
import struct

num_threads = 6

CTR = False # else GCM

COUNTER_START = 0 if CTR else 2

pad16 = lambda s: s + b"\0" * (16-len(s))

def xor(a1, a2):
	assert len(a1) == len(a2)
	return bytes([(a1[i] ^ a2[i]) for i in range(len(a1))])


def xorcmp(a1, a2, x):
	for i, c in enumerate(x):
		if a1[i] ^ a2[i] != c:
			return False
	return True


def nonce_search(thread):
	start_time = datetime.datetime.now()
	hdr_xor_l = len(hdr_xor)
	aes1 = AES.new(pad16(key1), AES.MODE_ECB)
	aes2 = AES.new(pad16(key2), AES.MODE_ECB)

	found_nonce = None
	limit = 2**(8*hdr_xor_l) * 2**16
	start = thread * limit * num_threads
	nonce = (start << 32) + COUNTER_START
	steps = 2**(8*(hdr_xor_l) - 1)

	i = 0
	while i < limit:
		nonce += 1 << 32

		# a good period of calculation
		#if (i % steps) == 0:
		#	print(">  thread %03i searched %016x" % (thread, i))

		block1 = aes1.encrypt(long_to_bytes(nonce, 16))
		block2 = aes2.encrypt(long_to_bytes(nonce, 16))

		if xorcmp(block1, block2, hdr_xor):
			found_nonce = nonce >> 32
			elapsed = datetime.datetime.now() - start_time
			print(" - found 0x%016x [thread:%03i time %s]" %
				(found_nonce, thread, elapsed))
			break

		i += 1

# dual JPGs with comments - xor 
hdr1 = b"\xFF\xD8\xFF\xFE"
hdr2 = hdr1

# PDF / PE
hdr1, hdr2 = [ b"%P", b"MZ" ]


def getMitraOverlap():
	import sys
	fn = sys.argv[1]
	hdr1 = fn[fn.find("{")+1:]
	hdr1 = hdr1[:hdr1.find("}")]
	hdr1 = binascii.unhexlify(hdr1)

	l = len(hdr1)
	with open(fn, "rb") as f:
		hdr2 = f.read(l)

	return hdr1, hdr2


hdr1, hdr2 = getMitraOverlap()

hdr_xor = xor(hdr1,hdr2)

# key1 = b"Now?"
# key2 = b"L4t3r!!!"

key1 = b"\x01" * 16
key2 = b"\x02" * 16

if __name__ == '__main__':
	print("Start time: %s" % datetime.datetime.now())
	if COUNTER_START == 0:
		mode = "CTR"
	elif COUNTER_START == 2:
		mode = "GCM"
	else:
		mode = "unk"
	print("key1: %s (%s)" % (binascii.hexlify(key1), repr(key1)))
	print("key2: %s (%s)" % (binascii.hexlify(key2), repr(key2)))
	print("hdr1: %s (%s)" % (binascii.hexlify(hdr1), repr(hdr1)))
	print("hdr2: %s (%s)" % (binascii.hexlify(hdr2), repr(hdr2)))
	print("start: %i (%s)" % (COUNTER_START, mode))

	multiprocessing.freeze_support()
	pool = multiprocessing.Pool(num_threads)
	retvals = pool.map_async(nonce_search,range(num_threads))
	_ = retvals.get()
	pool.close()
	pool.join()

#!/usr/bin/env python

# CTR/GCM nonce searching

from Crypto.Cipher import AES

import binascii
import multiprocessing
from Crypto.Util.number import long_to_bytes,bytes_to_long
import struct

num_threads = 8

CTR = False # else GCM

COUNTER_START = 0 if CTR else 2

pad16 = lambda s: s + b"\0" * (16-len(s))



def xor(a1, a2):
	assert len(a1) == len(a2)
	return bytes([(a1[i] ^ a2[i]) for i in range(len(a1))])


def NonceToIV(n):
	s = struct.pack(">L", n) + b"\0" * 4
	s = b"\0"*(16 - len(s)) + s
	return s


def nonce_search(offset):
	aes1 = AES.new(pad16(key1), AES.MODE_ECB)
	aes2 = AES.new(pad16(key2), AES.MODE_ECB)

	found_nonce = None
	i = 0
	i //= num_threads
	while i < 2**64:

		nonce = (i*num_threads + offset)

		# a good period of calculation
		if (nonce % 2**24) == 0x1001*offset:
			print(">  thread %02i searched %08x" % (offset, nonce))

		block1 = aes1.encrypt(long_to_bytes((nonce << 32) + COUNTER_START, 16))
		block2 = aes2.encrypt(long_to_bytes((nonce << 32) + COUNTER_START, 16))

		if xor(block1[:hdr_xor_l], block2[:hdr_xor_l]) == hdr_xor:
			print("- nonce: %08i 0x%08x" % (nonce, nonce))
			found_nonce = nonce
			break

		i += 1


# dual JPGs with comments - xor 
hdr1 = b"\xFF\xD8\xFF\xFE"
hdr2 = hdr1

# PDF / PE
hdr1, hdr2 = [ b"%P", b"MZ" ]

hdr_xor = xor(hdr1,hdr2)
hdr_xor_l = len(hdr_xor)

key1 = b"Now?"
key2 = b"L4t3r!!!"

if __name__ == '__main__':
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

	print("Results:")
	#nonce_search(0)
	#sys.exit()
	multiprocessing.freeze_support()
	pool = multiprocessing.Pool(num_threads)
	retvals = pool.map_async(nonce_search,range(num_threads))
	_ = retvals.get()
	pool.close()
	pool.join()


# For references

# key1: 4e6f773f ('Now?')
# key2: 4c34743372212121 ('L4t3r!!!')
# hdr1: 2550 ('%P')
# hdr2: 4d5a ('MZ')
# start: 0 (CTR)
# Results:
# - nonce: 270712 (IV: 00000000000000000004217800000000 )
# - nonce: 276607 (IV: 00000000000000000004387f00000000 )
# - nonce: 386778 (IV: 00000000000000000005e6da00000000 )
# - nonce: 501661 (IV: 00000000000000000007a79d00000000 )

# key1: 4e6f773f ('Now?')
# key2: 4c34743372212121 ('L4t3r!!!')
# hdr1: 414243 ('ABC')
# hdr2: 313233 ('123')
# start: 2 (GCM)
# Results:
# - nonce: 00703091 (IV: 0000000000000000000aba7300000000 )
# - nonce: 40314641 (IV: 00000000000000000267271100000000 )
# - nonce: 49065134 (IV: 000000000000000002ecacae00000000 )
# - nonce: 78863479 (IV: 000000000000000004b35c7700000000 )
# - nonce: 148076704 (IV: 000000000000000008d378a000000000 )
# - nonce: 153466557 (IV: 00000000000000000925b6bd00000000 )

# key1: 4e6f773f ('Now?')
# key2: 4c34743372212121 ('L4t3r!!!')
# hdr1: ffd8fffe ('\xff\xd8\xff\xfe')
# hdr2: ffd8fffe ('\xff\xd8\xff\xfe')
# start: 2 (GCM)
# Results:
# - nonce: 8108314280 (0x1E34B0EA8)

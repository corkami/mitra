#!/usr/bin/env python3

# Fix a JPG file with 4 bytes of overlap
# so that the file structure matches the parasite length

from Crypto.Cipher import AES

import binascii
from Crypto.Util.number import long_to_bytes,bytes_to_long
import struct
import sys


COUNTER_START = 0 # CTR
COUNTER_START = 2 # GCM

pad16 = lambda s: s + b"\0" * (16-len(s))

def xor(a1, a2):
	assert len(a1) == len(a2)
	return bytes([(a1[i] ^ a2[i]) for i in range(len(a1))])


fn, nonce = sys.argv[1:3]

# 00 01 02 03 04 05 06
# FF D8 FF FE XX YY

# get the current file start - including the other lower byte.
with open(fn, "rb") as fin:
	data = fin.read()
curHdr = data[:16]


# get the other file start from the filename - including the other higher byte.
othHdr = fn[fn.find("{")+1:]
othHdr = othHdr[:othHdr.find("}")]
othHdr = binascii.unhexlify(othHdr)
assert len(othHdr) == 4

splits = fn[fn.find("(")+1:]
splits = splits[:splits.find(")")]
splits = splits.split("-")
splits = [int(i, 16) for i in splits]
assert len(splits) == 2
assert splits[0] == 4

last_split = splits[1]
old_length = last_split - 4

# get the keys and nonce
key1 = b"\x01" * 16 # b"Now?"
key2 = b"\x02" * 16 # b"L4t3r!!!"
if nonce.startswith("0x"):
	nonce = int(nonce, 16)
else:
	nonce = int(nonce)
print("Nonce: %i 0x%x" % (nonce, nonce))
print("Keys: %s %s" % (repr(key1), repr(key2)))

nonce = (nonce << 32) + COUNTER_START

# generate keystreams
aes1 = AES.new(pad16(key1), AES.MODE_ECB)
aes2 = AES.new(pad16(key2), AES.MODE_ECB)

block1 = aes1.encrypt(long_to_bytes(nonce, 16))
block2 = aes2.encrypt(long_to_bytes(nonce, 16))

# encrypt merged start twice
mergedHdr = othHdr[:4] + curHdr[4:]
encHdr = xor(block1, mergedHdr)
encHdr = xor(block2, encHdr)


# it should match the start of the current file.
assert encHdr[:4] == curHdr[:4]

# get the encrypted lower nibble
high = encHdr[4]
low = encHdr[5]

# get the full parasite length
new_length = 0x100 * high + low
print("Old length: %i 0x%x" % (old_length,old_length))
print("New length: %i 0x%x" % (new_length,new_length))
assert new_length >= old_length
delta = new_length - old_length

# go to higher byte offset, grow by encrypted lower nibble.
cut = last_split
fixed = b"".join([
	data[:cut],
	delta*b"\0",
  data[cut:],
	])

with open("4-%s" % fn, "wb") as fout:
	fout.write(fixed)

#!/usr/bin/env python3

"""
Take a polyglot from mitra,
generate a OFB ciphertext which decrypts correctly under two different algorithms with the same key.

iv = dec(c0 ^ p0)
"""

import binascii
import os
import argparse
import re
from Crypto.Cipher import AES
from Crypto.Cipher import Blowfish as OtherAlgo
from Crypto.Util.number import long_to_bytes,bytes_to_long
from Crypto.Util.number import long_to_bytes as l2b
from Crypto.Util.number import bytes_to_long as b2l


BLOCKLEN = 16

pad16 = lambda s: s + b"\0" * (16-len(s))
b2a = lambda b: repr(b)[2:-1]


def xor(_a1, _a2):
	assert len(_a1) == len(_a2)
	return bytes([(_a1[i] ^ _a2[i]) for i in range(len(_a1))])


def pad(_d, _alig):
	d_l = len(_d)
	_d = _d if 0 == d_l % _alig else _d + b'\x00' * (_alig - d_l % _alig)

	assert len(_d) % _alig == 0

	return _d


def unhextry(_d):
	try:
		_d = binascii.unhexlify(_d)
	except Exception:
		pass # TypeError: Non-hexadecimal digit found
	return _d


def getKSaes(key, iv, bCount):
	aesECB = AES.new(key, AES.MODE_ECB)
	curBlock = iv
	stream = b""
	for _ in range(bCount + 1):
		curBlock = aesECB.encrypt(curBlock) 
		stream += curBlock
	assert len(stream) == 16*(bCount+1)
	return stream

def getKSother(key, iv, bCount):
	otherECB = OtherAlgo.new(key, OtherAlgo.MODE_ECB)
	curBlock = iv
	stream = b""
	for _ in range(2*bCount + 10): # different count
		curBlock = otherECB.encrypt(curBlock)
		stream += curBlock
	assert len(stream) >= 16*(bCount+1)
	return stream


def mix(d1, d2, l):
	assert len(d1) == len(d2)
	mix = b""
	start = 0
	in1 = True
	for end in l:
		mix += d1[start:end] if in1 else d2[start:end]
		in1 = not in1
		start = end
	mix += d1[start:] if in1 else d2[start:]
	return mix

IVS = {}


if __name__=='__main__':
	parser = argparse.ArgumentParser(description="Turn a non-overlapping polyglot into a dual AES-OFB ciphertext.")
	parser.add_argument('polyglot',
		help="input polyglot - requires special naming like 'P(10-5c).png.rar'.")
	parser.add_argument('output',
		help="generated file.")
	parser.add_argument('-i', '--iv', default=b"0",
		help="nonce - default: 0.")
	parser.add_argument('-k', '--keys', nargs=2, default=b"QuandYenAMarre!!",
		help="encryption keys - default: Now? / L4t3r!!!.")

	args = parser.parse_args()

	fnmix = args.polyglot
	fnpoc = args.output
	key = args.keys
	iv = args.iv

	iv = pad16(unhextry(iv))
	key = pad16(unhextry(key))

	with open(fnmix, "rb") as file:
		dIn = file.read()
	dIn = pad(dIn, BLOCKLEN) # the padding will break with formats not supporting appended data



	# fnmix should come from Mitra and
	# has a naming convention like "P(14-89)-ID3v2[Zip].4d01e2fb.mp3.zip"
	swaps = [int(i, 16) for i in fnmix[fnmix.find("(") + 1:fnmix.find(")")].split("-")]
	exts = fnmix[-9:].split(".")[-2:]
	

	assert len(dIn) % 16 == 0
	bCount = len(dIn) // 16

	ksAES = getKSaes(key, iv, bCount)
	ksOther = getKSother(key, iv[:8], bCount) # different IV size

	dCrypt1 = xor(dIn, ksAES[:len(dIn)])
	dCrypt2 = xor(dIn, ksOther[:len(dIn)])
	dOut = mix(dCrypt1, dCrypt2, swaps)

	ctxt = dOut

	output = "\n".join([
			"key: %s" % b2a(binascii.hexlify(key)),
			"iv: %s" % b2a(binascii.hexlify(iv)),
			"ciphertext: %s" % b2a(binascii.hexlify(ctxt)),
		  "exts: %s" % " ".join(exts),
		  "origin: %s" % fnmix,
		])
	with open(fnpoc, "wb") as fpoc:
		fpoc.write(output.encode())
		fpoc.close()

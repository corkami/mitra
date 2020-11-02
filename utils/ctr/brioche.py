#!/usr/bin/env python

"""
Take a polyglot from mitra, Generate a CTR ciphertext
which decrypts correctly under two different keys
"""

import binascii
import argparse
from Crypto.Cipher import AES
from Crypto.Util.number import long_to_bytes as l2b
from Crypto.Util.number import bytes_to_long as b2l
import BitVector as bv


DEBUG = True
DEBUG = False

BLOCKLEN = 16
all_zeros = b'\x00'*BLOCKLEN


pad16 = lambda s: s + "\0" * (16-len(s))
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


def getKS(key, nonce, bCount, initCount=0): # initCount = 2 for GCM, 0 for CTR
	aesECB = AES.new(key, AES.MODE_ECB)
	stream = b"".join([aesECB.encrypt(l2b((nonce << 32) + initCount + i, 16)) for i in range(bCount+1)])
	assert len(stream) == 16*(bCount+1)
	return stream


def xor(a1, a2):
	assert len(a1) == len(a2)
	return bytes([(a1[i] ^ a2[i]) for i in range(len(a1))])


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


if __name__=='__main__':
	parser = argparse.ArgumentParser(description="Turn a non-overlapping polyglot into a dual AES-GCM ciphertext.")
	parser.add_argument('polyglot',
		help="input polyglot - requires special naming like 'P(10-5c).png.rar'.")
	parser.add_argument('output',
		help="generated file.")
	parser.add_argument('-k', '--keys', nargs=2, default=["Now?", "L4t3r!!!"],
		help="encryption keys - default: Now? / L4t3r!!!.")
	parser.add_argument('-n', '--nonce', default=0,
		help="nonce - default: 0.")

	args = parser.parse_args()

	fnmix = args.polyglot
	fnpoc = args.output
	key1, key2 = args.keys
	nonce = args.nonce

	key1 = pad16(unhextry(key1)).encode().ljust(3)
	key2 = pad16(unhextry(key2)).encode().ljust(3)
	assert not key1 == key2

	noncei = int(nonce)
	nonceb = l2b(int(nonce),12)

	# fnmix should come from Mitra and
	# has a naming convention like "P(14-89)-ID3v2[Zip].4d01e2fb.mp3.zip"
	swaps = [int(i, 16) for i in fnmix[fnmix.find("(") + 1:fnmix.find(")")].split("-")]
	exts = fnmix[-9:].split(".")[-2:]

	with open(fnmix, "rb") as file:
		dIn = file.read()
	dIn = pad(dIn, BLOCKLEN) # the padding will break with formats not supporting appended data

	assert len(dIn) % 16 == 0
	bCount = len(dIn) // 16

	ks1 = getKS(key1, noncei, bCount)
	ks2 = getKS(key2, noncei, bCount)

	dCrypt1 = xor(dIn, ks1[:len(dIn)])
	dCrypt2 = xor(dIn, ks2[:len(dIn)])

	dOut = mix(dCrypt1, dCrypt2, swaps)

	key1_s = b2a(binascii.hexlify(key1.strip())).rstrip("00")
	key2_s = b2a(binascii.hexlify(key2.strip())).rstrip("00")
	iv_s = b2a(binascii.hexlify(nonceb)).rstrip("00")
	if iv_s == "":
		iv_s = "0"

	with open(fnpoc, "wb") as fpoc:
		fpoc.write(dOut)
		fpoc.close()

	print("Generated output: %s" % (fnpoc))
	print("Tests:")
	print(" openssl enc -in %s -out output1.%s -aes-128-ctr -iv %s -K %s" % (fnpoc, exts[0].ljust(3), iv_s, key1_s))
	print(" openssl enc -in %s -out output2.%s -aes-128-ctr -iv %s -K %s" % (fnpoc, exts[1].ljust(3), iv_s, key2_s))

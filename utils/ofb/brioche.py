#!/usr/bin/env python3

"""
Take a polyglot from mitra,
generate a OFB ciphertext which decrypts correctly under two different keys.

iv = dec(c0 ^ p0)
"""

import binascii
import os
import argparse
import re
from Crypto.Cipher import AES
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


def getKS(key, iv, bCount):
	aesECB = AES.new(key, AES.MODE_ECB)
	curBlock = iv
	stream = b""
	for _ in range(bCount + 1):
		curBlock = aesECB.encrypt(curBlock) 
		stream += curBlock
	assert len(stream) == 16*(bCount+1)
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


dir_path = os.path.dirname(os.path.realpath(__file__))
ivsfn = os.path.join(dir_path, "ivs.txt")
with open(ivsfn, "r") as f:
	iv_data = f.readlines()
IVS = {}
for l in iv_data:
	if l.count("#") > 0:
		l = l[:l.find("#")]
	l = l.strip()
	if l == "":
		continue
	l = re.split(r'\s+', l)
	if len(l) != 6:
		continue
	iv,types,header1, header2, key1, key2 = l
	if len(header1) != len(header2):
		continue
	if len(key1) != len(key2):
		continue
	header1 = binascii.unhexlify(header1)
	header2 = binascii.unhexlify(header2)
	key1 = binascii.unhexlify(key1)
	key2 = binascii.unhexlify(key2)
	iv = binascii.unhexlify(iv)
	xor_hdr = xor(header1, header2)
	IVS[(xor_hdr, key1, key2)] = iv


if __name__=='__main__':
	parser = argparse.ArgumentParser(description="Turn a non-overlapping polyglot into a dual AES-OFB ciphertext.")
	parser.add_argument('polyglot',
		help="input polyglot - requires special naming like 'P(10-5c).png.rar'.")
	parser.add_argument('output',
		help="generated file.")
	parser.add_argument('-i', '--iv', default=b"0",
		help="nonce - default: 0.")
	parser.add_argument('-k', '--keys', nargs=2, default=[b"Now?", b"L4t3r!!!"],
		help="encryption keys - default: Now? / L4t3r!!!.")

	args = parser.parse_args()

	fnmix = args.polyglot
	fnpoc = args.output
	key1, key2 = args.keys
	iv = args.iv

	iv = pad16(unhextry(iv))
	key1 = pad16(unhextry(key1))
	key2 = pad16(unhextry(key2))

	with open(fnmix, "rb") as file:
		dIn = file.read()
	dIn = pad(dIn, BLOCKLEN) # the padding will break with formats not supporting appended data

	assert not key1 == key2


	# fnmix should come from Mitra and
	# has a naming convention like "P(14-89)-ID3v2[Zip].4d01e2fb.mp3.zip"
	swaps = [int(i, 16) for i in fnmix[fnmix.find("(") + 1:fnmix.find(")")].split("-")]
	exts = fnmix[-9:].split(".")[-2:]
	


	def BruteIv(fn):
		hdr1 = fn[fn.find("{")+1:]
		hdr1 = hdr1[:hdr1.find("}")]
		hdr1 = binascii.unhexlify(hdr1)

		hdr2 = dIn[:len(hdr1)]
		hdr_xor = xor(hdr1,hdr2)
		t = (hdr_xor, key1, key2)
		if t in IVS:
			iv = IVS[t]
			print("IV already computed")
			return iv
		hdr_xor_l = len(hdr_xor)
		aes1 = AES.new(key1, AES.MODE_ECB)
		aes2 = AES.new(key2, AES.MODE_ECB)

		i = 0
		for i in range(2**64):
			iv_s = long_to_bytes(i, 16)
			block1 = aes1.encrypt(iv_s)
			block2 = aes2.encrypt(iv_s)

			if xor(block1[:hdr_xor_l], block2[:hdr_xor_l]) == hdr_xor:
				print("Bruteforce results:")
				print(" ".join("%s" % b2a(binascii.hexlify(i)) for i in [iv_s, hdr1, hdr2, key1, key2]))
				return iv_s
		return None


	if fnmix.startswith("O") and \
		"{" in fnmix and \
		"}" in fnmix:
		print("Overlap file found")
		iv = BruteIv(fnmix)
		print("IV: %s" % b2a(binascii.hexlify(iv)))


	assert len(dIn) % 16 == 0
	bCount = len(dIn) // 16

	ks1 = getKS(key1, iv, bCount)
	ks2 = getKS(key2, iv, bCount)

	dCrypt1 = xor(dIn, ks1[:len(dIn)])
	dCrypt2 = xor(dIn, ks2[:len(dIn)])
	dOut = mix(dCrypt1, dCrypt2, swaps)

	print("key 1:", b2a(key1.strip(b"\0")))
	print("key 2:", b2a(key2.strip(b"\0")))

	ctxt = dOut

	output = "\n".join([
			"key1: %s" % b2a(binascii.hexlify(key1)),
			"key2: %s" % b2a(binascii.hexlify(key2)),
			"iv: %s" % b2a(binascii.hexlify(iv)),
			"ciphertext: %s" % b2a(binascii.hexlify(ctxt)),
		  "exts: %s" % " ".join(exts),
		  "origin: %s" % fnmix,
		])
	with open(fnpoc, "wb") as fpoc:
		fpoc.write(output.encode())
		fpoc.close()

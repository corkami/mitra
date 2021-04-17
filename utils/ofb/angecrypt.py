#!/usr/bin/env python3

"""
AngeCryption from Mitra:
Take a polyglot from mitra,
make the file encrypt to another valid file via AES-OFB with a crafted IV
"""

import binascii
import argparse
from Crypto.Cipher import AES

BLOCKLEN = 16

pad = lambda s: s + b"\0" * (BLOCKLEN - (len(s) % BLOCKLEN)) 
b2a = lambda b: repr(b)[2:-1]

def unhextry(_d):
	try:
		_d = binascii.unhexlify(_d)
	except Exception:
		pass # TypeError: Non-hexadecimal digit found
	return _d


def getOverlap(fnin):
	assert "{" in fnin # is it required ?
	other_hdr = b""
	other_hdr = fnin[fnin.find("{")+1:]
	other_hdr = other_hdr[:other_hdr.find("}")]
	other_hdr = binascii.unhexlify(other_hdr)
	hdr_l = len(other_hdr)
	print("Other header read from filename: `%s`" % b2a(binascii.hexlify(other_hdr)))

	return other_hdr, hdr_l


def getSwap(fnin, hdr_l):
	assert "(" in fnin
	swaps = [int(i, 16) for i in fnin[fnin.find("(") + 1:fnin.find(")")].split("-")]
	assert len(swaps) == 2
	#assert swaps[0] == hdr_l
	assert swaps[1] % BLOCKLEN == 0
	swap = swaps[1]

	return swap


if __name__=='__main__':
	parser = argparse.ArgumentParser(
		description="Turn an overlapping polyglot into a file staying valid after AES-OFB encryption.")
	parser.add_argument('polyglot',
		help=r"input polyglot - requires special naming like 'O(6-70){89504E470D0A}.png'.")
	parser.add_argument('output',
		help="generated file.")
	parser.add_argument('-k', '--key', nargs=1, default=b"AngeCryption!!!",
		help="encryption key - default: AngeCryption!!!.")

	args = parser.parse_args()

	fnin = args.polyglot
	fnpoc = args.output
	key = args.key
	key = b"\x01" * 16

	key = unhextry(key)
	key_s = b2a(binascii.hexlify(key))

	exts = fnin[-9:].split(".")[-2:]

	other_hdr, hdr_l = getOverlap(fnin)
	assert hdr_l <= BLOCKLEN
	swap = getSwap(fnin, hdr_l)

	with open(fnin, "rb") as file:
		dIn = file.read()

	# need swapping because Mitra produce parasite polyglots by default
	# and we need the top content parsed in plaintext.
	other_hdr, dIn = dIn[:hdr_l], other_hdr + dIn[hdr_l:]

	plain0 = dIn[:BLOCKLEN]
	# print("first plaintext block", plain0)

	cipher0 = other_hdr + dIn[len(other_hdr):BLOCKLEN]
	# print("other plaintext block:", cipher0)

	ecb_dec = AES.new(key, AES.MODE_ECB)
	# print("Other after decryption:", cipher0)

	# c = p ^ enc(iv) => iv = dec(p ^ c)
	iv = bytearray([cipher0[i] ^ plain0[i] for i in range(BLOCKLEN)])
	iv = ecb_dec.decrypt(iv)
	iv_s = b2a(binascii.hexlify(iv))

	ofb_enc = AES.new(key, AES.MODE_OFB, iv)
	dOut = ofb_enc.encrypt(dIn[:swap]) + dIn[swap:]

	ofb_dec = AES.new(key, AES.MODE_OFB, iv)
	dOut = ofb_dec.decrypt(pad(dOut))

	output = "\n".join([
			"plaintext: %s" % b2a(binascii.hexlify(dOut)),
			"key: %s" % b2a(binascii.hexlify(key)),
			"iv: %s" % iv_s,
		  "exts: %s" % " ".join(exts),
		  "origin: %s" % fnin,
		])

	fnoutput = "%s.%s" % (fnpoc, exts[0])
	print("Generated input file: %s" % (fnpoc))
	with open(fnpoc, "wb") as fpoc:
		fpoc.write(output.encode())
		fpoc.close()

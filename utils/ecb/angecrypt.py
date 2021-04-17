#!/usr/bin/env python3

"""
AngeCryption from Mitra:
Take a polyglot from mitra,
make the file encrypt to another valid file via AES-ECB (requires no overlap)
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


def getSwaps(fnin):
	assert "(" in fnin
	swaps = [int(i, 16) for i in fnin[fnin.find("(") + 1:fnin.find(")")].split("-")]
	assert len(swaps) == 2
	assert swaps[0] % BLOCKLEN == 0
	assert swaps[1] % BLOCKLEN == 0

	return swaps


if __name__=='__main__':
	parser = argparse.ArgumentParser(
		description="Turn a non-overlapping polyglot into a file staying valid after AES-ECB encryption.")
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

	swaps = getSwaps(fnin)
	exts = fnin[-9:].split(".")[-2:]

	with open(fnin, "rb") as file:
		dIn = file.read()

	ecb_dec = AES.new(key, AES.MODE_ECB)
	dOut = dIn[:swaps[0]] + \
		ecb_dec.decrypt(dIn[swaps[0]:swaps[1]]) + \
		dIn[swaps[1]:]
	print(len())

	output = "\n".join([
			"plaintext: %s" % b2a(binascii.hexlify(dOut)),
			"key: %s" % b2a(binascii.hexlify(key)),
		  "exts: %s" % " ".join(exts),
		  "origin: %s" % fnin,
		])

	fnoutput = "%s.%s" % (fnpoc, exts[0])
	print("Generated input file: %s" % (fnpoc))
	with open(fnpoc, "wb") as fpoc:
		fpoc.write(output.encode())
		fpoc.close()

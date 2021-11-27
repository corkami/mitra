#!/usr/bin/env python3

# Malabar (AES/Blowfish) decryption for OFB

import sys

import os
import hashlib
import binascii
import struct
from Crypto.Cipher import AES
from Crypto.Cipher import Blowfish as OtherAlgo


if __name__=='__main__':
	fname = sys.argv[1]
	with open(fname, "rb") as f:
		lines = f.readlines()

	for line in lines:
		line = line.strip()
		l = line.split(b": ")
		if l[1].startswith(b"b'") and l[1][-1] == 39:
			l[1] = l[1][2:-1]
		vars()[l[0].decode("utf-8").lower()] = l[1].strip().decode("utf-8")

	for v in ["key", "iv", "ciphertext"]:
		vars()[v] = binascii.unhexlify(vars()[v])

	ofb1 = AES.new(key, AES.MODE_OFB, iv)
	ofb2 = OtherAlgo.new(key, OtherAlgo.MODE_OFB, iv[:8])
	plaintxt1 = ofb1.decrypt(ciphertext)
	plaintxt2 = ofb2.decrypt(ciphertext)
	assert not plaintxt1 == plaintxt2

	hash = hashlib.sha256(ciphertext).hexdigest()[:8].lower()

	fname = os. path.splitext(fname)[0] # remove file extension

	exts = exts.split(" ")[-2:]
	with open("%s-1.%s.%s" % (fname, hash, exts[0]), "wb") as file1:
		file1.write(plaintxt1)

	with open("%s-2.%s.%s" % (fname, hash, exts[1]), "wb") as file2:
		file2.write(plaintxt2)

	print("key:", key.rstrip(b"\0"))
	print("iv:", iv)
	print("Success!")
	print()
	print("plaintext1:", binascii.hexlify(plaintxt1[:16]),"...")
	print("plaintext2:", binascii.hexlify(plaintxt2[:16]),"...")

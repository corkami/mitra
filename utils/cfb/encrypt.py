#!/usr/bin/env python3

# CFB encryption - for AngeCryption

import sys

import os
import hashlib
import binascii
from Crypto.Cipher import AES

MODE = AES.MODE_CFB

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

	key_s = key
	iv_s = iv
	for v in ["key", "iv", "plaintext"]:
		vars()[v] = binascii.unhexlify(vars()[v])

	cfb = AES.new(key, MODE, iv, segment_size=128)
	ciphertext = cfb.encrypt(plaintext)

	hash_ = hashlib.sha256(plaintext).hexdigest()[:8].lower()

	fname = os. path.splitext(fname)[0] # remove file extension

	exts = exts.split(" ")[-2:]
	fn1 = "%s.%s.%s" % (fname, hash_, exts[0])
	with open(fn1, "wb") as file1:
		file1.write(plaintext)

	fn2 = "%s.%s.%s" % (fname, hash_, exts[1])
	with open(fn2, "wb") as file2:
		file2.write(ciphertext)

	print("key:", key.rstrip(b"\0"))
	print("iv:", iv_s)
	print()
	print("plaintext1:", binascii.hexlify(plaintext[:32]),"...")
	print("plaintext2:", binascii.hexlify(ciphertext[:32]),"...")
	print()
	print("Test:")
	print(" openssl enc -in %s -out %s -aes-128-cfb -iv %s -K %s" % (fn1, fn2, iv_s, key_s))

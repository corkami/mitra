#!/usr/bin/env python3

import sys

import os
import hashlib
import binascii
import struct
from Crypto.Util.number import long_to_bytes,bytes_to_long
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


def gcm_decrypt(_key,_nonce,_ctxt,_tag,_ad):
	decryptor = Cipher(
		algorithms.AES(_key),
		modes.GCM(_nonce,_tag),
		backend=default_backend()
	).decryptor()

	decryptor.authenticate_additional_data(_ad)

	pt = decryptor.update(_ctxt) + decryptor.finalize()
	return pt


if __name__=='__main__':
	fname = sys.argv[1]
	with open(fname, "rb") as f:
		lines = f.readlines()

	for line in lines:
		line = line.strip()
		l = line.split(b": ")
		vars()[l[0].decode("utf-8")] = l[1].strip().decode("utf-8")

	for v in ["key1", "key2", "adata", "nonce", "ciphertext", "tag"]:
		vars()[v] = binascii.unhexlify(vars()[v])

	assert not key1 == key2
	plaintxt1 = gcm_decrypt(key1, nonce, ciphertext, tag, adata)
	plaintxt2 = gcm_decrypt(key2, nonce, ciphertext, tag, adata)
	assert not plaintxt1 == plaintxt2

	success = False
	try:
		invalidkey = b'\x07'*16
		plaintxt1 = gcm_decrypt(invalidkey, nonce, ciphertext, tag, adata)
	except Exception:
		success = True
	if not success:
		print("Decryption with other key failed didn't fail as expected")

	hash = hashlib.sha256(ciphertext).hexdigest()[:8].lower()

	fname = os. path.splitext(fname)[0] # remove file extension

	exts = exts.split(" ")[-2:]
	with open("%s-1.%s.%s" % (fname, hash, exts[0]), "wb") as file1:
		file1.write(plaintxt1)

	with open("%s-2.%s.%s" % (fname, hash, exts[1]), "wb") as file2:
		file2.write(plaintxt2)

	print("key1:", key1.rstrip(b"\0"))
	print("key1:", key2.rstrip(b"\0"))
	print("ad:", adata.rstrip(b"\0"))
	print("nonce:", bytes_to_long(nonce))
	print("tag:", binascii.hexlify(tag))
	print("Success!")
	print()
	print("plaintext1:", binascii.hexlify(plaintxt1[:16]),"...")
	print("plaintext2:", binascii.hexlify(plaintxt2[:16]),"...")

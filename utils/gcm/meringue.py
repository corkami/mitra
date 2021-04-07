#!/usr/bin/env python3

"""
Take a polyglot from mitra, Generate a GCM ciphertext which decrypts correctly under two different keys
"""

from aes_gcm import AES_GCM,InvalidTagException,gf_2_128_mul
from Crypto.Cipher import AES
from Crypto.Random.random import getrandbits
from Crypto.Util.number import long_to_bytes,bytes_to_long
from Crypto.Util.number import long_to_bytes as l2b
from Crypto.Util.number import bytes_to_long as b2l
import BitVector as bv
import binascii
import os
import sys
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes

import base64
import argparse
import re


DEBUG = True
DEBUG = False

BLOCKLEN = 16
all_zeros = b'\x00'*BLOCKLEN
gcm_modulus_array = [1] + [0]*120 + [1, 0, 0, 0, 0, 1, 1, 1]
gcm_modulus = bv.BitVector(bitlist = list(gcm_modulus_array))


pad16 = lambda s: s + b"\0" * (16-len(s))
b2a = lambda b: repr(b)[2:-1]


import os 
dir_path = os.path.dirname(os.path.realpath(__file__))
invertsfn = os.path.join(dir_path, "inverts.txt")
with open(invertsfn, "r") as f:
	invert_data = f.readlines()

INVERTS = {}
for l in invert_data:
	l = l.strip()
	if l == "":
		continue
	if l.startswith("#"):
		continue
	els = l.split(" ")[:2]
	if len(els) < 2:
		continue
	if len(els[0]) != 32:
		continue
	if len(els[1]) != 32:
		continue
	a = els[0].encode()
	b = int(els[1], 16)
	INVERTS[a] = b

def xor(_a1, _a2):
	assert len(_a1) == len(_a2)
	return bytes([(_a1[i] ^ _a2[i]) for i in range(len(_a1))])


noncesfn = os.path.join(dir_path, "nonces.txt")
with open(noncesfn, "r") as f:
	nonce_data = f.readlines()
NONCES = {}
for l in nonce_data:
	if l.count("#") > 0:
		l = l[:l.find("#")]
	l = l.strip()
	if l == "":
		continue
	l = re.split('\s+', l)
	if len(l) != 6:
		continue
	nonce,types,header1, header2, key1, key2 = l
	if len(header1) != len(header2):
		continue
	if len(key1) != len(key2):
		continue
	nonce = int(nonce, 16)
	header1 = binascii.unhexlify(header1)
	header2 = binascii.unhexlify(header2)
	key1 = binascii.unhexlify(key1)
	key2 = binascii.unhexlify(key2)
	xor_hdr = xor(header1, header2)
#	print(types.ljust(10), binascii.hexlify(xor_hdr).decode(), nonce)
	NONCES[(xor_hdr, key1, key2)] = nonce

def ifAdd(_a1, _a2):
	return l2b(b2l(_a1) ^ b2l(_a2), 16)


def ifAddL(_a1,_a2):
	return l2b(_a1 ^ _a2, 16)


def pad(_d, _alig):
	d_l = len(_d)
	_d = _d if 0 == d_l % _alig else _d + b'\x00' * (_alig - d_l % _alig)

	assert len(_d) % _alig == 0

	return _d


def ifInvert(_val):
	le_bv_to_invert = le_bv(_val)
	inverse = le_bv_to_invert.gf_MI(gcm_modulus, 128)
	return int(bv.BitVector(bitstring=str(inverse)[::-1]))


# Get a little-endian BitVector representation of the byte array input
def le_bv(_input_ba):
	longval_a1 = b2l(_input_ba)
	bv_a1 = bv.BitVector(intVal=longval_a1, size=128)
	return bv.BitVector(bitstring=str(bv_a1)[::-1])


def ifMul(_a1, _a2):
	old_product = gf_2_128_mul(b2l(_a1),b2l(_a2))
	return l2b(old_product, 16)


def ifSquare(_a1):
	return gf_2_128_mul(b2l(_a1),b2l(_a1))


def ifCube(_a1):
	return gf_2_128_mul(gf_2_128_mul(b2l(_a1),b2l(_a1)),b2l(_a1))


def gcm_encrypt(_key, _nonce, _pt, _ad):
	encryptor = Cipher(
		algorithms.AES(_key),
		modes.GCM(_nonce),
		backend=default_backend()
	).encryptor()

	encryptor.authenticate_additional_data(_ad)

	ct = encryptor.update(_pt) + encryptor.finalize()
	return ct, encryptor.tag


def gcm_decrypt(_key, _nonce, _cipher, _tag, _ad):
	decryptor = Cipher(
		algorithms.AES(_key),
		modes.GCM(_nonce, _tag),
		backend=default_backend()
	).decryptor()

	decryptor.authenticate_additional_data(_ad)

	pt = decryptor.update(_cipher) + decryptor.finalize()
	return pt


def unhextry(_d):
	try:
		_d = binascii.unhexlify(_d)
	except Exception:
		pass # TypeError: Non-hexadecimal digit found
	return _d


# returns an array of size pows+1 whose i-th component is H1^i + H2^i
def getCoeffs(_H1, _H2, _pows, DEBUG=False):
	print("Computing", _pows, "coefficients.")

	retval = [l2b(1, 16), ifAdd(_H1,_H2)]
	prev_H1 = _H1
	prev_H2 = _H2
	for i in range(2, _pows+1):
		prev_H1 = ifMul(prev_H1, _H1)
		prev_H2 = ifMul(prev_H2, _H2)
		retval.append(ifAdd(prev_H1, prev_H2))

	# sanity check
	assert retval[1] == ifAdd(_H1, _H2)
	assert retval[2] == ifAddL(ifSquare(_H1), ifSquare(_H2))
	assert retval[3] == ifAddL(ifCube(_H1), ifCube(_H2))

	return retval


def getInverse(_coef):
	global invert_data
	print("Coef to be inverted: %s" % b2a(_coef), end = '')
	if _coef in INVERTS:
		print(" (already computed)")
		inverse = INVERTS[_coef]
	else:
		print(" (not present)")
		print("Inverting the coefficient (takes a few mins)...")
		inverse = ifInvert(binascii.unhexlify(_coef))
		a, b = repr(_coef)[2:-1], repr(binascii.hexlify(l2b(inverse, 16)))[2:-1]
		print("New invert:", a, b)
		with open(invertsfn, "w") as f:
			invert_data += ["\n%s %s" % (a, b)]
			f.write("".join(invert_data))
	return inverse


def ad_sum(_ad, _coeffs, _len):
	sum_ = all_zeros
	for i in range(len(_ad)//16):
		# A_i
		curr_ad_block = _ad[16*i:16*(i+1)]
		curr_ad_coeff = _coeffs[_len-i]
		sum_ = ifAdd(sum_, ifMul(curr_ad_block, curr_ad_coeff))
	return sum_


def getSum(_ad, _coeffs, _pads, _ct, _idx):
	ct_bl = 8 * len(_ct) * 16
	ct_bkl = len(_ct)
	ad_bl = 8*len(_ad)

	sum_ = ad_sum(_ad, _coeffs, ad_bl//128 + ct_bkl + 1)

	lenblock = l2b(ad_bl, 8) + l2b(ct_bl, 8)
	lenblock_term = ifMul(_coeffs[1], lenblock)
	sum_ = ifAdd(sum_, lenblock_term)
	sum_ = ifAdd(sum_, _pads)
	for i in range(len(_ct)):
		if not i == _idx:
			block = _ct[i]
			coeff = _coeffs[ct_bkl+1-i]
			sum_ = ifAdd(sum_, ifMul(block, coeff))

	return sum_


def encrypt_check(_ct, _ct_l, _key1, _key2, _nonce, _ad):
	ct_bkl = _ct_l // BLOCKLEN

	aes1 = AES.new(_key1, AES.MODE_ECB)
	aes2 = AES.new(_key2, AES.MODE_ECB)

	bks1 = [aes1.encrypt(l2b((b2l(_nonce) << 32) + 2 + i, 16)) for i in range(ct_bkl)]
	bks2 = [aes2.encrypt(l2b((b2l(_nonce) << 32) + 2 + i, 16)) for i in range(ct_bkl)]

	full_ct = [0]*_ct_l
	ks1 = [0]*_ct_l
	ks2 = [0]*_ct_l
	for i in range(_ct_l):
		ks1[i] = bks1[i//16][i % 16]
		ks2[i] = bks2[i//16][i % 16]
		full_ct[i] = _ct[i//16][i % 16]

	plaintxt1 = xor(bytes(full_ct), bytes(ks1))
	plaintxt2 = xor(bytes(full_ct), bytes(ks2))

	encrypted1,tag1 = gcm_encrypt(_key1, _nonce, plaintxt1,_ad)
	encrypted2,tag2 = gcm_encrypt(_key2, _nonce, plaintxt2,_ad)

	assert encrypted1 == encrypted2 and tag1 == tag2
	return encrypted1, tag1


def collide(_key1, _key2, _nonce, _plain, _ad, DEBUG=False, _blockidx=-1):
	ct_l = len(_plain)
	ct_bkl = ct_l // BLOCKLEN
	ct_bl = 8 * ct_l

	ad_bl = 8*len(_ad)

	print("blocks:", ct_bkl)
	print()
	aes1 = AES.new(_key1, AES.MODE_ECB)
	aes2 = AES.new(_key2, AES.MODE_ECB)

	authkey1 = aes1.encrypt(all_zeros)
	authkey2 = aes2.encrypt(all_zeros)

	coeffs = getCoeffs(authkey1, authkey2, ad_bl//128 + ct_bkl+1)

	pad1 = aes1.encrypt(l2b((b2l(_nonce) << 32) | 1, 16))
	pad2 = aes2.encrypt(l2b((b2l(_nonce) << 32) | 1, 16))
	pads = ifAdd(pad1, pad2)

	keystream1 = [aes1.encrypt(l2b((b2l(_nonce) << 32) + 2 + i, 16)) for i in range(ct_bkl)]

	ct = [ifAdd(_plain[16*i:16*(i+1)], keystream1[i]) for i in range(ct_bkl)]
	assert len(ct) == ct_bkl

	coef = binascii.hexlify(coeffs[ct_bkl+1-_blockidx])
	sum_ = getSum(_ad, coeffs, pads, ct, _blockidx)

	ct[_blockidx] = ifMul(l2b(getInverse(coef), 16), sum_)

	encrypted, tag = encrypt_check(ct, ct_l, _key1, _key2, _nonce, _ad)

	return encrypted,tag


def getKS(key, nonce, bCount, initCount=2): # initCount = 2 for GCM, 0 for CTR
	aesECB = AES.new(key, AES.MODE_ECB)
	stream = b"".join([aesECB.encrypt(long_to_bytes((nonce << 32) + initCount + i, 16)) for i in range(bCount+1)])
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


if __name__=='__main__':
	parser = argparse.ArgumentParser(description="Turn a non-overlapping polyglot into a dual AES-GCM ciphertext.")
	parser.add_argument('polyglot',
		help="input polyglot - requires special naming like 'P(10-5c).png.rar'.")
	parser.add_argument('output',
		help="generated file.")
	parser.add_argument('-k', '--keys', nargs=2, default=[b"Now?", b"L4t3r!!!"],
		help="encryption keys - default: Now? / L4t3r!!!.")
	parser.add_argument('-a', '--additional-data', default=b"MyVoiceIsMyPass!",
		help="Additional data - default: MyVoiceIsMyPass!.")
	parser.add_argument('-n', '--nonce', default="0",
		help="nonce - default: 0.")
	parser.add_argument('-i', '--block-index', default=-1,
		help="Specify block index - default: -1.")

	args = parser.parse_args()

	fnmix = args.polyglot
	fnpoc = args.output
	key1, key2 = b"\x01" * 16, b"\x02" * 16
	key1, key2 = args.keys
	ad = args.additional_data
	blockidx = args.block_index
	nonce = args.nonce

	key1 = pad16(unhextry(key1))
	key2 = pad16(unhextry(key2))
	assert not key1 == key2

	if nonce.startswith("0x"):
		noncei = int(nonce, 16)
	else:
		noncei = int(nonce)
	nonceb = l2b(noncei,12)
	ad = unhextry(ad)
	ad = pad(ad, BLOCKLEN)

	# fnmix should come from Mitra and
	# has a naming convention like "P(14-89)-ID3v2[Zip].4d01e2fb.mp3.zip"
	swaps = [int(i, 16) for i in fnmix[fnmix.find("(") + 1:fnmix.find(")")].split("-")]
	exts = fnmix[-9:].split(".")[-2:]
	

	with open(fnmix, "rb") as file:
		dIn = file.read()

	def BruteNonce(fn):
		hdr1 = fn[fn.find("{")+1:]
		hdr1 = hdr1[:hdr1.find("}")]
		hdr1 = binascii.unhexlify(hdr1)

		hdr2 = dIn[:len(hdr1)]
		hdr_xor = xor(hdr1,hdr2)
		t = (hdr_xor, key1, key2)
		if t in NONCES:
			nonce = NONCES[t]
			print("Nonce already computed.")
			return nonce
		hdr_xor_l = len(hdr_xor)
		aes1 = AES.new(key1, AES.MODE_ECB)
		aes2 = AES.new(key2, AES.MODE_ECB)

		i = 0
		for i in range(2**64):
			block1 = aes1.encrypt(long_to_bytes((i << 32) + 2, 16))
			block2 = aes2.encrypt(long_to_bytes((i << 32) + 2, 16))

			if xor(block1[:hdr_xor_l], block2[:hdr_xor_l]) == hdr_xor:
				return i
		return None


	if fnmix.startswith("O") and \
		"{" in fnmix and \
		"}" in fnmix:
		print("Overlap file found")
		noncei = BruteNonce(fnmix)
		nonce = "%i" % noncei
		nonceb = l2b(noncei,12)

		print("Nonce: %x" % noncei)

	dIn = pad(dIn, BLOCKLEN) # the padding will break with formats not supporting appended data

	assert len(dIn) % 16 == 0
	bCount = len(dIn) // 16

	ks1 = getKS(key1, noncei, bCount)
	ks2 = getKS(key2, noncei, bCount)

	dCrypt = xor(dIn, ks1[:len(dIn)])
	dCrypt = xor(dCrypt, ks2[:len(dCrypt)])

	dOut = mix(dIn, dCrypt, swaps)


	blockidx = int(blockidx)
	if blockidx == -1:
		dIn += b"\0" * BLOCKLEN

	if blockidx < 0:
		blockidx += len(dIn) // 16 - 1

	block_target = dIn[16*blockidx:16*(blockidx+1)]
	if block_target != b"\0" * 16:
		print("Error: target block is not null")
		print("%i: %s" % (blockidx, block_target))
		sys.exit()

	print("key 1:", b2a(key1.strip(b"\0")))
	print("key 2:", b2a(key2.strip(b"\0")))
	print("ad   :", b2a(ad.strip(b"\0")))

	ctxt, tag = collide(key1, key2, nonceb, dOut, ad, _blockidx=blockidx,DEBUG=DEBUG)

	output = "\n".join([
			"key1: %s" % b2a(binascii.hexlify(key1)),
			"key2: %s" % b2a(binascii.hexlify(key2)),
			"adata: %s" % b2a(binascii.hexlify(ad)),
			"nonce: %s" % b2a(binascii.hexlify(nonceb)),
			"ciphertext: %s" % b2a(binascii.hexlify(ctxt)),
			"tag: %s" % b2a(binascii.hexlify(tag)),
		  "exts: %s" % " ".join(exts),
		  "origin: %s" % fnmix,
		])
	with open(fnpoc, "wb") as fpoc:
		fpoc.write(output.encode())
		fpoc.close()

	assert not key1 == key2
	plaintxt1 = gcm_decrypt(key1, nonceb, ctxt, tag, ad)
	plaintxt2 = gcm_decrypt(key2, nonceb, ctxt, tag, ad)
	assert not plaintxt1 == plaintxt2

	success = False
	try:
		invalidkey = b'\x07'*16
		plaintxt1 = gcm_decrypt(invalidkey, nonce, ctxt, tag, ad)
	except Exception:
		success = True
	if not success:
		print("Decryption with other key failed didn't fail as expected")

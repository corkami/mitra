#!/usr/bin/env python

# a JPG image crypto-polyglot generator for GCM

# Ange Albertini 2020

# Useage: jpg.py in/ange.jpg in/marc.jpg


import sys
import binascii
import struct
import re

def comment_start(size):
	return b"\xff\xfe" + struct.pack(">H", size)

def comment(size, s=""):
	return comment_start(size) + s + b"\0" * (size - 2 - len(s))


def comments(s, delta=0):
	return comment(len(s) + delta, s)


def xor(a1, a2):
	assert len(a1) == len(a2)
	return bytes([(a1[i] ^ a2[i]) for i in range(len(a1))])

fn1, fn2 = sys.argv[1:3]
with open(fn1, "rb") as f:
	d1 = f.read()
with open(fn2, "rb") as f:
	d2 = f.read()

#TODO: make fully generic (this comes from the xor of the keystreams)
XOR = binascii.unhexlify("000000002088138d2c8d79103c9befec")

block1 = binascii.unhexlify("FFD8FFFE0000FFFE2080")
block1 += b"\0" * (0x208C - 4 - len(block1))

block2 = block1
block2 = xor(block2[:len(XOR)], XOR) + block2[16:]

# skip the signature, split by scans (usually the biggest segments)
c1 = d1[2:].split(b"\xff\xda")

if max(len(i) for i in c1) >= 65536 - 8:
	print("ERROR: The first image file has a segment that is too big!")
	print("Maybe save it as progressive or reduce its size/scans.")
	sys.exit()


suffix = b"".join([
	b"\xff\xfe",
		struct.pack(">H", 0+len(c1[0]) - 2 + 8),
	c1[0], # the first image chunk

	# creating a tiny intra-block comment to host a trampoline comment segment
	b"".join([
			b"".join([
				# a comment over another comment declaration
				comments(
					b"\xff\xfe" +
					# +4 to reach the next intra-block
					struct.pack(">H", len(c) + 4 + 4),
					delta=2),
				b"\xff\xda",
				c
			]) for c in c1[1:]
		]),

		b"ANGE", # because we land 4 bytes too far

	d2[2:]
])

regexpCMT = rb"\xff\xfe.."
comments = re.findall(regexpCMT, block1+suffix)

data = block1+suffix
l = [0] 
for m in re.compile(regexpCMT).finditer(data):
	pattern = m.group()
	pattern_o = m.start()
	l += [pattern_o + 4]
	#print "%08i: %s" % (pattern_o, binascii.hexlify(pattern))

l += [data.find(b"ANGE\xFF") + 4]

zipperfn = "Z(%s).jpg.jpg" % ("-".join("%x" % i for i in l))
print("Generated file:\n%s" % zipperfn)

with open(zipperfn, "wb") as zipper:
	zipper.write(b"".join([
		block1,
		suffix
	]))

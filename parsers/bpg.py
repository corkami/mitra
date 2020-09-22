#!/usr/bin/env python

# Better Portable Graphics

from parsers import FType


def ue7_enc(n):
	if n == 0:
		return [0]
	l = []
	while (n > 0):
		l += [(n & 0x7f)]
		n = n >> 7
	for i in range(len(l) - 1):
		l[i + 1] = l[i + 1] | 0x80

	return l[::-1]


def ue7_encs(n):
	r = bytes(ue7_enc(n))
	return r


assert ue7_encs(127) == b"\x7f"
assert ue7_encs(128) == b"\x81\0"
assert ue7_encs(129) == b"\x81\1"

def ue7_dec(s):
	n = 0
	for i, c in enumerate(s):
		n = (n << 7) | (c & 0x7f)
		if c <= 0x80:
			break
	return n, i + 1


assert ue7_dec(b"\x7f")   == (127,1)
assert ue7_dec(b"\x81\0") == (128,2)
assert ue7_dec(b"\x81\1") == (129,2)


def getBPGinfo(data):
	off = 5
	b = data[off]
	ext_b = (b >> (7-4))  & 0b1

	off += 1

	width, delta = ue7_dec(data[off:])
	off += delta
	height, delta = ue7_dec(data[off:])
	off += delta
	image_l, delta = ue7_dec(data[off:])
	off += delta

	header = list(data[:off])

# TODO: probably buggy if extensions are already present
	if ext_b == 1:
			ext_l, delta = ue7_dec(data[off:])
			off += delta

			toff = 0
			while (toff < ext_):
					ext_tag, delta = ue7_dec(data[off + toff:])
					toff += delta
					ext_tag_l, delta = ue7_dec(data[off + toff:])
					toff += delta
					toff += ext_tag_l

			off += ext_l

	return header, data[off:]


###############################################################################


class BPGparser(FType):
	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data
		self.type = "BPG"
		self.bAppData = False # rejected by bpgview
		self.bParasite = True
		self.parasite_o = 0xC
		self.parasite_s = 0xffffff # ?

		self.cut = 0xE # TODO: actually variable


	def identify(self):
		return self.data.startswith(b"BPG\xFB")


	def parasitize(self, fparasite):
		host = self.data
		parasite = fparasite.data

		header, image = getBPGinfo(self.data) 

		# set extension flag to 1
		header[5] = header[5] | 8

		result = bytes(header)

		tag_len = len(parasite)
		tag_len_s = ue7_encs(tag_len)

		tag_s = ue7_encs(1) # just need a non-5 value
		ext_l = len(tag_len_s) + len(tag_s) + tag_len
		ext_l_s = ue7_encs(ext_l)

		result += ext_l_s
		result += tag_s
		result += tag_len_s
		parasite_o = len(result)
		result += parasite

		result += image

		return result, [parasite_o, parasite_o + len(parasite)]

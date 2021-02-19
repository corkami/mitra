#!/usr/bin/env python3

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


###############################################################################


class parser(FType):
	DESC = "BPG / Better Portable Graphics"
	TYPE = "BPG"
	MAGIC = b"BPG\xFB"
	FLAGS_o = 5


	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data
		self.bAppData = False # rejected by bpgview
		self.bParasite = True
		self.parasite_o = 0x10
		self.parasite_s = 0xffffff # ?

		self.cut = 9 # TODO: actually variable
		self.prewrap = 3


	def wrap(self, data): # _s means string representation
		tag_len = len(data)
		tag_len_s = ue7_encs(tag_len)

		tag_s = ue7_encs(1) # just need a non-5 (= animation_control) value
		ext_l = len(tag_len_s) + len(tag_s) + tag_len
		ext_l_s = ue7_encs(ext_l)

		prewrap = ext_l_s
		prewrap += tag_s
		prewrap += tag_len_s
		wrapped = prewrap + data
		return wrapped


	def fixformat(self, d, delta):
		flags = d[self.FLAGS_o]
		flags |= 8
		d = d[:self.FLAGS_o] + bytes([flags]) + d[self.FLAGS_o + 1:] # set extension flag
		return d


	def getCut(self):
		data = self.data
		off = self.FLAGS_o
		b = data[off]
		ext_b = (b >> (7-4))  & 0b1

		off += 1

		width, delta = ue7_dec(data[off:])
		off += delta
		height, delta = ue7_dec(data[off:])
		off += delta
		image_l, delta = ue7_dec(data[off:])
		off += delta

		# TODO: probably buggy if extensions are already present
		if ext_b == 1:
				ext_l, delta = ue7_dec(data[off:])
				off += delta

				toff = 0
				while (toff < ext_l):
						ext_tag, delta = ue7_dec(data[off + toff:])
						toff += delta
						ext_tag_l, delta = ue7_dec(data[off + toff:])
						toff += delta
						toff += ext_tag_l

				off += ext_l
		self.cut = off
		self.parasite_o = self.cut - self.prewrap
		return self.cut


	def getPrewrap(self, parasite_s):
		parasite__ = b"\0" * parasite_s
		wrapped = self.wrap(parasite__)
		delta = len(wrapped) - parasite_s
		assert delta >= self.prewrap

		self.prewrap = delta
		return delta

#!/usr/bin/env python3

# strategy: 
# - normalize "ebml" length size
# - insert parasite
# - adjust ebml length
# - that's all - unlike MP4, offsets are relative to segment starts

from parsers import FType


def minVarIntSize(_int):
	for i in range(8):
		if 0 <= _int < (1 << (7 * (i+1))):
			return i+1

assert minVarIntSize(0) == 1
assert minVarIntSize(0x7f) == 1
assert minVarIntSize(0x80) == 2
assert minVarIntSize(0x81) == 2


def IntToVarInt(i, nb=None):
	"""Int to VarInt"""
	if nb is None:
		nb = minVarIntSize(i)
	assert 0 <= i < (1 << (7 * nb))
	b = i.to_bytes(nb, byteorder='big')
	res = (b[0] ^ (1 << (8 - nb))).to_bytes(1, byteorder = "big") + b[1:]
	return res

assert IntToVarInt(0, 1) == b'\x80'
assert IntToVarInt(0x19, 1) == b'\x99'
assert IntToVarInt(0, 2) == b'\x40\0'
assert IntToVarInt(0x1134, 2) == b'\x51\x34'
assert IntToVarInt(0, 8) == b'\1\0\0\0\0\0\0\0'
assert IntToVarInt(0, 4) == b'\x10\0\0\0'
assert IntToVarInt(0xff, 4) == b'\x10\0\0\xff'


def VarIntToInt(d):
	"""arbitrary vInt bytes to value and its char length"""
	b = d[:8]
	len_hdr = bin(b[0])[2:].rjust(8,"0")
	l = len_hdr.find("1") + 1
	varint = b[:l]
	i_s = bytes([varint[0] ^ (1 << (8 - l))]) + varint[1:l]
	i = int.from_bytes(i_s, "big")
	return i, l

assert VarIntToInt(b"\x80") == (0, 1)
assert VarIntToInt(b"\x81") == (1, 1)
assert VarIntToInt(b"\xFF") == (0x7F, 1)
assert VarIntToInt(b"\x80\xFF") == (0, 1) # trailing garbage
assert VarIntToInt(b"\xFF\xFF") == (0x7F, 1)
assert VarIntToInt(b"\x40\x00") == (0, 2)
assert VarIntToInt(b"\x7F\xFF") == (0x3FFF, 2)
assert VarIntToInt(b"\x20\x00\x00") == (0, 3)
assert VarIntToInt(b"\x10\x00\x00\x00") == (0, 4)
assert VarIntToInt(b"\x01\x00\x00\x00\x00\x00\x00\x00") == (0, 8)


def minmizeVarInt(b):
	"""returns smallest VarInt for given VarInt as bytes"""
	i, _ = VarIntToInt(b)
	return IntToVarInt(i, minVarIntSize(i))

assert minmizeVarInt(b"\x80") == b"\x80"
assert minmizeVarInt(b"\xFF") == b"\xFF"
assert minmizeVarInt(b"\x40\x02") == b"\x82"
assert minmizeVarInt(b"\x20\x10\x02") == b"\x50\x02"



class parser(FType):
	DESC = "EBML / Extensible Binary Meta Language [container]"
	TYPE = "EBML"
	MAGIC = b"\x1A\x45\xDF\xA3"


	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data
		self.ebml_s = 4 # used size of VarInt
		self.ebml_o = len("\x1A\x45\xDF\xA3")
		self.void_s = len("\xEC")

		self.bParasite = True

		self.cut = self.ebml_o + self.ebml_s
		self.prewrap = self.void_s + self.ebml_s # VoidId:1, VarInt:self.ebml_s
		self.postwrap = 0
		self.parasite_o = self.cut + self.prewrap
		self.parasite_s = (1 << (7*self.ebml_s)) - 1


	def normalize(self):
		"Set EBML size to a specific VarInt size"
		d = self.data
		
		i, size_l = VarIntToInt(d[self.ebml_o:])
		parasite_o = self.ebml_o + size_l
		self.data = self.data[:self.ebml_o] + IntToVarInt(i, self.ebml_s) + self.data[parasite_o:]


	def wrap(self, data):
		VOID = b"\xEC"
		return VOID + IntToVarInt(len(data), self.ebml_s) + data


	def fixformat(self, d, delta):
		i, s = VarIntToInt(d[self.ebml_o:])
		assert s == self.ebml_s
		i += delta
		d = d[:self.ebml_o] + IntToVarInt(i, s) + d[self.ebml_o + s:]
		return d

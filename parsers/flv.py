#!/usr/bin/env python

# Flash Video

from parsers import FType
import struct


# Strategy:
# - put parasite right after header
# - increase data pointer

class FLVparser(FType):
	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data
		self.type = "FLV"
		self.bParasite = True
		self.parasite_o = 9
		self.parasite_s = 0xFFFFFFFF - 1

		self.cut = 9


	def identify(self):
		return self.data.startswith(b"FLV\1")


	def fixformat(self, d, delta):
		pointer_o = 5
		offset = struct.unpack(">I", d[pointer_o:pointer_o+4])[0]
		offset += delta

		return b"".join([
			d[:pointer_o],
			struct.pack(">I", offset),
			d[pointer_o + 4:]
			])

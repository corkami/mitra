#!/usr/bin/env python

from parsers import FType
import struct

class BMPparser(FType):
	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data
		self.type = "BMP"

		self.bParasite = True
		# BM SSSS ???? OOOO
		self.parasite_o = 0x40 # depends on each BMP
		self.parasite_s = 0xFFFFFFFF - 1

		self.cut = 0x40


	def identify(self):
		return self.data.startswith(b"BM")


	def getCut(self):
		self.cut = struct.unpack("<I", self.data[0xa:0xa + 4])[0]
		return self.cut

# move further the data start pointer
# put the parasite at the data start offset

	def fixformat(self, d, delta):
		size_o = 2
		size_s = 4
		size = struct.unpack("<I", d[size_o:size_o+size_s])[0] + delta

		offset_o = 0xA
		offset_s = 4
		offset = struct.unpack("<I", d[offset_o:offset_o+offset_s])[0] + delta

		d = b"".join([
			d[:size_o],
			struct.pack("<I", size),
			d[size_o + size_s:offset_o],
			struct.pack("<I", offset),
			d[offset_o + offset_s:],
			])
		return d

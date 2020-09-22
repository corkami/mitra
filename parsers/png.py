#!/usr/bin/env python

from parsers import FType

import struct
import binascii


class PNGparser(FType):
	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data
		self.type = "PNG"

		self.bParasite = True
		self.parasite_o = 0x10
		self.parasite_s = 0xFFFFFFFF

		self.cut = 8   # Just after the magic, before IHDR.
		self.prewrap = 2*4 # Length:4, Type:4
		self.postwrap = 4  # CRC:4


	def identify(self):
		return self.data.startswith(b"\x89PNG\r\n\x1a\n")


	def wrap(self, data, type_=b"cOMM"):
		return b"".join([
			struct.pack(">I", len(data)),
			type_,
			data,
			struct.pack(">I", binascii.crc32(type_ + data) % 0x100000000)])

#!/usr/bin/env python3

from parsers import FType

import binascii
from helpers import int4b


class parser(FType):
	DESC = "PNG / Portable Network Graphics"
	TYPE = "PNG"
	MAGIC = b"\x89PNG\r\n\x1a\n"

	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data

		self.bParasite = True
		self.parasite_o = 0x10
		self.parasite_s = 0xFFFFFFFF

		self.cut = 8   # Just after the magic, before IHDR.
		self.prewrap = 2*4 # Length:4, Type:4
		self.postwrap = 4  # CRC:4


	def wrap(self, data, type_=b"cOMM"):
		return b"".join([
			int4b(len(data)),
			type_,
			data,
			int4b(binascii.crc32(type_ + data) % 0x100000000)
		])

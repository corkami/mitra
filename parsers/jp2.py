#!/usr/bin/env python

# JP2: 'MP4'-based but:
#  - no relocation needed
#  - required early Atom before parasite

from parsers import FType
import struct


class JP2parser(FType):
	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data
		self.type = "JP2"
		self.bParasite = True
		self.parasite_o = 0x28 # After the JP2 header
		self.parasite_s = 0xFFFFFFFF # also exists in 64b flavor

		self.cut = 0x20
		self.prewrap = 2*4


	def identify(self):
		return self.data.startswith(b"\0\0\0\x0cjP  ")


	def wrap(self, data):
		return struct.pack(">I", len(data) + 8) + b"free" + data

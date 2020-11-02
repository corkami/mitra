#!/usr/bin/env python3

# JP2: 'MP4'-based but:
#  - no relocation needed
#  - required early Atom before parasite

from parsers import FType
from helpers import *


class parser(FType):
	DESC = "JP2 / JPEG 2000"
	TYPE = "JP2"
	MAGIC = b"\0\0\0\x0cjP  "

	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data
		self.bParasite = True
		self.parasite_o = 0x28 # After the JP2 header
		self.parasite_s = 0xFFFFFFFF # also exists in 64b flavor

		self.cut = 0x20
		self.prewrap = 2*4


	def identify(self):
		return self.data.startswith(self.MAGIC)


	def wrap(self, data):
		return int4b(len(data) + 8) + b"free" + data

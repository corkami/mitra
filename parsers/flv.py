#!/usr/bin/env python3

from parsers import FType
from helpers import *


# Strategy:
# - put parasite right after header
# - increase data pointer

class parser(FType):
	DESC = "FLV / Flash Video"
	TYPE = "FLV"
	MAGIC = b"FLV\1"

	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data
		self.bParasite = True
		self.parasite_o = 9
		self.parasite_s = 0xFFFFFFFF - 1

		self.cut = 9


	def fixformat(self, d, delta):
		pointer_o = 5
		d = inc4b(d, pointer_o, delta)
		return d
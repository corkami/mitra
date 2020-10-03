#!/usr/bin/env python

from parsers import FType
from helpers import *

# Parasite strategy:
# - add an extra RGB section for an unneeded palette (format 2)
#   (requires an extra palette afterwards)


class parser(FType):
	DESC = "ILDA / International Laser Display Association vector images"
	TYPE = "ILDA"
	MAGIC = b"ILDA"

	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data

		self.bParasite = True
		self.parasite_o = 32         # size of section header
		self.parasite_s = 0xFFFF*3  # max nb of RGB records

		self.cut = 0
		self.prewrap = 32


	def fixparasite(self, parasite):
		# rgb padding
		if len(parasite) % 3 > 0:
			parasite += (3-(len(parasite) % 3)) * b"\0"
		return parasite


	def wrap(self, data):
		RecNb = int2b(len(data) // 3)
		wrapped = b"".join([
			b"ILDA",   # magic
			b"\0\0\0", # reserved
			b"\2",     # format code <= RGB 
			b"\0"*8,   # name
			b"\0"*8,   # company name
			RecNb,     # Number of records * RGB
			b"\0"*2,   # frame or number
			b"\0"*2,   # 0
			b"\0"*1,   # projector number
			b"\0"*1,   # reserved
			data
		])
		return wrapped

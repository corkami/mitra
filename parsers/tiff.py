#!/usr/bin/env python3

from parsers import FType
from helpers import *


# Strategy:
# 1. move parasite right after File Header
# 2. adjust IFD pointers
# 3. adjust StripOffsets values


BYTE =			1
ASCII =			2
SHORT =			3
LONG = 			4
RATIONAL = 	5


Lengths = {
	BYTE			:1,
	ASCII			:1,
	SHORT			:2,
	LONG			:4,
	RATIONAL	:8,
}

class parser(FType):
	DESC = "TIFF / Tagged Image File Format"
	TYPE = "TIFF"
	MAGICb = b"MM\0\x2a"
	MAGICl = b"II\x2a\0"

	# pointer to the first IFD
	ifdptr_o = 4
	ifdptr_s = 4

	# where the first image data can start
	data_o = 8


	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data

		self.bParasite = True
		self.parasite_o = self.data_o
		self.parasite_s = 0xFFFFFFFF

		self.cut = self.parasite_o
		self.prewrap = 0


	def identify(self):
		d = self.data

		if d.startswith(self.MAGICb):
			self.endianness = BIG
		elif d.startswith(self.MAGICl):
			self.endianness = LITTLE
		else:
			return False

		return True


	def fixparasite(self, parasite):
		# word alignment
		if len(parasite) % 2 == 1:
			parasite += b"\0"
		return parasite


	def fixformat(self, d, delta):
		o = self.ifdptr_o
		while o != 0:
			d = inc4(d, o, delta, self.endianness)
			o = get4(d, o, self.endianness)

			c = get2(d, o, self.endianness) # entries count
			o += 2

			for i in range(c):
				tag = get2(d, o, self.endianness)
				o += 2
				type_ = get2(d, o, self.endianness)
				o += 2
				count = get4(d, o, self.endianness)
				o += 4
				valoff = get4(d, o, self.endianness)

				if tag == 273: # StripOffsets
					# print(tag, type_, count, valoff)
					if type_ == LONG and count == 1:
						d = inc4(d, o, delta, self.endianness)
					else: 
						raise Exception("TIFF", "TODO: handle more cases")

				o += 4

			o = get4(d, o, self.endianness)

		return d

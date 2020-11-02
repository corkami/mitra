#!/usr/bin/env python3

# iNES rom format

from parsers import FType

# 512 byte trainer space if byte Flag6 has 3rd byte set

# Parasite strategy:
# - Set trainer space and use it.
#   Hopefully it doesn't crash anything ? :D


class parser(FType):
	DESC = "iNES rom"
	TYPE = "NES"
	MAGIC = b"NES\x1a"
	TRAINER_o = 16
	TRAINER_s = 512

	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data

		self.bParasite = True
		self.parasite_o = self.TRAINER_o
		self.parasite_s = self.TRAINER_s

		self.cut = self.TRAINER_o
		self.prewrap = self.parasite_o - self.cut

#		self.precav_o = 0x16
#		self.precav_s = 512


	def normalize(self):
		# need to set trainer flag bit
		d = bytearray(self.data)
		flag6 = d[6]
		flag6 |= 1 << 2
		d[6] = flag6
		self.data = d


	def fixparasite(self, parasite):
		# need to pad parasite to 512
		parasite += bytes([0]) * (512-len(parasite))
		return parasite

#!/usr/bin/env python

# iNES rom format

from parsers import FType

# 512 byte trainer space if byte Flag6 has 3rd byte set

# Parasite strategy:
# - Set trainer space and use it.
#   Hopefully it doesn't crash anything ? :D


class NESparser(FType):
	trainer_o = 16
	trainer_s = 512

	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data
		self.type = "NES"

		self.bParasite = True
		self.parasite_o = self.trainer_o
		self.parasite_s = self.trainer_s

		self.cut = self.trainer_o
		self.prewrap = self.parasite_o - self.cut


	def identify(self):
		return self.data.startswith(b"NES\x1a")


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

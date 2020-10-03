#!/usr/bin/env python

from parsers import FType
from helpers import *


class parser(FType):
	DESC = "RIFF / Resource Interchange File Format [container]"
	TYPE = "RIFF"
	MAGICl = b"RIFF"
	MAGICb = b"RIFX"
	WEBPTYPE = b"WEBP"

	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data

		self.bParasite = True
		self.parasite_o = 12
		self.parasite_s = 0xFFFFFFFF

		self.cut = 12
		self.prewrap = 2*4


	def identify(self):
		d = self.data

		# WebP doesn't follow the full RIFF structure
		if d[8:8+4] == self.WEBPTYPE:
			return False

		if d.startswith(self.MAGICb):
			self.endianness = BIG
		elif d.startswith(self.MAGICl):
			self.endianness = LITTLE
		else:
			return False

		return True


	def wrap(self, data, type_=b"JUNK"):
		return b"".join([
			type_,
			int4(len(data), self.endianness),
			data
		])


	def fixparasite(self, parasite):
		# word alignment
		if len(parasite) % 2 == 1:
			parasite += b"\0"
		return parasite


	def fixformat(self, d, delta):
		d = d[:4] + int4(len(d) - 8, self.endianness) + d[8:]
		return d

#!/usr/bin/env python

from parsers import FType
from helpers import *


class parser(FType):
	DESC = "BMP / Windows Bitmap"
	TYPE = "BMP"
	MAGIC = b"BM"

	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data

		self.bParasite = True
		self.cut = 0x40
		self.parasite_o = 0x40
		self.parasite_s = 0xFFFFFFFF - 1


	def getCut(self):
		self.cut = get4l(self.data, 0xA)
		return self.cut


	def fixformat(self, d, delta):
		# `BM` SSSS ???? OOOO
		size_o = 2
		d = inc4l(d, size_o, delta)

		offset_o = 0xA
		d = inc4l(d, offset_o, delta)

		return d

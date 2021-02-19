#!/usr/bin/env python3

from parsers import FType
from helpers import *


class parser(FType):
	DESC = "BMP / Windows Bitmap"
	TYPE = "BMP"
	MAGIC = b"BM"

	# whole file size (not necessarily correct nor validated)
	SIZE_o = 2
	# pointer to bitmap data - after the whole header.
	OFFSET_o = 0xA


	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data

		self.bParasite = True
		self.parasite_o = 14 + 12 # minimum in OS/2 1.x - BitmapFileHeader + BitmapCoreHeader 
		self.parasite_s = 0xFFFFFFFF - 1
		self.cut = self.parasite_o 


	def getCut(self):
		self.cut = get4l(self.data, self.OFFSET_o)
		self.parasite_o = self.cut + self.prewrap
		return self.cut


	def fixformat(self, d, delta):
		d = inc4l(d, self.SIZE_o, delta)
		d = inc4l(d, self.OFFSET_o, delta)

		return d

#!/usr/bin/env python

from parsers import FType
from helpers import *


class JPGparser(FType):
	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data
		self.type = "JPG"

		self.bParasite = True

		self.parasite_o = 6
		self.parasite_s = 0xFFFF - 2

		self.cut = 2
		self.prewrap = 1+1+2


	def identify(self):
		return self.data.startswith(b"\xFF\xD8")


	def wrap(self, parasite, marker=b"\xFE"):
		return b"".join([
			b"\xFF",
			marker,
			int2b(len(parasite)+2),
			parasite,
			])

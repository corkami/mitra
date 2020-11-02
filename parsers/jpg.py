#!/usr/bin/env python3

from parsers import FType
from helpers import *


class parser(FType):
	DESC = "JFIF / JPEG File Interchange Format"
	TYPE = "JPG"
	MAGIC = b"\xFF\xD8"

	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data

		self.bParasite = True

		self.parasite_o = 6
		self.parasite_s = 0xFFFF - 2

		self.cut = 2
		self.prewrap = 1+1+2


	def wrap(self, parasite, marker=b"\xFE"):
		return b"".join([
			b"\xFF",
			marker,
			int2b(len(parasite)+2),
			parasite,
			])

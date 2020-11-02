#!/usr/bin/env python3

# PDF but only has a cavity format

from parsers import FType
import os


class parser(FType):
	DESC = "Portable Document Format"
	TYPE = "PDF"
	MAGIC = b"%PDF-1"
	MAGIC_o = 1018

	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data

		self.start_o = 0
		# the whole `%PDF-1.3` signature has to be present in the first 1kb 
		self.precav_s = 1018

		self.bAppData = True
		self.bParasite = False


	def identify(self):
		return self.data[self.MAGIC_o:self.MAGIC_o + 20].startswith(self.MAGIC)

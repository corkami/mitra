#!/usr/bin/env python

# https://github.com/dsnet/compress/blob/master/doc/bzip2-format.pdf

from parsers import FType


class BZ2parser(FType):
	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data
		self.type = "Bzip2"

		self.start_o = 0 # yes, it's required 
		self.bParasite = False # not sure yet


	def identify(self):
		return self.data.startswith(b"BZh")

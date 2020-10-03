#!/usr/bin/env python

# https://github.com/dsnet/compress/blob/master/doc/bzip2-format.pdf

from parsers import FType


class parser(FType):
	DESC = "BZ2 / bzip2"
	TYPE = "BZ2"
	MAGIC = b"BZh"

	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data

		self.bParasite = False # not sure yet

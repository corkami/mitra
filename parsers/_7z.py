#!/usr/bin/env python

from parsers import FType

class parser(FType):
	DESC = "7-Zip"
	TYPE = "7Z"
	MAGIC = b"7z\xbc\xaf\x27\x1C"

	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data
		self.start_o = 4*1024*1024 # not sure of actual threshold
		self.bParasite = False # not yet

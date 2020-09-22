#!/usr/bin/env python

from parsers import FType

class _7Zparser(FType):
	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data
		self.type = "7Zip"
		self.start_o = 4*1024*1024 # not sure of actual threshold
		self.bParasite = False # not yet


	def identify(self):
		return self.data.startswith(b"7z")

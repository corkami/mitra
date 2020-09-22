#!/usr/bin/env python

from parsers import FType

class JSparser(FType):
	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data
		self.type = "JavaScript"
		self.start_o = 4*1024*1024
		self.parasite_o = None
		self.parasite_s = None

		self.terminator = b"<!--"

	def identify(self):
		return self.data.startswith(b"-->")

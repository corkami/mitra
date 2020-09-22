#!/usr/bin/env python

from parsers import FType

class dummyParser(FType):
	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data
		self.type = "dummy"
		self.start_o = 4*1024*1024


	def identify(self):
		return True

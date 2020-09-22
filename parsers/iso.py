#!/usr/bin/env python

from parsers import FType

class ISOparser(FType):
	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data
		self.type = "ISO"

		self.bParasite = False # no parasiting yet. Would be trivial.

		self.precav_s = 0x8000


	def identify(self):
		return self.data[0x8000:].startswith(b"\1CD001\1")

#!/usr/bin/env python

from parsers import FType

class parser(FType):
	DESC = "ISO 9660 image [dump]"
	TYPE = "ISO"

	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data

		self.bParasite = False # no parasiting yet. Would be trivial.

		self.precav_s = 0x8000


	def identify(self):
		return self.data[0x8000:].startswith(b"\1CD001\1")

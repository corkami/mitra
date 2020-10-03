#!/usr/bin/env python

from parsers import FType

from helpers import *

# Parasitizing:
# the header contains X structures, each containing an offset to the data
# -> insert parasite after the structures, and update each offset


class parser(FType):
	DESC = "ICO"
	TYPE = "ICO"

	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data

		self.bParasite = True
		self.parasite_o = 0x70 # rought estimate - dependant
		self.parasite_s = 0xFFFFFFFF


	def identify(self):
		if not self.data.startswith(b"\0\0\1\0"): # what a shitty lack of magic
			return False

		self.count = get2l(self.data, 4)
		return True


	def getCut(self):
		self.cut = 6 + self.count * 0x10
		return self.cut


	def fixformat(self, d, delta):
		offset = 6 + 0x0c
		for i in range(self.count):
			d = inc4l(d, offset, delta)

			offset += 0x10
		return d

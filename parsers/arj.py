#!/usr/bin/env python

from parsers import FType


class ARJparser(FType):
	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data
		self.type = "Arj"

		self.bParasite = False

		self.start_o = 128*1024 # with WinRar


	def identify(self):
		return self.data.startswith(bytes([0x60, 0xEA]))

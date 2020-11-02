#!/usr/bin/env python3

from parsers import FType


class parser(FType):
	DESC = "Arj / Archived by Robert Jung"
	TYPE = "Arj"
	MAGIC = bytes([0x60, 0xEA])

	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data

		self.bParasite = False

		self.start_o = 128*1024 # with WinRar

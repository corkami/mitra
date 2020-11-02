#!/usr/bin/env python3

from parsers import FType
import binascii


class parser(FType):
	DESC = "Shell Link"
	TYPE = "LNK"
	MAGIC = binascii.unhexlify("4C000000" + "0114020000000000C000000000000046")

	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data

		self.bParasite = False

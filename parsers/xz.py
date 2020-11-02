#!/usr/bin/env python3

# "Gzip with LZMA"
# https://tukaani.org/xz/

# No possible polyglot yet

from parsers import FType

class parser(FType):
	DESC = "XZ"
	TYPE = "XZ"
	MAGIC = b"\xFD7zXZ\0"

	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data
		self.bAppData = False # Required matching footer
		self.bParasite = False # No known strategy


	def identify(self):
		return self.data.startswith(self.MAGIC)

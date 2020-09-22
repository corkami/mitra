#!/usr/bin/env python

# XZ "Gzip with LZMA"
# https://tukaani.org/xz/

# No possible polyglot yet

from parsers import FType

class XZparser(FType):
	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data
		self.type = "XZ"
		self.bAppData = False # Required matching footer
		self.bParasite = False # No known strategy


	def identify(self):
		return self.data.startswith(b"\xFD7zXZ\0")

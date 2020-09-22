#!/usr/bin/env python

from parsers import FType

class RARparser(FType):
	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data
		self.type = "RAR"
		self.bParasite = False # Actual rar is required
		self.start_o = 4*1024*1024 # for v4 or v5, 0 for v1.4


	def identify(self):
		return self.data.startswith(b"Rar!\x1A\7\0") or \
			self.data.startswith(b"Rar!\x1A\7\1\0")
		# or self.data.startswith(b"RE~^\7\0")

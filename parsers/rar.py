#!/usr/bin/env python

from parsers import FType

class parser(FType):
	DESC = "RAR / Roshal Archive"
	TYPE = "RAR"
	MAGIC14 = b"RE~^\7\0"
	MAGIC4 = b"Rar!\x1A\7\0"
	MAGIC5 = b"Rar!\x1A\7\1\0"

	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data
		self.bParasite = False # Actual rar is required
		self.start_o = 4*1024*1024 # for v4 or v5, 0 for v1.4


	def identify(self):
		return self.data.startswith(self.MAGIC4) or \
			self.data.startswith(self.MAGIC5)
		# or self.data.startswith(self.MAGIC14)

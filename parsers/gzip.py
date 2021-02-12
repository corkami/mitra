#!/usr/bin/env python3

# GZIP

# Unsupported: if an extra field is already present.

from parsers import FType
from helpers import *


class parser(FType):
	DESC = "gzip"
	TYPE = "GZ"
	MAGIC = b"\x1f\x8b"


	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data
		self.start_o = 0 # yes, it's required

		self.bParasite = True
		self.hack = False # as a subfield or directly in the extra field

		self.cut = 10
		self.prewrap = 2
		if not self.hack:
			self.prewrap = 6
		else:
			self.prewrap = 2

		self.parasite_o = self.cut + self.prewrap
		self.parasite_s = 0xFFFF


	def fixformat(self, d, delta):
		# set the extra field flag
		flags = d[3]
		flags += 1 << 2

		return d[:3] + bytes([flags]) + d[4:]


	def wrap(self, data):
		# the extra field is made of TLV subfields
		if not self.hack:
			extra = b"".join([
				b"Id",             # Type
				int2l(len(data)),  # Length
				data,              # Value
			])
		else:
			extra = data

		return b"".join([
			int2l(len(extra)),
			extra,
		])

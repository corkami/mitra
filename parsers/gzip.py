#!/usr/bin/env python

# GZIP

from parsers import FType
import struct


class GZIPparser(FType):
	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data
		self.type = "Gzip"
		self.start_o = 0 # yes, it's required 

		self.bParasite = True
		self.parasite_o = 12 # as extra field 
		self.parasite_s = 0xFFFF

		self.cut = 10
		self.prewrap = 2


	def identify(self):
		return self.data.startswith(b"\x1f\x8b")


	def wrap(self, data):
		return b"".join([
			struct.pack("<H", len(data)),
			data,
		])


	def fixformat(self, d, delta):
		flags = d[3]
		flags += 1 << 2

		return d[:3] + bytes([flags]) + d[4:]

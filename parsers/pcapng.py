#!/usr/bin/env python

# Packet Capture Next Generation

from parsers import FType
import struct

class PCAPNGparser(FType):
	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data
		self.type = "PCAPNG"
		self.bAppData = False # end wrapping possible but with postwrapping

		self.bParasite = True
		self.parasite_o = 0x28
		self.parasite_s = 0xFFFFFFFF

		self.cut = 0x1c
		self.prewrap = 3*4
		self.postwrap = 4


	def identify(self):
		return self.data.startswith(b"\x0a\x0d\x0d\x0a")


	def fixparasite(self, parasite):
		# dword padding
		if len(parasite) % 4 > 0:
			parasite += (4-(len(parasite) % 4)) * b"\0"
		return parasite


	def wrap(self, parasite):
		l = struct.pack("<I", len(parasite) + 4*4)

		wrapped = b"".join([
			b"\xAD\x0B\0\x40", # non-copied custom block
			l,
			b"Ange",           # Private Enterprise Number
			parasite,
			l,
			])

		return wrapped

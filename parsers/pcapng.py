#!/usr/bin/env python3

from parsers import FType
from helpers import int4l

class parser(FType):
	DESC = "PCAPNG / Packet Capture Next Generation"
	TYPE = "PCAPNG"
	MAGIC = b"\x0a\x0d\x0d\x0a"

	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data
		self.bAppData = False # end wrapping possible but with postwrapping

		self.bParasite = True
		self.parasite_o = 0x28
		self.parasite_s = 0xFFFFFFFF

		self.cut = 0x1c
		self.prewrap = 3*4
		self.postwrap = 4


	def fixparasite(self, parasite):
		# dword padding
		if len(parasite) % 4 > 0:
			parasite += (4-(len(parasite) % 4)) * b"\0"
		return parasite


	def wrap(self, parasite):
		l = int4l(len(parasite) + 4*4)

		wrapped = b"".join([
			b"\xAD\x0B\0\x40", # non-copied custom block
			l,
			b"Ange",           # Private Enterprise Number
			parasite,
			l,
			])

		return wrapped

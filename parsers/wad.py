#!/usr/bin/env python3

from parsers import FType
from helpers import *


class parser(FType):
	DESC = "WAD / Doom's Where's All the Data ?"
	TYPE = "WAD"
	MAGICi = b"IWAD"
	MAGICp = b"PWAD"

	sig_o = 0
	sig_s = 4

	numlumps_o = 4
	infotableofs_o = 8


	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data

		self.bParasite = True
		self.parasite_o = 12
		self.parasite_s = 0xFFFFFFF

		self.cut = 12
		self.prewrap = 0
		self.postwrap = 0


	def identify(self):
		d = self.data
		start = getd(d, self.sig_o, self.sig_s)
		if start != self.MAGICi and start != self.MAGICp:
			return False

		self.numlumps = get4l(d, self.numlumps_o)
		self.lumps_o = get4l(d, self.infotableofs_o)

		return True


	def fixformat(self, d, delta):
		"Increase the pointers if the size is not null (non-virtual)."
		d = inc4l(d, self.infotableofs_o, delta)
		ptr = self.lumps_o + delta
		for i in range(self.numlumps):
			size = get4l(d, ptr + 4)
			if size != 0:
				d = inc4l(d, ptr, delta)
			ptr += 0x10

		return d

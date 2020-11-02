#!/usr/bin/env python3

from parsers import FType

class parser(FType):
	DESC = "SVG / Scalable Vector Graphics"
	TYPE = "SVG"
	MAGIC = b"<svg "

	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data

		# disabled because some tools are unhappy with binary in XML comments
		self.bParasite = False
		self.bAppData = False 

		self.parasite_o = 0x80 # rough average...
		self.parasite_s = 0xFFFFFFFF


	def parasitize(self, fparasite):
		host = self.data
		parasite = fparasite.data
		cut = data.find(b"><") + 1

		parasite_c = b"".join([
			b"<!--",
			parasite,
			b"-->"
			])

		return host[:cut] + parasite_c + host[cut:], [] # TODO:swaps

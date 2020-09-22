#!/usr/bin/env python

# Scalable Vector Graphics (xml-based)

from parsers import FType

class SVGparser(FType):
	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data
		self.type = "SVG"

		# disabled because some tools are unhappy with binary in XML comments
		self.bParasite = False
		self.bAppData = False 

		self.parasite_o = 0x80 # rough average...
		self.parasite_s = 0xFFFFFFFF


	def identify(self):
		return self.data.startswith(b"<svg ")


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

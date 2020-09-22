#!/usr/bin/env python

import io
import zipfile
import os
from parsers import FType

class ZipParser(FType):
	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data
		self.type = "Zip"

		self.bParasite = True
		self.parasite_o = 0x1E
		self.parasite_s = 0xffffff # ?

		self.start_o = 4*1024*1024 # no actual downward limit

# Doesn't apply the usual way
#		self.cut = 0
#		self.prewrap = 0x25


	def identify(self):
		return self.data.startswith(b"PK\3\4") # totally incomplete


	def parasitize(self, fparasite):
		# TODO: with no recompression

		# strategy: just store the parasite as first invisible file with no compression
		zipinfo = zipfile.ZipInfo(
			filename='', # it works - sometimes hidden by software
			date_time=(1981, 2, 3, 4, 5, 6) # invariant for easier testing
		) 

		hHost = io.BytesIO(self.data)
		hFinal = io.BytesIO()

		with zipfile.ZipFile(hFinal, 'w', zipfile.ZIP_STORED) as final:
			final.writestr(zipinfo, fparasite.data)

			with zipfile.ZipFile(hHost, "r") as zf:
				for n in zf.namelist():
						contents = zf.open(n).read()
						final.writestr(zf.getinfo(n), contents, compress_type=zipfile.ZIP_DEFLATED)

		return hFinal.getvalue(), [] # TODO:swaps

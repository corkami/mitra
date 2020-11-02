#!/usr/bin/env python3

from parsers import FType


def readFlags(ll, f):
	flags = {}
	for l in ll:
		flags[l[0]] = f & (2**(l[1]+1)-1)
		f >>= l[1]
	return flags


class parser(FType):
	DESC = "GIF / Graphics Interchange Format"
	TYPE = "GIF"

	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data

		self.bParasite = True
		self.parasite_o = 16     # Extension, right after the header (extreme case if there's no global palette)
		self.parasite_s = 255   # max size of a subblock

		self.cut = 13     # variable if global palette is present
		self.prewrap = 3
		self.postwrap = 1 # terminator of the comment


	def identify(self):
		# in theory, only GIF 89 support comments
		# but in practice, it's irrelevant
		return self.data.startswith(b"GIF87a") or \
			self.data.startswith(b"GIF89a")


	def wrap(self, parasite):
		return b"!" + b"\xfe" + bytes([len(parasite)]) + parasite + b"\0" # terminator


	def getCut(self):
		host = self.data

		# is there a Global Color Table?
		flags = readFlags([
			["GlobalColorTable",1],
			["ColorResolution", 3],
			["Sort", 1],
			["GCTSize", 3],
		][::-1],
			host[0xA]
		)

		gct_s = 3*(2<<(flags["GCTSize"])) if flags["GlobalColorTable"] == 1 else 0
		cut = 6 + 7 + gct_s

		self.cut = cut

		return self.cut

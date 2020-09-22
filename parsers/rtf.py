#!/usr/bin/env python

# Rich Text Format

# http://www.biblioscape.com/rtf15_spec.htm

# https://www.decalage.info/rtf_tricks
# https://www.fireeye.com/blog/threat-research/2016/05/how_rtf_malware_evad.html

# Strategy:
# - declare a picture, with its data in binary format via \binN #BDATA (not supported by all viewers)
# - omit most picture metadata (\*blip, \picw1, \pich1)
# - move picture declaration early for more possible abuse


from parsers import FType


class RTFparser(FType):
	template = rb"{\pict\bin%06i "


	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data
		self.type = "RTF"

		self.bParasite = True
		self.parasite_o = 0x17
		self.parasite_s = 999999

		self.cut = 6
		self.prewrap = len(self.template % 0) # self.parasite_o - self.cut


	def identify(self):
		return self.data.startswith(b"{\\rtf1") # can be shorter in practice


	def wrap(self, parasite):
		return b"".join([
			self.template % len(parasite),
			parasite,
			b"}"
			])

#!/usr/bin/env python3

# Adobe Photoshop

from parsers import FType
from helpers import *


class parser(FType):
	DESC = "PSD / Photoshop"
	TYPE = "PSD"
	MAGIC = b"8BPS"
	COLOR_MODE_DATA_o = 0x1a # Size:4 Data:Size
	IMAGE_RESOURCE_BLOCK_s = 12


	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data

		self.bParasite = True
		self.cut = self.COLOR_MODE_DATA_o + 8
		self.parasite_o = self.cut
		self.parasite_s = 0xFFFFFFFF
		self.prewrap = self.IMAGE_RESOURCE_BLOCK_s


	def getCut(self):
		# we add an Image Resource Block,
		# the Image Resources section, right after the Color Mode Data
		self.cmd_s = get4b(self.data, self.COLOR_MODE_DATA_o)
		self.resource_o = self.COLOR_MODE_DATA_o + 4 + self.cmd_s

		# The section starts with its size, then Image Resource Blocks
		self.cut = self.resource_o + 4
		self.parasite_o = self.cut + self.prewrap
		return self.cut


	def identify(self):
		if not self.data.startswith(self.MAGIC):
			return False

		self.getCut()
		return True


	def fixparasite(self, parasite):
		# word alignment
		if len(parasite) % 2 == 1:
			parasite += b"\0"
		return parasite


	def wrap(self, parasite):
		ImageResourceBlock = b"".join([
			b"8BIM",       # Signature
			b"\0\0",       # UID
			b"\0\0",       # Name (padded empty string here)
			int4b(len(parasite)),
			parasite
		])

		return ImageResourceBlock


	def fixformat(self, d, delta):
		# Update the Image Resource section size
		d = inc4b(d, self.resource_o, delta)
		return d

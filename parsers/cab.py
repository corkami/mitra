#!/usr/bin/env python

# CFHEADER contains:
# - cbCabinet, the cabinet size
# - cFolders, the folders count.
# First CFFILE pointed by CFHEADER.coffFiles
# CFFOLDER points via coffCabStart to CFData

# -> parasitize = , update pointers in CFHeader, in CFolder, size in CFHeader


from parsers import FType
from helpers import *


class parser(FType):
	DESC = "CAB / Microsoft Cabinet"
	TYPE = "CAB"
	MAGIC = b"MSCF"

	# in header:
	cbCabinet_o = 0x8   # Cabinet size
	coffFiles_o = 0x10  # offsets to first file block
	cFolders_o = 0x1a   # count of folders
	CFHEADER_s = 0x24

	# in folders:
	coffCabStart_o = 0  # offset to first data block
	CFFOLDER_s = 0x8	  # (Reserve flag not supported)


	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data

		self.start_o = 0        # WinRar supports other offsets, not Microsoft Expand

		self.bAppData = True

		self.bParasite = True
		self.parasite_s = 0xffffff

		self.cut = self.CFHEADER_s

		self.prewrap = 0
		self.parasite_o = self.cut # no prewrap


	def identify(self):
		if not self.data.startswith(self.MAGIC):
			return False

		self.cFolders = get2l(self.data, self.cFolders_o)
		return True


	def getCut(self):
		# Folder structures follow the header
		self.cut += 0x8 * self.cFolders
		# cut after all Folders
		return self.cut


	def fixformat(self, d, delta):
		d = inc4l(d, self.cbCabinet_o, delta)
		d = inc4l(d, self.coffFiles_o, delta)

		o = self.CFHEADER_s
		for i in range(self.cFolders):
 			d = inc4l(d, o + self.coffCabStart_o, delta)
 			o += self.CFFOLDER_s

		return d

#!/usr/bin/env python

from parsers import FType
import struct

class PEparser(FType):
	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data
		self.type = "PE(hdr)"
		self.bAppData = True # let's not have duplicates
		self.bParasite = True
		# alignment, but actually first physical offset of a section for big headers
		self.cut = 2
		self.prewrap = 0
		self.parasite_o = 0x50
		self.parasite_s = 0x100

		self.cut = 2


	def identify(self):
		return self.data.startswith(b"MZ") # :D


	def fixparasite(self, parasite):
		# padding
		ALIG = 4
		if len(parasite) % ALIG > 0:
			parasite += (ALIG-(len(parasite) % ALIG)) * b"\0"
		return parasite


	def parasitize(self, fparasite):
		# strategy: add parasite between DOS and PE headers

		# TODO: turn this into fixformat

		host = self.data
		parasite = self.fixparasite(fparasite.data)
		delta = len(parasite)

		DOSHdr_s = 0x40
		# move the PE header at the right offset
		PEhdr_o = DOSHdr_s + delta

		PEHeadersMax = 0x200 # could be adjusted for bigger headers - 0x400 for cuphead
		PEoffset = host.find(b"PE\0\0")
		peHDR = host[PEoffset:PEHeadersMax].rstrip(b"\0") # roughly accurate :p
		if PEhdr_o + len(peHDR) > PEHeadersMax:
			return None, []

		# update SizeOfHeaders
		SoH_o = 0x54 # local header in the PE header
		SoH_s = 4
		SizeOfHeader = struct.unpack("<I", peHDR[SoH_o:SoH_o+SoH_s])[0] + delta
		peHDR = peHDR[:SoH_o] + struct.pack("<I", SizeOfHeader) + peHDR[SoH_o + SoH_s:]

		# combine new PE header with rest of the PE
		merged = b"".join([
			b"MZ",                       # Magic
			b"\0" * (DOSHdr_s-2-4),      # DOS header slack space
			struct.pack("<I", PEhdr_o), # pointer to new PE header offset
			parasite,
			peHDR,
			b"\0" * (PEHeadersMax - PEhdr_o - len(peHDR)),
			host[PEHeadersMax:],
			])
		return merged, [DOSHdr_s, PEhdr_o]

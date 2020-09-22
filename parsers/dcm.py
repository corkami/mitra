#!/usr/bin/env python

from parsers import FType
import struct


class DICOMparser(FType):
	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data
		self.type = "DICOM"

		self.precav_s = 128 # slack space but magic always at offset 80
		self.cut = 0x84

		self.bAppData = True # wrappended

		self.bParasite = True
		self.parasite_o = 0x160 # dependant on the host file
		self.parasite_s = 0xFFFFFFFF

		self.prewrap = 12


	def identify(self):
		return self.data[0x80:].startswith(b"DICM")


	def wrap(self, parasite):
		return b"".join([
			b"\x09\0",     # PRIVATE GROUP
			b"\0\0",       # EMPTY TAG
			b"OB",         # Other Byte (long)
			b"\0\0",       # reserved
			struct.pack("<I", len(parasite)),
			parasite
		])


	def wrappend(self, data):
		return self.wrap(data)


	def getCut(self):
		host = self.data
		# we can put our private tag just after the metadata part

		# the first TAG should be FILE META INFORMATION GROUP LENGTH
		# which defines the length of the critical stuff.
		
		# Some viewer even ignore that convention
		#  and tolerate PRIVATE tags right after the magic, at 0x84
		HACK = False
		
		if not HACK:
			cut = 0x84
			if host[cut:cut + 8] != b"\x02\x00\x00\x00\x55\x4C\x04\x00":
					return None

			cut += 8
			metadata_l = struct.unpack("<I", host[cut:cut + 4])[0]
			cut += 4
			cut += metadata_l
			self.cut = cut

		return self.cut


	# filler (hardcoded magic) strategy
	def zipper(self, fhost): # DCM is not the host
		Ddata = self.data
		Dcut = self.getCut()

		Hdata = fhost.data
		Hcut = fhost.getCut()

		# TODO: made generic / at higher level?
		if Hcut is None:
			return None, []
		
		if fhost.bAppData == False:
			return None, []

		if Hcut+fhost.prewrap > 0x80: # DCMstart
			return None, []

		parasite1 = fhost.postwrap * b"\0" + Hdata[Hcut:]

		Ddata = Ddata[:Dcut] + self.wrap(parasite1) + Ddata[Dcut:]

		parasite2 = Ddata[Hcut + fhost.prewrap:Dcut + self.prewrap]

		if len(parasite2) > fhost.parasite_s:
			return None, []

		wrapped = fhost.wrap(parasite2)
		delta = len(wrapped)

		dMerged = b"".join([
			Hdata[:Hcut],
			wrapped,
			Ddata[Dcut + self.prewrap + fhost.postwrap:],
			])

		dMerged = fhost.fixformat(dMerged, delta)
		swaps = [
			0x80,
			self.cut + self.prewrap,
			self.cut + self.prewrap + len(parasite1) + self.postwrap
		]
		return dMerged, swaps

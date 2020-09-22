#!/usr/bin/env python

from parsers import FType
import struct


def getPEhdr(d):
	PEoffset = d.find("PE\0\0")
	peHDR = d[PEoffset:]

	Machine = struct.unpack("H", peHDR[4:4+2])[0]

	SecCount = struct.unpack("h", peHDR[0x6:0x6+2])[0]
	bits = None
	if Machine == 0x014C:
		bits = 32
	elif Machine == 0x8664:
		bits = 64
	if bits is None:
		print("ERROR: unknown arch")
		sys.exit()

	NumDiffOff = 0x74 if bits == 32 else 0x84
	NumDD = struct.unpack("i", peHDR[NumDiffOff:NumDiffOff+4])[0]

	SecTblOff = NumDiffOff + 4 + NumDD * 2 * 4

	# get the offset of the first section
	SectsStart = struct.unpack("i", peHDR[SecTblOff+0x14:SecTblOff+0x14+4])[0]

	PElen = SecTblOff + SecCount * 0x28

	return PEoffset, PElen, SecCount, PEoffset + SecTblOff, SectsStart


def relocateSections(d, SecTblOff, SecCount, delta):
	for i in range(SecCount):
		offset = SecTblOff + i*0x28 + 0x14
		PhysOffset = struct.unpack("i", d[offset:offset+4])[0]

		d = b"".join([
			d[:offset],
			struct.pack("i", PhysOffset + delta),
			d[offset+4:]
			])
	return d


class PEparser(FType):
	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data
		self.type = "PE(sec)"
		self.bParasite = True
		# alignment, but actually first physical offset of a section for big headers
		self.parasite_o = 0x200
		self.parasite_s = 0xFFFFFFFF


	def identify(self):
		return self.data.startswith(b"MZ") # :D


	def parasitize(self, fparasite):
		# strategy: add parasite between header and the first section

		align = self.parasite_o
		parasite = fparasite.data
		host = self.data

		PEoff, HdrLen, NumSec, SecTblOff, SectsStart = getPEhdr(host)

		Sec1PS = SecTblOff + 0x14
		SectionsOffset = struct.unpack("i", host[Sec1PS:Sec1PS+4])[0]

		# padd parasite
		parasite += "\0" * (align - (len(parasite) % align))
		delta = len(parasite)

		# add parasite at the start of first section
		host = host[:SectionsOffset] + parasite + host[SectionsOffset:]
		
		# adjust all sections offsets
		host = relocateSections(host, SecTblOff, NumSec, delta)
		return host, [] # TODO:swaps

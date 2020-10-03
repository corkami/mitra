#!/usr/bin/env python

from parsers import FType
from helpers import *


def getPEhdr(d):
	PEoffset = d.find(b"PE\0\0")
	peHDR = d[PEoffset:]

	Machine = get2l(peHDR, 4)
	SecCount = get2l(peHDR, 6)

	bits = None
	if Machine == 0x014C:
		bits = 32
	elif Machine == 0x8664:
		bits = 64
	if bits is None:
		print("ERROR: unknown arch")
		sys.exit()

	NumDiffOff = 0x74 if bits == 32 else 0x84
	NumDD = get4l(peHDR, NumDiffOff)

	SecTblOff = NumDiffOff + 4 + NumDD * 2 * 4

	# get the offset of the first section
	SectsStart = get4l(peHDR, SecTblOff+0x14)

	PElen = SecTblOff + SecCount * 0x28

	return PEoffset, PElen, SecCount, PEoffset + SecTblOff, SectsStart


def relocateSections(d, SecTblOff, SecCount, delta):
	for i in range(SecCount):
		offset = SecTblOff + i*0x28 + 0x14
		d = inc4l(d, offset, delta)
	return d


class parser(FType):
	DESC = "Portable Executable (hdr)"
	TYPE = "PE(sec)"
	MAGIC = b"MZ"

	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data
		self.bParasite = True
		# alignment, but actually first physical offset of a section for big headers
		self.parasite_o = 0x200
		self.parasite_s = 0xFFFFFFFF
		self.cut = 0x200


	def parasitize(self, fparasite):
		# strategy: add parasite between header and the first section

		align = self.parasite_o
		parasite = fparasite.data
		host = self.data

		PEoff, HdrLen, NumSec, SecTblOff, SectsStart = getPEhdr(host)

		Sec1PS = SecTblOff + 0x14
		SectionsOffset = get4l(host, Sec1PS)

		# padd parasite
		parasite += b"\0" * (align - (len(parasite) % align))
		delta = len(parasite)

		# add parasite at the start of first section
		host = host[:SectionsOffset] + parasite + host[SectionsOffset:]
		
		# adjust all sections offsets
		host = relocateSections(host, SecTblOff, NumSec, delta)
		return host, [] # TODO:swaps

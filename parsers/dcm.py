#!/usr/bin/env python3

from parsers import FType
from helpers import *


class parser(FType):
	DESC = "DICOM / Digital Imaging and Communications in Medicine"
	TYPE = "DCM"
	MAGIC = b"DICM"

	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data

		self.precav_s = 128 # slack space but magic always at offset 80
		self.cut = 0x84

		self.bAppData = True # wrappended

		self.bParasite = True
		self.parasite_o = 0x160 # dependent on the host file
		self.parasite_s = 0xFFFFFFFF

		self.prewrap = 12

		self.bZipper = True


	def identify(self):
		return self.data[0x80:].startswith(self.MAGIC)


	def wrap(self, parasite):
		return b"".join([
			b"\x09\0",     # PRIVATE GROUP
			b"\0\0",       # EMPTY TAG
			b"OB",         # Other Byte (long)
			b"\0\0",       # reserved
			int4l(len(parasite)),
			parasite
		])


	def getCut(self):
		host = self.data
		# we can put our private tag just after the metadata part

		# the first TAG should be FILE META INFORMATION GROUP LENGTH
		# which defines the length of the critical stuff.
		
		# Some viewer even ignore that convention
		#  and tolerate PRIVATE tags right after the magic, at 0x84
		HACK = True
		
		if not HACK:
			cut = self.cut
			if host[cut:cut + 8] != b"\x02\x00\x00\x00\x55\x4C\x04\x00":
					return None

			cut += 8
			metadata_l = get4l(host, cut)
			cut += 4
			cut += metadata_l
			self.cut = cut

		return self.cut


#          [Dicom]
#
#  Zero     NonZ           Zero        NonZ                      Zipper
# +-----+  +-----+        +-----+                                +-----+
# |\\\\\|  |     |  ZHead |\\\\\|                                |\\\\\| ZHead
# |\\\\\|  +-----+  ZCut> +-----+ - - +-----+       \      Zcut> +-----+
# |\\\\\|  |/////|        :     :     |/////| DHead |            |/////| DHead
# +-----+  +-----+        +-----+ - - +-----+ <DCut |      DCut> +-----+
#          |/////|  ZBody |\\\\\|     :     :       |            |\\\\\| ZBody
#          |/////|        |\\\\\|     :     :       |            |\\\\\|
#          |/////|        +-=-=-+ - - +-----+       | Tdata      +-=-=-+
#          |/////|                    |/////|       |            |/////|
#          +-----+                    |/////| DBody |            |/////| DBody
#                                     |/////|       |            |/////|
#                                     |/////|       |            |/////|
#                                     +-----+       /            +-----+

	def zipper(self, zero):
		# FIXME: follow verbosity level
		ndata = self.data    # dicom is the non-zero format
		ncut = self.getCut()

		zero.normalize()
		zdata = zero.data
		zcut = zero.getCut()

		# TOCHECK: Why - obsolete ? check bParasite ?
		if zcut is None:
			print("> %s doesn't support cut (!?)" % zero.TYPE)
			return None, []
		
		if zero.bAppData == False:
			print("> %s doesn't support appended data." % zero.TYPE)
			return None, []

		if zcut + zero.prewrap > self.precav_s:
			print("> %s Header too big to fit in Dicom cavity." % zero.TYPE)
			return None, []

		# TODO: wrappending support
		parZ = zero.postwrap * b"\0" + zdata[zcut:]

		# TODO: replace with a self.parasitize call ?
		tdata = ndata[:ncut] + self.wrap(parZ) + ndata[ncut:]

		# TODO: support variable prewrap ?
		nhead = tdata[zcut + zero.prewrap:ncut + self.prewrap]

		if len(nhead) > zero.parasite_s:
			print("> DICOM body too big to fit in %s parasite." % zero.TYPE)
			return None, []

		nheadwrap = zero.wrap(nhead)
		delta = len(nheadwrap)

		zipdata = b"".join([
			zdata[:zcut],
			nheadwrap,
			tdata[ncut + self.prewrap + zero.postwrap:],
			])

		zipdata = zero.fixformat(zipdata, delta)
		swaps = [
			self.precav_s,
			self.cut + self.prewrap,
			self.cut + self.prewrap + len(parZ) + self.postwrap
		]
		print("Zipper Success!")
		return zipdata, swaps

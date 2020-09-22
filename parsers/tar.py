#!/usr/bin/env python

from parsers import FType
import tarfile
import io

class TARparser(FType):
	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data
		self.type = "TAR"
		self.bAppData = True # YMMV - some corruption messages.

		# the filename can be sacrificed to store info
		# but the file still starts at zero
		self.start_o = 0

		self.bParasite = True # add a dummy file early in the archive
		self.parasite_o = 512
		self.parasite_s = 0xffffff # ?


	def identify(self):
		return self.data[0x100:0x100 + 6] == b"\0ustar" # other magic are possible. This is unrealistically strict.


	def parasitize(self, fparasite):
		Hparasite = io.BytesIO(fparasite.data)

		tarinfo = tarfile.TarInfo(name=".") # null file makes the file truncated
		tarinfo.mode = 0 # invariant
		tarinfo.size = len(Hparasite.getvalue())

		Hfile = io.BytesIO()
		with tarfile.open(fileobj=Hfile, mode="w") as f:
			f.addfile(tarinfo=tarinfo, fileobj=Hparasite)
		
		# we need to remove the extra closing blocks added by TarFile, not sure why fixed at 2400
		return Hfile.getvalue()[:-0x2400] + self.data, [] # TODO:swaps


	def fixchecksum(self, d):
		CHECKSUM_o = 0x94
		HEADER_s = 512

		# grab the header
		hdr = list(d[:HEADER_s])

		# wipe the checksum field with spaces
		for i in range(8):
			hdr[i + CHECKSUM_o] = ord(b" ")

		# add all chars of the header to an unsigned int
		c = 0
		for i in hdr:
			c += i

		print(oct(c)[2:])
		# store the unsigned int in octal, followed by space then NULL
		for i, j in enumerate(oct(c)[2:]):
			hdr[i + CHECKSUM_o] = ord(j)
		hdr[CHECKSUM_o + 6] = ord(b"\0")

		return bytes(hdr) + d[HEADER_s:]


	def emptyHdr(self):
		l = 512 * [0]
		off = 0x64

		l[0] = ord(b".") # File Name

		for count, length in [[3,7], [2,11]]:
			for _ in range(count):
				for i in range(length):
					l[off] = ord("0")
					off += 1
				off += 1

		for i, c in enumerate(b"\0ustar  "):
			l[0x100 + i] = c

		hdr = bytes(l)
		return hdr


# TODO: move as a separate parser ?

# Reverse parasite (not a zipper)
#
#          *          TAR                */TAR        
#       +-----+     + - - +             +-----+     
# Head1 |\\\\\|     ://///:       Head1 |\\|//| Fake0
#       +-----+ - - +-----+             +-----+
#       :     :     |/////|             |/////|
#       :     :     |/////| TAR         |/////| TAR
#       :     :     |/////|             |/////|
#       +-----+ - - +-----+             +-----+
# Body1 |\\\\\|                   Body1 |\\\\\|
#       |\\\\\|                         |\\\\\|
#       +-----+                         +-----+

	def zipper(self, fhost): # TAR is not the host
		Tdata = self.data

		Hcut = fhost.getCut()
		if Hcut is None: # TODO: double check
			return None, []
		Hprewrap = fhost.prewrap

		TarCut = Hcut + Hprewrap
		if TarCut > 0x63:
			return None, []

# - prepend fake header to TAR.
		TData = self.emptyHdr() + Tdata

# - cut out the length necessary for 
		self.data = TData[TarCut:]

		# TODO:swaps
		dMerged, swaps = fhost.parasitize(self)
		if dMerged is None:
			return None, []

		return self.fixchecksum(dMerged), [] # TODO:swaps

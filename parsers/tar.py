#!/usr/bin/env python

from parsers import FType
import tarfile
import io

class parser(FType):
	DESC = "TAR / Tape Archive"
	TYPE = "TAR"
	MAGIC = b"\0ustar"
	MAGIC_o = 0x100

	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data
		self.bAppData = True # YMMV - some corruption messages.

		# the filename can be sacrificed to store info
		# but the file still starts at zero
		self.start_o = 0

		self.bParasite = True # add a dummy file early in the archive
		self.cut = 512
		self.parasite_o = 512
		self.parasite_s = 0xffffff # ?

		self.bZipper = True


	def identify(self):
		# other magic are possible. This is unrealistically strict.
		return self.data[self.MAGIC_o:self.MAGIC_o + 6] == self.MAGIC

	def parasitize_(self, fparasite):
		Hparasite = io.BytesIO(fparasite.data)

		tarinfo = tarfile.TarInfo(name=".") # null file makes the file truncated
		tarinfo.mode = 0 # invariant
		tarinfo.size = len(Hparasite.getvalue())

		Hfile = io.BytesIO()
		with tarfile.open(fileobj=Hfile, mode="w") as f:
			f.addfile(tarinfo=tarinfo, fileobj=Hparasite)
		
		# we need to remove the extra closing blocks added by TarFile, not sure why fixed at 2400
		return Hfile.getvalue()[:-0x2400] + self.data, [] # TODO:swaps


	def normalize(self):
		self.data = self.emptyHdr() + self.data


	def fixchecksum(self, d):
		CHECKSUM_o = 0x94
		CHECKSUM_s = 8
		HEADER_s = 512

		# grab the header
		hdr = list(d[:HEADER_s])

		# wipe the checksum field with spaces
		for i in range(CHECKSUM_s):
			hdr[i + CHECKSUM_o] = ord(b" ")

		# add all chars of the header to an unsigned int
		c = 0
		for i in hdr:
			c += i

		# store the unsigned int in octal, followed by space then NULL
		for i, j in enumerate(oct(c)[2:]):
			hdr[i + CHECKSUM_o] = ord(j)
		hdr[CHECKSUM_o + 6] = ord(b"\0")

		return bytes(hdr) + d[HEADER_s:]
 

	def fixformat(self, d, delta):
		# we just update the new size in the header.
		# the size is already rounded up to 512.
		SIZE_o = 0x7c
		SIZE_s = 11
		osize = oct(delta)[2:].rjust(SIZE_s, "0")
		d = d[:SIZE_o] + osize.encode() + d[SIZE_o + SIZE_s:]
		self.data = self.fixchecksum(d)
		return self.data


	def fixparasite(self, parasite):
		# word alignment
		if len(parasite) % 512 != 0:
			parasite += b"\0" * (512 - len(parasite) % 512)
		return parasite


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


# Reverse parasite (not a zipper)
# Works for PNG, not for others
#
# Strategy:
# 1. add an empty file header
# 2. overwrite the file name with a header
#
#        Zero         TAR               Zipper
#       +-----+     + - - +             +-----+
# ZHdr  |\\\\\|     ://///:       ZHdr  |\\|//| Fake0
#       +-----+ - - +-----+             +-----+
#       :     :     |/////|             |/////|
#       :     :     |/////| TAR         |/////| TAR
#       :     :     |/////|             |/////|
#       +-----+ - - +-----+             +-----+
# ZBody |\\\\\|                   ZBody |\\\\\|
#       |\\\\\|                         |\\\\\|
#       +-----+                         +-----+


	def zipper(self, zero): # TAR is not the host
		tdata = self.data

		zcut = zero.getCut()
		if zcut is None: # TODO: double check
			return None, []

		tcut = zcut + zero.prewrap
		if tcut > 0x63:
			# FIXME: follow verbosity level
			print("> RevParasite: Header too big to fit in Tar header.")
			return None, []

# - prepend fake header to TAR.
		tdata = self.emptyHdr() + tdata

# - cut out the length necessary for 
		self.data = tdata[tcut:]

		zipper, swaps = zero.parasitize(self)
		if zipper is None:
			return None, []

		zipper = self.fixchecksum(zipper)
		# FIXME: swaps are actually reversed because it's a reverse parasite
		return zipper, swaps

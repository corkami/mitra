#!/usr/bin/env python

from parsers import FType
from helpers import *


class parser(FType):
	DESC = "ICC / International Color Consortium profiles"
	TYPE = "ICC"
	MAGIC = b"acsp"

	size_o = 0
	size_s = 4

	sig_o = 0x24
	sig_s = 4

	tagcount_o = 0x80
	tagcount_s = 4

	table_o = tagcount_o + tagcount_s

	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data

		self.bParasite = True
		self.parasite_o = self.tagcount_o + self.tagcount_s
		self.parasite_s = 0xFFFFFFFF

		self.cut = self.parasite_o
		self.prewrap = 0


	def identify(self):
		if self.data[self.sig_o:self.sig_o+self.sig_s] != self.MAGIC:
			return False

		d = self.data

		self.size = get4b(d, self.size_o)
		self.tagcount = get4b(d, self.tagcount_o)

		return True


	def getCut(self):
		self.cut = self.parasite_o + 3*4*(self.tagcount+1)
		return self.cut


	def fixformat(self, d, delta):
		fdelta = delta + 3*4 # we need a new tag table entry

		# adjust tag table
		ptr = self.tagcount_o + self.tagcount_s + 4*1
		for i in range(self.tagcount):
			d = inc4b(d, ptr, fdelta)
			ptr += 3*4

		self.tagcount += 1
		self.size += fdelta

		d = b"".join([
			struct.pack(">I", self.size),     # file size
			d[self.size_s+self.size_o:  			# other header contents
				self.tagcount_o],
			struct.pack(">I", self.tagcount), # tag counter
																	      # new tag entry
				b"junk", 						            # tag signature
				struct.pack(">I",								# tag offset
					 self.table_o + 3*4*self.tagcount),
				struct.pack(">I", delta),       # tag size
				d[self.table_o:]                # rest of the file
			])

		return d

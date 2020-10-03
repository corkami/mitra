#!/usr/bin/env python

# (binary form) CPIO

# slightly buggy but the idea is there :D


from parsers import FType
from helpers import *


class parser(FType):
	DESC = "CPIO"
	TYPE = "CPIO"
	MAGIC = b"\xc7\x71" # 070707o
	HDR_s = 0x1A

	trailer = b"TRAILER!!!"

	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data

		self.bParasite = True
		self.parasite_s = 0xffffffff # ?

		self.bAppData = True

		self.start_o = 0 # will actually skip forward with a warning...
		self.cut = 0

		self.parasite_o = self.HDR_s
		self.prewrap = self.HDR_s


	def makeHdr(self, filename, data):
		hdr = b"".join([
			self.MAGIC,
			b"\0\0", # device
			b"\0\0", # inode
			b"\0\0", # permissions
			b"\0\0", # uid
			b"\0\0", # gid
			b"\0\0", # nlink
			b"\0\0", # rdevice number
			b"\0\0", # mtime[2]
			  b"\0\0",

			# name size (includes trailing null)
			int2l(len(filename) + 1),

			# filesize[2]
		  b"\0\0",
				int2l(len(data)),

			filename + b"\0",
				b"\0"*((len(filename) + 1) % 2),
			data
			])
		return hdr


	def fixformat(self, d, delta):
		# padding to 512 bytes
		if len(d) % 512 != 0:	
			d = d + b"\0" * (512 - (len(d) % 512))

		assert len(d) % 512 == 0
		return d


	def wrap(self, data):
		return self.makeHdr(b"", data)

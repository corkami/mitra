#!/usr/bin/env python

from parsers import FType


class parser(FType):
	DESC = "Ar / Unix archiver"
	TYPE = "AR"
	MAGIC = b"!<arch>\n"
	MAGIC_s = len(MAGIC)


	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data

		self.bParasite = True
		self.parasite_s = 0xffffff # ?

		self.bAppData = True # risks of "malformed archive", but wrappending ok

		self.hdr_s = 60 # len(self.makeHdr(b""))
		self.cut = self.MAGIC_s

		self.parasite_o = self.MAGIC_s + self.hdr_s
		self.prewrap = self.hdr_s


	def makeHdr(self, filename, timestamp=0, owner=0, group=0, perms=0, size=0):
		pad = lambda s, l:s.ljust(l, b" ")
		hdr = b"".join([
			pad(filename, 16),
			pad(b"%i" % timestamp, 12),
			pad(b"%i" % owner, 6),
			pad(b"%i" % group, 6),
			pad(b"%03i" % perms, 8), # in theory they are in octal
			pad(b"%i" % size, 10),
			b"`\n",
			])
		return hdr


# assert makeHdr(b"/") == b"/               0           0     0     000     0         `\n"
# assert makeHdr(b"hello.txt/", perms=644, size=13) == b"hello.txt/      0           0     0     644     13        `\n"


	def wrap(self, data):
		l = len(data)

		# word alignment padding
		if l % 2 == 1:
			data += b"\n"

		hdr = self.makeHdr(b"#1/0", size=l)
		return hdr + data

	def wrappend(self, data):
		return self.wrap(data)

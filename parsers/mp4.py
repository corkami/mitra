#!/usr/bin/env python

# MP4 format


from parsers import FType
import struct

def dprint(s):
	DEBUG = True
	DEBUG = False
	if DEBUG:
		print(("D " + s))


class parser(FType):
	DESC = "MP4 / Iso Base Media Format [container]"
	TYPE = "MP4"
	ATOM = b"ftyp"

	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data
		self.bParasite = True
		self.parasite_o = 0x8
		self.parasite_s = 0xFFFFFFFF # also exists in 64b flavor

		self.cut = 0 # yes
		self.prewrap = 2*4


	def identify(self):
		# ugly and totally incomplete but just works
		# limiting on purpose on standard files
		if self.data[4:4+4] != self.ATOM: # and self.data[0:3] != b"\0\0\0"
			return False

		# heif/c parsers don't support parasites or even appended data !?
		if self.data[8:8+3] == b"hei":
			return False
		return True


	def wrap(self, data):
		return struct.pack(">I", len(data) + 8) + b"free" + data


	def fixformat(self, d, delta):
		# finds and relocates all Sample Tables Chunk Offset tables
		# TODO: support 64 bits `co64` tables
		offset = 0
		tablecount = d.count(b"stco")
		dprint("stco found: %i" % tablecount)
		for i in range(tablecount):
			offset = d.find(b"stco", offset)
			dprint("current offset: %0X" % offset)

			length   = struct.unpack(">I", d[offset-4:offset])[0]
			verflag  = struct.unpack(">I", d[offset+4:offset+8])[0]
			offcount = struct.unpack(">I", d[offset+8:offset+12])[0]

			if verflag != 0:
				dprint(" version/flag not 0 (found %X) at offset: %0X" % (verflag, offset+4))
				continue

			# length, type, verflag, count - all 32b
			if (offcount + 4) * 4 != length:
				dprint(" Atom length (%X) and offset count (%X) don't match" % (length, offcount))
				continue

			dprint(" offset count: %i" % offcount)
			offset += 4 * 3
			offsets = struct.unpack(">%iI" % offcount, d[offset:offset + offcount * 4])
			dprint(" offsets (old): %s" % repr(list(offsets))) 
			offsets = [i + delta for i in offsets]
			dprint(" (new) offsets: %s" % repr(offsets))

			d = d[:offset] + struct.pack(">%iI" % offcount, *offsets) + d[offset+offcount*4:]

			offset += 4 * offcount

		dprint("")
		return d

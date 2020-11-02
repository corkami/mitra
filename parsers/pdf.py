#!/usr/bin/env python3

from parsers import FType
import os

mutool = "mutool"


def EnclosedString(d, starts, ends):
	off = d.find(starts) + len(starts)
	return d[off:d.find(ends, off)]


def getCount(d):
	s = EnclosedString(d, b"/Count ", b"/")
	count = int(s)
	return count


template = b"""%%PDF-1.3
%%\xC2\xB5\xC2

1 0 obj
<</Length 2 0 R>>
stream

endstream
endobj

2 0 obj
_PAYLOADL_
endobj

3 0 obj
<<
  /Type /Catalog
  /Pages 4 0 R
>>
endobj

4 0 obj
<</Type/Pages/Count %(count)i/Kids[%(kids)s]>>
endobj
"""


class parser(FType):
	DESC = "Portable Document Format"
	TYPE = "PDF"
	MAGIC = b"%PDF-1"

	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data

		# the whole `%PDF-1.3` signature has to be present in the first 1kb 
		self.start_o = 1024 - 8

		self.bAppData = True

		self.bParasite = True
		self.parasite_o = 0x30
		self.parasite_s = 0xFFFFFFFF

# Doesn't apply the usual way
		self.cut = 0x30


	def fixformat(self, contents, delta):
		"""dumb [start]xref fix: fixes old-school xref with no holes, with hardcoded \\n"""
		startXREF = contents.find(b"\nxref\n0 ") + 1
		endXREF = contents.find(b" \n\n", startXREF) + 1
		origXref = contents[startXREF:endXREF]
		objCount = int(origXref.splitlines()[1].split(b" ")[1])

		xrefLines = [
			b"xref",
			b"0 %i" % objCount,
			# mutool declare its first xref like this
			b"0000000000 00001 f "
			]


		i = 1
		while i < objCount:
			# only very standard object declarations
			off = contents.find(b"\n%i 0 obj\n" % i) + 1
			xrefLines.append(b"%010i 00000 n " % (off))
			i += 1

		xref = b"\n".join(xrefLines)

		# XREF length should be unchanged
		try:
			assert len(xref) == len(origXref)
		except AssertionError:
			print("<:", repr(origXref))
			print(">:", repr(xref))

		contents = contents[:startXREF] + xref + contents[endXREF:]

		startStartXref = contents.find(b"\nstartxref\n", endXREF) + len(b"\nstartxref\n")
		endStartXref = contents.find(b"\n%%EOF", startStartXref)
		contents = contents[:startStartXref] + b"%i" % startXREF + contents[endStartXref:]

		# offset @ cut + delta + 0x1C
		contents = contents.replace(b"_PAYLOADL_", b"%010i" % delta)

		# FIXME: find out why wrappending is one byte too long
		contents = contents[:-1]

		return contents


	def normalize(self):
		with open("host.pdf", "wb") as f:
			f.write(self.data)

		# merging with a dummy page (mutool)
		os.system(mutool + ' merge -o merged.pdf blank.pdf host.pdf')
		os.remove('host.pdf')

		with open("merged.pdf", "rb") as f:
			dm = f.read()
		os.remove('merged.pdf')

		# removing dummy page reference
		count = getCount(dm) - 1

		kids = EnclosedString(dm, b"/Kids[", b"]")

		# we skip the first dummy that should be 4 0 R because of the `mutool merge`
		assert kids.startswith(b"4 0 R ")
		kids = kids[6:]

		# fixing object references
		dm = dm[dm.find(b"5 0 obj"):]
		dm = dm.replace(b"/Parent 2 0 R", b"/Parent 4 0 R")
		dm = dm.replace(b"/Root 1 0 R", b"/Root 3 0 R")

		# need this to map b'payload' to the payload var ...?
		mapping = {}
		for s in ("count", "kids"):
			mapping[s.encode()] = locals()[s]

		# aligning payload header
		stage1 = template % mapping

		contents = (template % mapping) + dm

		self.data = contents

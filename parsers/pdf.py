#!/usr/bin/env python3

import fitz # PyMuPDF
import os
import re
from parsers import FType

# Strategy:
# 1. merge with a dummy single page doc to make room for an empty stream object at slot 1
#      This operations kills ToC, which need to be transferred and adjusted because of the dummy page.
# 2. overwrite first 4 object with a specific template to make sure offsets are correct
# 3. inject the payload at a fixed offset
# 4. update the payload length
# 5. update Xref and startxref offsets


def EnclosedString(d, starts, ends):
	off = d.find(starts) + len(starts)
	return d[off:d.find(ends, off)]

assert EnclosedString(b"/Kids[1 0 R]", b"/Kids[", b"]") == b"1 0 R"


def getCount(d):
	s = EnclosedString(d, b"/Count ", b"/")
	count = int(s)
	return count

assert getCount(b"/Count 314 /") == 314


def getObjDecl(d, s):
	val = EnclosedString(d, s, b"0 R")
	val = val.strip()
	if val.decode().isnumeric():
		return b"%s %s 0 R" % (s, val)
	else:
		return b""

assert getObjDecl(b"/Outlines 1 0 R", b"/Outlines") == b"/Outlines 1 0 R"


def getValDecl(d, s):
	"""locates declaration such as '/PageMode /UseOutlines' """
	off = d.find(s) + len(s)
	if off == -1:
		return b""
	match = re.match(b" *\/[A-Za-z0-9]*", d[off:])
	if match is None:
		return b""
	else:
		return b"%s %s" % (s, match[0])

assert getValDecl(b"/PageMode/UseOutlines", b"/PageMode") == b"/PageMode /UseOutlines"



def adjustToC(toc):
	"""increasing page numbers of each ToC entry"""
	for entry in toc:
		d = entry[3]
		if d["kind"] == 1:
			d["page"] += 1
			entry[2] += 1
	return toc

assert adjustToC([[0, 'Bookmark', 1, {'kind': 1, 'page': 25}]]) == [[0, 'Bookmark', 2, {'kind': 1, 'page': 26}]]


# This template starts the parasite at offset 0x30, which is a reasonable minimum.
# The dummy /Payload is to prevent garbage collection - remove to clean your file.
# the `extra` parameter will contain optional declarations of optional PDF catalog elements:
#   /Names, /OpenAction, /Outlines, /PageMode

template = b"""%%PDF-1.3
%%\xC2\xB5\xC2\xB6
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
	/Payload 1 0 R
	%(extra)s
>>
endobj

4 0 obj
<<
  /Type /Pages
  /Count %(count)i
  /Kids[%(kids)s]
>>
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
		_DEBUG_FILES = 0

		# Merging with a dummy page
		with fitz.open() as mergedDoc:

			with fitz.open() as blankdoc:
				blankdoc._newPage()
				mergedDoc.insert_pdf(blankdoc)

			with fitz.open(stream=self.data, filetype="pdf") as inDoc:
				if _DEBUG_FILES: inDoc.save("_0normalized.pdf")

				pagemode = getValDecl(inDoc.write(), b"/PageMode")

				toc = inDoc.get_toc(simple=False)
				toc = adjustToC(toc)

				mergedDoc.insert_pdf(inDoc)

			mergedDoc.set_toc(toc)
			merged_data = mergedDoc.write(no_new_id=True) # remove randomness
			if _DEBUG_FILES: mergedDoc.save("_1merged.pdf")

		# Removing dummy page reference
		count = getCount(merged_data) - 1


		outlines = getObjDecl(merged_data, b"/Outlines")
		names = getObjDecl(merged_data, b"/Names")
		openaction = getObjDecl(merged_data, b"/OpenAction")

		extra = outlines + names + openaction + pagemode


		# we skip the first dummy page that should be 4 0 R
		kids = EnclosedString(merged_data, b"/Kids[", b"]")
		RefObj4 = b"4 0 R "
		assert kids.startswith(RefObj4)
		kids = kids[len(RefObj4):]

		body = merged_data[merged_data.find(b"5 0 obj"):]

		# fixing object references
		body = body.replace(b"/Parent 2 0 R", b"/Parent 4 0 R") # one per page
		body = body.replace(b"/Root 1 0 R", b"/Root 3 0 R") # one in the trailer

		# need this to map b'payload' to the payload var ...?
		mapping = {}
		for s in (
			"count",
			"kids",
			"extra",
			):
			mapping[s.encode()] = locals()[s]

		templated = template % mapping

		# Make sure the cut is at the right offfset
		assert templated[41:41+16] == b"stream\nendstream"

		self.data = templated + body

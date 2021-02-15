#!/usr/bin/env python3

# common functions

# Ange Albertini 2020

import random
import re
from string import punctuation, digits, ascii_letters

def randblock(l):
	return bytes([random.randrange(255) for i in range(l)])


# Cosmetic functions ###########################################################

ASCII = (punctuation + digits + ascii_letters + " ").encode()

def hexii(c):
		#replace 00 by empty char
		if c == b"\0":
			return b"  "
		#replace printable char by .<char>
		if c in ASCII:
			return b" " + bytes([c])
		if c == 0x0a:
			return b"\n"
		if c == b"\r":
			return b"\\r"
		#otherwise, return hex
		return b"%02X" % c


def hexiis(s):
	return repr(b" ".join([hexii(c) for c in s]))[2:-1]


def showsplit(d, i):
	WIDTH = 8
	return "%s  |  %s" % (hexiis(d[i-WIDTH:i]), hexiis(d[i:i+WIDTH]))



# 'GCM' functions ##############################################################

def cut3(data, a):
	# skip 0:a[0] -- not needed ?
	return data[a[0]:a[1]], data[a[1]:a[2]], data[a[2]:]


def mixfiles(d1, d2, cuts):
	"""mixing data with exclusive parts of each data"""
	assert len(d1) == len(d2)
	d = b""
	start = 0
	keep = d1
	skip = d2
	for end in cuts:
		d += keep[start:end]
		start = end
		keep, skip = skip, keep
	d += keep[start:]
	return d


def splitfile(data, cuts):
	p1 = b""
	p2 = b""
	start = 0
	count = 0
	for end in cuts:
		count += 1
		p1 += data[start:end]
		p2 += randblock(end-start)

		start = end
		p1, p2 = p2, p1

	p1 += data[end:]
	p2 += randblock(len(data)-end)
	assert len(p1) == len(p2)
	if count % 2 == 1:
		p1, p2 = p2, p1

	return p1, p2



# PDF functions ################################################################

def EnclosedStringS(d, starts, ends):
	off = d.find(starts)
	return d[off:d.find(ends, off + len(starts))]


def EnclosedString(d, starts, ends):
	off = d.find(starts) + len(starts)
	return d[off:d.find(ends, off)]


def getCount(d):
	s = EnclosedString(d, b"/Count ", b"/")
	count = int(s)
	return count


def getObjDecl(d, s):
	val = EnclosedString(d, s, b"0 R")
	val = val.strip()
	if val.decode().isnumeric():
		return b"%s %s 0 R" % (s, val)
	else:
		return b""


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


def adjustToC(toc):
	"""increasing page numbers of each ToC entry"""
	for entry in toc:
		d = entry[3]
		if d["kind"] == 1:
			d["page"] += 1
			entry[2] += 1
	return toc


def adjustPDF(contents):
	startSig = contents.find(b"%PDF") # relative to file start
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
		xrefLines.append(b"%010i 00000 n " % (off -  startSig))
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
	contents = contents[:startStartXref] + b"%08i" % (startXREF - startSig) + contents[endStartXref:]

	return contents


template = b"""%%PDF-1.3
%%\xC2\xB5\xC2\xB6
1 0 obj
<</Length 2 0 R>>
stream
%(payload)s
endstream
endobj

2 0 obj
%(payload_l)i
endobj

3 0 obj
<<
	/Type /Catalog
	/Pages 4 0 R
	/Payload 1 0 R %% to prevent garbage collection
	%(extra)s %% optional: Names + OpenAction + Outlines + PageMode
	>>
endobj

4 0 obj
<</Type/Pages/Count %(count)i/Kids[%(kids)s]>>
endobj
"""

# a compact dummy PDF declaring an empty page
dummy = b"""%PDF-1.5
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Kids[3 0 R]/Type/Pages/Count 1>>endobj
3 0 obj<</Type/Page/Contents 4 0 R>>endobj
4 0 obj<<>>endobj

xref
0 5
0000000000 65536 f 
0000000009 00000 n 
0000000052 00000 n 
0000000101 00000 n 
0000000143 00000 n 

trailer<</Size 5/Root 1 0 R>>

startxref
163
%%EOF
"""

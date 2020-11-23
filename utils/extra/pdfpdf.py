#!/usr/bin/env python3

# A PDF/PDF crypto-polyglot generator

# Ange Albertini 2020


import os
import random
import sys
from string import punctuation, digits, ascii_letters

mutool = "wine ~/mutool.exe"
mutool = "mutool"


# number of blocks to be appended to the PE inside the PDF
BLOCKCOUNT = 2

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
			return bytes([c]) + b" "
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


random.seed(31415)



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
%(parasite)s
endstream
endobj

2 0 obj
%(lenPAR)i
endobj

3 0 obj
<</Type /Catalog /Pages 4 0 R>>
endobj

4 0 obj
<</Type/Pages/Count %(count)i/Kids[%(kids)s]>>
endobj
"""



# Main functions ###############################################################

if len(sys.argv) == 1:
	print("PDF-PDF GCM collider")
	print("Usage: pdfpdf.py <host.pdf> <parasite.pdf>")
	sys.exit()



print(" * merging host with a dummy page (mutool)") ############################

tiny = b"\n".join([
	b"%PDF-1.3",
	b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj",
	b"2 0 obj<</Kids[3 0 R]/Type/Pages>>endobj",
	b"3 0 obj<</Type/Page/Contents 4 0 R>>endobj",
	b"4 0 obj<<>>endobj",
	b"trailer<</Size 5/Root 1 0 R>>",
])

with open("_dummy.pdf", "wb") as f:
	f.write(tiny)

os.system(mutool + ' merge -o _merged.pdf _dummy.pdf %s' % (sys.argv[1]))

with open("_merged.pdf", "rb") as f:
	dm = f.read()



print(" * removing dummy page reference") ######################################
count = getCount(dm) - 1

kids = EnclosedString(dm, b"/Kids[", b"]")

# we skip the first dummy that should be 4 0 R because of `mutool merge`
REF = b"4 0 R "
assert kids.startswith(REF)
kids = kids[len(REF):]



print(" * fixing object references") ###########################################
dm = dm[dm.find(b"5 0 obj"):]
dm = dm.replace(b"/Parent 2 0 R", b"/Parent 4 0 R")
dm = dm.replace(b"/Root 1 0 R", b"/Root 3 0 R")



print(" * normalizing parasite (mutool)") ######################################

os.system(mutool + ' merge -o _normalized.pdf %s' % (sys.argv[2]))

with open("_normalized.pdf", "rb") as f:
	para = f.read()

para += b"\0" * (16 + (16 - (len(para) % 16)))

# for tag correcting and tag setting
para += b"\0" * 16 * BLOCKCOUNT

para_cuts = []
para_cuts += [para.find(b"\n1 0 obj\n<<") + 1]
para_cuts += [para.find(b"\n\nxref\n0 ", para_cuts[0]) + 1]
para_cuts += [para.find(b"\nstartxref\n", para_cuts[1]) + 1]

print(" parasite cuts:")
for _c in para_cuts:
	print("  %08x> %s" % (_c, showsplit(para, _c)))

# helps PDFjs to parse successfully
# cf https://mozilla.github.io/pdf.js/web/viewer.html
parasite = b"\n" + para[:para_cuts[2]] + b"\n%"
parasite += b"\0" * (16 - (len(parasite) % 16))

lenPAR = len(parasite)



print(" * inserting parasite") #################################################
mapping = {}
for s in ("parasite", "lenPAR", "count", "kids"):
	mapping[s.encode()] = locals()[s]

cuts = [0x30, 0x30 + lenPAR]


contents = (template % mapping) + dm
contents = contents[:contents.rfind(b"\nstartxref\n") + 1]

fakestartxref = b"\n".join([
	b"",
	b"startxref",
	b"%08i" % (len(contents)),
	b"%%EOF",
	b""
	])
contents += fakestartxref
# block alignment
contents += b"\0" * (16 - (len(contents) % 16))

cuts += [len(contents)]

contents += fakestartxref

with open("_parasited.pdf", "wb") as f:
	f.write(contents)



print(" * splitting & fixing payloads") ########################################
# by splitting, adjusting and merging, we can adjust xrefs easily.

print(" polyglot cuts:")
for _c in cuts:
	print("  %08x> %s" % (_c, showsplit(contents, _c)))

pdf1, pdf2 = splitfile(contents, cuts)
with open("_split1.pdf", "wb") as f: f.write(pdf1)
with open("_split2.pdf", "wb") as f: f.write(pdf2)

pdf1 = adjustPDF(pdf1)
pdf2 = adjustPDF(pdf2)
with open("_payload1.pdf", "wb") as f: f.write(pdf1)
with open("_payload2.pdf", "wb") as f: f.write(pdf2)



print(" * merging payloads & generating polyglot") #############################
final = mixfiles(pdf1, pdf2, cuts)
final += b"\0" * (16 - (len(final) % 16))
final += b"\0" * 16

offsets_s = repr(b"-".join([b"%x" % i for i in cuts]))[2:-1]
with open("Z(%s).pdf.pdf" % offsets_s, "wb") as f:
	f.write(final)



print(" * cleaning up temporary files") ########################################
for fn in [
	'dummy',
	'merged',
	'normalized',
	'parasited',
	'split1', 'split2',
	# adjusted separated plaintexts
#	'payload1', 'payload2',
]:
	if 1: os.remove("_%s.pdf" % fn)



print("Success!") # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
print()

sys.exit() #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

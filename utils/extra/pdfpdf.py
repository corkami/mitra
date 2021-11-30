#!/usr/bin/env python3

# A PDF/PDF crypto-polyglot generator

# Ange Albertini 2020

import fitz

from common import *
import os
import sys


# number of blocks to be appended to the parasite inside the PDF
BLOCKCOUNT = 2


random.seed(31415)

# Main functions ###############################################################

if len(sys.argv) == 1:
	print("PDF-PDF GCM collider")
	print("Usage: pdfpdf.py <host.pdf> <parasite.pdf>")
	sys.exit()


print(" * merging host with a dummy page") #####################################

with fitz.open() as mergedDoc:

	with fitz.open() as blankdoc:
		blankdoc._newPage()
		mergedDoc.insertPDF(blankdoc)

	with fitz.open(sys.argv[1]) as inDoc:
		mergedDoc.insertPDF(inDoc)
		toc = inDoc.getToC(simple=False)
		pagemode = getValDecl(inDoc.write(), b"/PageMode")
	adj_toc = adjustToC(toc)
	mergedDoc.setToC(adj_toc)
	dm = mergedDoc.write()

	if 0: mergedDoc.save("_1merged.pdf")

if pagemode == b"":
	pagemode = b"/PageMode /UseOutlines" 


print(" * removing dummy page reference") ######################################
count = getCount(dm) - 1

kids = EnclosedString(dm, b"/Kids[", b"]")

outlines = getObjDecl(dm, b"/Outlines")
names = getObjDecl(dm, b"/Names")
openaction = getObjDecl(dm, b"/OpenAction")

extra = outlines + names + openaction + pagemode

# we skip the first dummy that should be 4 0 R because of merge
REF = b"4 0 R "
assert kids.startswith(REF)
kids = kids[len(REF):]



print(" * fixing object references") ###########################################
dm = dm[dm.find(b"5 0 obj"):]
dm = dm.replace(b"/Parent 2 0 R", b"/Parent 4 0 R")
dm = dm.replace(b"/Root 1 0 R", b"/Root 3 0 R")



print(" * normalizing parasite") ###############################################

with fitz.open() as mergedDoc:
	with fitz.open(sys.argv[2]) as inDoc:
		toc = inDoc.getToC(simple=False)
		mergedDoc.insertPDF(inDoc)
	mergedDoc.setToC(toc)
	para = mergedDoc.write()

para += b"\0" * (16 + (16 - (len(para) % 16)))

# for tag correcting and tag setting
para += b"\0" * 16 * BLOCKCOUNT

para_cuts = []
para_cuts += [para.find(b"\n1 0 obj\n<<") + 1]
para_cuts += [para.find(b"\n\nxref\n0 ", para_cuts[0]) + 1]
para_cuts += [para.find(b"\nstartxref\n", para_cuts[1]) + 1]

print("  parasite cuts:")
for _c in para_cuts:
	print("   %08x> %s" % (_c, showsplit(para, _c)))

# helps PDFjs to parse successfully
# cf https://mozilla.github.io/pdf.js/web/viewer.html
payload = b"\n" + para[:para_cuts[2]] + b"\n%"
payload += b"\0" * (16 - (len(payload) % 16))

payload_l = len(payload)



print(" * inserting parasite") #################################################
mapping = {}
for s in ("payload", "payload_l", "count", "kids", "extra"):
	mapping[s.encode()] = locals()[s]

cuts = [0x30, 0x30 + payload_l]


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



print(" * splitting & fixing payloads") ########################################
# by splitting, adjusting and merging, we can adjust xrefs easily.

print("  polyglot cuts:")
for _c in cuts:
	print("   %08x> %s" % (_c, showsplit(contents, _c)))

pdf1, pdf2 = splitfile(contents, cuts)

pdf1 = adjustPDF(pdf1)
pdf2 = adjustPDF(pdf2)
if 0:
	with open("_payload1.pdf", "wb") as f: f.write(pdf1)
	with open("_payload2.pdf", "wb") as f: f.write(pdf2)



print(" * merging payloads & generating polyglot") #############################
final = mixfiles(pdf1, pdf2, cuts)
final += b"\0" * (16 - (len(final) % 16))
final += b"\0" * 16

offsets_s = repr(b"-".join([b"%x" % i for i in cuts]))[2:-1]
with open("Z(%s).pdf.pdf" % offsets_s, "wb") as f:
	f.write(final)

for i in range(6):
	WIDTH = 16
	l = WIDTH - 1
	s = i*(WIDTH)
	print("   %08x: %s" % (s, hexiis(final[s:s+l])))


print("Success!") # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
print()

sys.exit() #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

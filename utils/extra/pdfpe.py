#!/usr/bin/env python3

# A PDF/PE polyglot generator with signature overlap via nonce

# Ange Albertini 2020


import fitz # PyMuPDF

from common import *
import os
import sys

_DEBUG = 0

# number of blocks to be appended to the PE inside the PDF
BLOCKCOUNT = 2


# Main functions ###############################################################

if len(sys.argv) == 1:
  print("PDF-PE GCM collider")
  print("Usage: pdfpe.py <file1.pdf> <file2.exe>")
  sys.exit()

with open(sys.argv[2], "rb") as f:
  payload = f.read()

# for tag correcting and tag setting
payload += b"\0" * 16 * BLOCKCOUNT

assert payload.startswith(b"MZ")
payload = payload[0x33:] # aligning things
payload_l = len(payload) - 46 # minimal PDF header length


print(" * normalizing, merging with a dummy page") #############################

with fitz.open() as mergedDoc:
  with fitz.open("pdf", dummy) as dummyDoc:
    mergedDoc.insertPDF(dummyDoc)

  with fitz.open(sys.argv[1]) as inDoc:
    if _DEBUG: inDoc.save("_0normalized.pdf")

    pagemode = getValDecl(inDoc.write(), b"/PageMode")

    toc = inDoc.getToC(simple=False)
    toc = adjustToC(toc)

    mergedDoc.insertPDF(inDoc)

  mergedDoc.setToC(toc)
  dm = mergedDoc.write()
  if _DEBUG: mergedDoc.save("_1merged.pdf")


print(" * removing dummy page reference") ######################################
count = getCount(dm) - 1

kids = EnclosedString(dm, b"/Kids[", b"]")

outlines = getObjDecl(dm, b"/Outlines")
names = getObjDecl(dm, b"/Names")
openaction = getObjDecl(dm, b"/OpenAction")

extra = outlines + names + openaction + pagemode

# we skip the first dummy that should be 4 0 R because of the merge
RefObj4 = b"4 0 R "
assert kids.startswith(RefObj4)
kids = kids[len(RefObj4):]


print(" * fixing object references") ###########################################
dm = dm[dm.find(b"5 0 obj"):]
dm = dm.replace(b"/Parent 2 0 R", b"/Parent 4 0 R")
dm = dm.replace(b"/Root 1 0 R", b"/Root 3 0 R")


print(" * aligning PE header") #################################################
mapping = {}
for s in (
  "payload",
  "payload_l",
  "count",
  "kids",
  "extra",
  ):
  mapping[s.encode()] = locals()[s]

# aligning payload header
stage1 = template % mapping

streamOffset = stage1.find(b"stream\n") + len(b"stream\n")

payload = payload[streamOffset:]
payload_l = len(payload) 

mapping[b"payload_l"] = payload_l
contents = (template % mapping) + dm
contents = adjustPDF(contents)
if _DEBUG:
  with open("_2hacked.pdf", "wb") as f:
    f.write(contents)


print(" * finalizing main PDF") ################################################
# let's adjust offsets - using garbage=1 because object 2 is not required
with fitz.open("pdf", contents) as hackedDoc:
  cleaned = hackedDoc.write(garbage=1)


# Not always needed - most PE are aligned
# print(" * adding extra block")
# cleaned += randblock(16 + (16 - (len(cleaned) % 16)))


print(" * generating polyglot") ################################################

offsets = [2,
  cleaned.find(b"\nstream\n") + len(b"\nstream\n"),
  cleaned.find(b"\nendstream")]
offsets_s = repr(b"-".join([b"%x" % i for i in offsets]))[2:-1]

if not _DEBUG:
  cleaned = b"M" + b"Z" + cleaned[2:]

with open("Z(%s).exe.pdf" % offsets_s, "wb") as f:
  f.write(cleaned)

if _DEBUG:
  cleaned = b"M" + b"Z" + cleaned[2:]
  with open("Z(%s).exe" % offsets_s, "wb") as f:
    f.write(cleaned)

print("Success!")
print()

sys.exit() #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

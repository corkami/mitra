#!/usr/bin/env python3

# A PDF/PE polyglot generator with signature overlap via nonce

# Ange Albertini 2020

import fitz # PyMuPDF

import os
import sys


# number of blocks to be appended to the PE inside the PDF
BLOCKCOUNT = 2

# PDF functions ################################################################

def EnclosedString(d, starts, ends):
  off = d.find(starts) + len(starts)
  return d[off:d.find(ends, off)]

def getCount(d):
  s = EnclosedString(d, b"/Count ", b"/")
  count = int(s)
  return count

def adjustPDF(contents):
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

  return contents


template = b"""%%PDF-1.3
%%\xC2\xB5\xC2\xB6

1 0 obj
<</Length 2 0 R>>
stream
%(pe)s
endstream
endobj

2 0 obj
%(lenPE)i
endobj

3 0 obj
<<
  /Type /Catalog
  /Pages 4 0 R
  /Dummy 1 0 R %% to prevent object 1 from being discarded
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


# Main functions ###############################################################

if len(sys.argv) == 1:
  print("PDF-PE GCM collider")
  print("Usage: pdfpe.py <file1.pdf> <file2.exe>")
  sys.exit()

with open(sys.argv[2], "rb") as f:
  pe = f.read()

# for tag correcting and tag setting
pe += b"\0" * 16 * BLOCKCOUNT

assert pe.startswith(b"MZ")
pe = pe[0x33:] # aligning things
lenPE = len(pe) - 46 # minimal PDF header length


print(" * normalizing, merging with a dummy page") #############################
with fitz.open() as mergedDoc:
  with fitz.open("pdf", dummy) as dummyDoc:
    mergedDoc.insertPDF(dummyDoc)

  with fitz.open(sys.argv[1]) as inDoc:
    mergedDoc.insertPDF(inDoc)
  dm = mergedDoc.write()


print(" * removing dummy page reference") ######################################
count = getCount(dm) - 1

kids = EnclosedString(dm, b"/Kids[", b"]")

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
for s in ("lenPE", "pe", "count", "kids"):
  mapping[s.encode()] = locals()[s]

# aligning payload header
stage1 = template % mapping

streamOffset = stage1.find(b"stream\n") + len(b"stream\n")

pe = pe[streamOffset:]
lenPE = len(pe) 

mapping[b"lenPE"] = lenPE
contents = (template % mapping) + dm
contents = adjustPDF(contents)


print(" * finalizing main PDF") ################################################
# let's adjust offsets - using garbage=1 because object 2 is not required
with fitz.open("pdf", contents) as hackedDoc:
  cleaned = hackedDoc.write(garbage=1)

cleaned = b"M" + b"Z" + cleaned[2:]

# Not always needed - most PE are aligned
# print(" * adding extra block")
# cleaned += randblock(16 + (16 - (len(cleaned) % 16)))


print(" * generating polyglot") ################################################

offsets = [2,
  cleaned.find(b"\nstream\n") + len(b"\nstream\n"),
  cleaned.find(b"\nendstream")]
offsets_s = repr(b"-".join([b"%x" % i for i in offsets]))[2:-1]
with open("Z(%s).exe.pdf" % offsets_s, "wb") as f:
  f.write(cleaned)

print("Success!")

print()

sys.exit() #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

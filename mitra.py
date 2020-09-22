#!/usr/bin/env python

from parsers import *
import random
import sys
import hashlib
import os.path
from cmd import *

__version__ = "0.1" # https://semver.org/
__date__ = "2020-09-22"
__description__ = "Mitra v%s (%s) by Ange Albertini" % (__version__, __date__)

PARSERS = [
# placeholder
#	dummy.dummyParser,

# magic at 0
	arj.ARJparser,
	ar.ARparser,
	bmp.BMPparser,
	bpg.BPGparser,
	cpio.CPIOparser,
	ebml.EBMLparser,
	elf.ELFparser,
	flac.FLACparser,
	flv.FLVparser,
	gif.GIFparser,
	icc.ICCparser,
	ico.ICOparser,
	ilda.ILDAparser,
	java.JAVAparser,
	jp2.JP2parser,
	jpg.JPGparser,
	lnk.LNKparser,
	id3v2.ID3V2parser,
	nes.NESparser,
	ogg.OGGparser,
	pcap.PCAPparser,
	pcapng.PCAPNGparser,
	pe_sec.PEparser,
	pe_hdr.PEparser,
	png.PNGparser,
	riff.RIFFparser,
	svg.SVGparser,
	tiff.TIFFparser,
	wasm.WASMparser,
	xz.XZparser,

# magic potentially further but checked at 0
	_7z._7Zparser,
	mp4.MP4parser,
	pdf.PDFparser,
	gzip.GZIPparser,
	bzip2.BZ2parser,
	postscript.PSparser,
	zip_.ZipParser,
	rar.RARparser,
	rtf.RTFparser,

# magic further
	dcm.DICOMparser,
	iso.ISOparser,
	tar.TARparser,
	js.JSparser,
	php.PHPparser,

# footer
	id3v1.ID3V1parser,
]


def randbuf(length):
	return bytes([random.randrange(255) for i in range(length)])


def separatePayloads(fn, exts, data, swaps):
	NoFile, SplitDir = GetArgs(["NOFILE", "SPLITDIR"])

	ext1, ext2 = exts
	p1 = b""
	p2 = b""
	start = 0
	for end in swaps:
		p1 += data[start:end]
		p2 += randbuf(end-start)

		start = end
		p1, p2 = p2, p1

	p1 += data[end:]
	p2 += randbuf(len(data)-end)

	if not NoFile:
		with open(os.path.join(SplitDir, "%s.%s" % (fn, ext1)), "wb") as f:
				f.write(p1)
		with open(os.path.join(SplitDir, "%s.%s" % (fn, ext2)), "wb") as f:
				f.write(p2)
	return


def writeFile(name, exts, data, swaps = []):
	OutDir, NoFile, Split = GetArgs(["OUTDIR", "NOFILE", "SPLIT"])

	random.seed(0)
	hash = hashlib.sha256(data).hexdigest()[:8].lower()

	if Split and swaps != []:
		separatePayloads(name, exts, data, swaps)
	fn = "%s.%s.%s" % (name, hash, ".".join(exts))
	if not NoFile:
		with open(os.path.join(OutDir, "%s" % fn), "wb") as f:
				f.write(data)
	return


def isStackOk(ftype1, ftype2):
	dprint("Stack: %s-%s" % (ftype1.type, ftype2.type))
	result = True
	if not ftype1.bAppData:
		dprint("! File type 1 (%s) doesn't support appended data." % (ftype1.type))
		result = False

	if ftype2.start_o == 0:
		dprint("! File type 2 (%s) starts at offset 0 - it can't be appended." % (ftype2.type))
		return False
	else:
		len1 = len(ftype1.data)
		if len1 >= ftype2.start_o:
			dprint("! File 1 is too big (0x%X). File 2 should start at offset 0x%X or less." % (len1, ftype2.start_o) )
			result = False

	return result


def isCavOk(ftype1, ftype2):
	dprint("Cavity: %s_%s" % (ftype1.type, ftype2.type))
	filling = ftype1.data
	filling_l = len(ftype1.data)

	result = True
	if not ftype1.bAppData:
		dprint("! File type 1 (%s) doesn't support appended data." % (ftype1.type))
		result = False

	if not ftype2.precav_s:
		dprint("! File type 2 (%s) doesn't start with any cavity." % (ftype2.type))
		return False
	elif filling_l > ftype2.precav_s:
		dprint("! File 1 is too big (0x%X). File 2's cavity is only 0x%X." % (filling_l, ftype2.precav_s) )
		result = False

	return result


def isParasiteOk(ftype1, ftype2):
	dprint("Parasite: %s[%s]" % (ftype1.type, ftype2.type))
	result = True
	if not ftype1.bParasite:
		dprint("! File type 1 (%s) doesn't support parasites." % (ftype1.type))
		return False

	if (ftype1.parasite_o > ftype2.start_o):
		dprint("! File type 1 (%s) can only host parasites at offset 0x%X. File 2 should start at offset 0x%X or less." % (ftype1.type, ftype1.parasite_o, ftype2.start_o) )
		result = False

	if ftype1.parasite_s < len(ftype2.data):
		dprint("! File type 1 (%s) can accept parasites only of size 0x%X max. File 2 is too big (%X)." % (ftype1.type, ftype1.parasite_s, len(ftype2.data)) )
		result = False

	return result


def isZipperOk(ftype1, ftype2):
	dprint("Zipper: %s^%s" % (ftype1.type, ftype2.type))
	result = True
#  if not ftype1.bAppData:
#    dprint("! File type 1 (%s) doesn't support appended data." % (ftype1.type))
#    result = False

	if not ftype1.bParasite:
		dprint("! File type 1 (%s) doesn't support parasites." % (ftype1.type))
		return False

	if not ftype2.bParasite:
		dprint("! File type 2 (%s) doesn't support parasites." % (ftype2.type))
		return False

#	if ftype2.start_o != 0:
#		dprint("! File type 2 (%s) doesn't start at offset 0." % (ftype2.type))
#		return False

#  if (ftype1.parasite_o > ftype2.start_o):
#    dprint("! File type 1 (%s) can only host parasites at offset 0x%X. File type 2 (%s) should start at offset 0x%X or less." % (ftype1.type, ftype1.parasite_o, ftype2.type, ftype2.start_o) )
#    result = False

#  if len(ftype1.data) >= ftype2.start_o:
#    dprint("! File 1 is too big (0x%X). File type 2 (%s) should start at offset 0x%X or less." % (len(ftype1.data), ftype2.type, ftype2.start_o))
#    result = False

#  if ftype1.parasite_s < ftype2.parasite_o:
#    dprint("! File type 1 (%s) can accept parasites only of size 0x%X max. File 2's pre-parasite is too big (%X)." % (ftype1.type, ftype1.parasite_s, ftype2.parasite_o) )
#    result = False
#
#  if ftype2.parasite_s < len(ftype1.data) - ftype1.parasite_o:
#    dprint("! File type 2 (%s) can accept parasites only of size 0x%X max. File 1's post-parasite is too big (%X)." % (ftype2.type, ftype2.parasite_s, len(ftype1.data) - ftype2.parasite_o) )
#    result = False

	return result


def Hit(type1, type2):
	global VERBOSE
	if GetArg("VERBOSE"):
		dprint("HIT " + ";".join(sorted([type1, type2])))

def Stack(ftype1, ftype2, fn1, fn2):
	if isStackOk(ftype1, ftype2):
		print(("Stack: concatenation of File1 (type %s) and File2 (type %s)" % (ftype1.type, ftype2.type)))
		# appData = ftype2.fixformat(ftype2.data, len(ftype1.data)) # alignments / padding?
		appData = ftype2.data
		swap_o = len(ftype1.data + 
			ftype1.wrappend(b""))

		Hit(ftype1.type, ftype2.type)
		writeFile(
			"S(%x)-%s-%s" % (swap_o, ftype1.type, ftype2.type),
			[ext(fn2), ext(fn1)],
			ftype1.data + 
			ftype1.wrappend(appData),
			[swap_o]
		)


def Parasite(ftype1, ftype2, fn1, fn2):
	if isParasiteOk(ftype1, ftype2):
		print(("Parasite: hosting of File2 (type %s) in File1 (type %s)" % (
			ftype2.type, ftype1.type)))
		# host file may have to validate parasite contents
		parasitized, swaps = ftype1.parasitize(ftype2)
		swapstr = "(%s)" % "-".join("%x" % s for s in swaps) if swaps != [] else ""
		if parasitized is not None:
			Hit(ftype1.type, ftype2.type)
			writeFile(
				"P%s-%s[%s]" % (swapstr, ftype1.type, ftype2.type),
				[ext(fn1), ext(fn2)],
				parasitized,
				swaps
			)


def Zipper(ftype1, ftype2, fn1, fn2):
	if isZipperOk(ftype1, ftype2):
		print(("Zipper: interleaving of File1 (type %s) and File2 (type %s)" % (
			ftype1.type, ftype2.type)))
		# host file may have to validate parasite contents
		# appData = ftype2.fixformat(len(ftype1.data)) # alignments / padding?
		# parasite = ftype2.fixformat(ftype1.parasite_o)
		zipper, swaps = ftype1.zipper(ftype2)
		swapstr = "(%s)" % "-".join("%x" % s for s in swaps) if swaps != [] else ""
		if zipper is not None:
			Hit(ftype1.type, ftype2.type)
			writeFile(
				"Z%s-%s^%s" % (swapstr, ftype1.type, ftype2.type),
				[ext(fn1), ext(fn2)],
				zipper,
				swaps
			)


def Cavity(ftype1, ftype2, fn1, fn2):
	if isCavOk(ftype1, ftype2):
		print(("Cavity: File1 (type %s) into File2 (type %s)" % (ftype1.type, ftype2.type)))

		# missing normalization ?
		filling = ftype1.data
		filling_l = len(filling + ftype1.wrappend(b"")) # FIXME: variable length not supported
		filled = filling + ftype1.wrappend(ftype2.data[filling_l:])
		swap = filling_l
		Hit(ftype1.type, ftype2.type)
		writeFile(
			"C(%x)-%s-%s" % (swap, ftype1.type, ftype2.type),
			[ext(fn2), ext(fn1)],
			filled,
			[swap]
		)


ext = lambda s:s[s.rfind(".")+1:]


def DoAll(ftype1, ftype2, fn1, fn2):
	Stack(ftype1, ftype2, fn1, fn2)
	Parasite(ftype1, ftype2, fn1, fn2)
	Zipper(ftype1, ftype2, fn1, fn2)
	Cavity(ftype1, ftype2, fn1, fn2)


def main():
	args = Setup(__description__)
	fn1,fn2 = args.file1, args.file2
	with open(fn1, "rb") as f:
		fdata1 = f.read()
	with open(fn2, "rb") as f:
		fdata2 = f.read()

	pad = GetArg("PAD")
	fdata1 += b"\1" * (pad - len(fdata1))
	fdata2 += b"\1" * (pad - len(fdata2))

	ftype1 = None
	ftype2 = None

	for ftype in PARSERS:
		f = ftype(fdata1)
		if f.identify():
			ftype1 = f
		f = ftype(fdata2)
		if f.identify():
			ftype2 = f

	print("File type 1: %s" % ftype1.type)
	print("File type 2: %s" % ftype2.type)
	print("")

	if ftype1.type == ftype2.type:
		print("Same file types - aborting.")
		sys.exit()

	DoAll(ftype1, ftype2, fn1, fn2)
	if GetArg("REVERSE"):
		dprint("REVERSE: Switching files order")
		dprint("")
		DoAll(ftype2, ftype1, fn2, fn1)

if __name__ == "__main__":
	main()

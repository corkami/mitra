#!/usr/bin/env python3

from parsers import *
import random
import sys
import hashlib
import os.path
from args import *

__version__ = "0.2" # https://semver.org/
__date__ = "2021-01-14"
__description__ = "Mitra v%s (%s) by Ange Albertini" % (__version__, __date__)

PARSERS = [
# magic at 0
	arj, ar, bmp, bpg, cpio, cab, ebml, elf, flac, flv, gif, icc, ico, ilda, java,
	jp2, jpg, lnk, id3v2, nes, ogg, pcap, pcapng, pe_hdr, pe_sec, png, psd, riff,
	svg, tiff, wad, wasm, xz,

# magic potentially further but checked at 0
	_7z, mp4, pdf, gzip, bzip2, postscript, zip_, rar, rtf,

# magic further
	dcm, tar, pdfc, iso,

# footer
	id3v1,
]


def randbuf(length):
	return bytes([random.randrange(255) for i in range(length)])


def separatePayloads(fn, exts, data, swaps):
	NoFile, SplitDir = getVars(["NOFILE", "SPLITDIR"])

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
	OutDir, NoFile, Split = getVars(["OUTDIR", "NOFILE", "SPLIT"])

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
	dprint("Stack: %s-%s" % (ftype1.TYPE, ftype2.TYPE))
	result = True
	if not ftype1.bAppData:
		dprint("! File type 1 (%s) doesn't support appended data." % (ftype1.TYPE))
		result = False

	if ftype2.start_o == 0:
		dprint("! File type 2 (%s) starts at offset 0 - it can't be appended." % (ftype2.TYPE))
		return False
	else:
		len1 = len(ftype1.data)
		if len1 >= ftype2.start_o:
			dprint("! File 1 is too big (0x%X). File 2 should start at offset 0x%X or less." % (len1, ftype2.start_o) )
			result = False

	return result


def isCavOk(ftype1, ftype2):
	dprint("Cavity: %s_%s" % (ftype1.TYPE, ftype2.TYPE))
	filling = ftype1.data
	filling_l = len(ftype1.data)

	result = True
	if not ftype1.bAppData:
		dprint("! File type 1 (%s) doesn't support appended data." % (ftype1.TYPE))
		result = False

	if not ftype2.precav_s:
		dprint("! File type 2 (%s) doesn't have with any cavity." % (ftype2.TYPE))
		return False
	elif filling_l > ftype2.precav_s:
		dprint("! File 1 is too big (0x%X). File 2's cavity is only 0x%X." % (filling_l, ftype2.precav_s) )
		result = False

	return result


def isParasiteOk(ftype1, ftype2):
	dprint("Parasite: %s[%s]" % (ftype1.TYPE, ftype2.TYPE))
	result = True
	if not ftype1.bParasite:
		dprint("! File type 1 (%s) doesn't support parasites." % (ftype1.TYPE))
		return False

	# start_o is 0 when precav_s isn't
	if (ftype1.parasite_o > ftype2.start_o + ftype2.precav_s):
		dprint("! File type 1 (%s) can only host parasites at offset 0x%X. File 2 should start at offset 0x%X or less." % (ftype1.TYPE, ftype1.parasite_o, ftype2.start_o) )
		result = False

	if ftype1.parasite_s < len(ftype2.data):
		dprint("! File type 1 (%s) can accept parasites only of size 0x%X max. File 2 is too big (%X)." % (ftype1.TYPE, ftype1.parasite_s, len(ftype2.data)) )
		result = False

	return result


def isZipperOk(ftype1, ftype2):
	dprint("Zipper: %s^%s" % (ftype1.TYPE, ftype2.TYPE))
	result = True
	if not ftype1.bZipper:
		dprint("! File type 1 (%s) doesn't support zippers." % (ftype1.TYPE))
		return False
#  if not ftype1.bAppData:
#    dprint("! File type 1 (%s) doesn't support appended data." % (ftype1.TYPE))
#    result = False

	if not ftype1.bParasite:
		dprint("! File type 1 (%s) doesn't support parasites." % (ftype1.TYPE))
		return False

	if not ftype2.bParasite:
		dprint("! File type 2 (%s) doesn't support parasites." % (ftype2.TYPE))
		return False

#	if ftype2.start_o != 0:
#		dprint("! File type 2 (%s) doesn't start at offset 0." % (ftype2.TYPE))
#		return False

#  if (ftype1.parasite_o > ftype2.start_o):
#    dprint("! File type 1 (%s) can only host parasites at offset 0x%X. File type 2 (%s) should start at offset 0x%X or less." % (ftype1.TYPE, ftype1.parasite_o, ftype2.TYPE, ftype2.start_o) )
#    result = False

#  if len(ftype1.data) >= ftype2.start_o:
#    dprint("! File 1 is too big (0x%X). File type 2 (%s) should start at offset 0x%X or less." % (len(ftype1.data), ftype2.TYPE, ftype2.start_o))
#    result = False

#  if ftype1.parasite_s < ftype2.parasite_o:
#    dprint("! File type 1 (%s) can accept parasites only of size 0x%X max. File 2's pre-parasite is too big (%X)." % (ftype1.TYPE, ftype1.parasite_s, ftype2.parasite_o) )
#    result = False
#
#  if ftype2.parasite_s < len(ftype1.data) - ftype1.parasite_o:
#    dprint("! File type 2 (%s) can accept parasites only of size 0x%X max. File 1's post-parasite is too big (%X)." % (ftype2.TYPE, ftype2.parasite_s, len(ftype1.data) - ftype2.parasite_o) )
#    result = False

	return result


def Hit(type1, type2):
	global VERBOSE
	if getVar("VERBOSE"):
		dprint("HIT " + ";".join(sorted([type1, type2])))

def Stack(ftype1, ftype2, fn1, fn2):
	if isStackOk(ftype1, ftype2):
		print(("Stack: concatenation of File1 (type %s) and File2 (type %s)" % (ftype1.TYPE, ftype2.TYPE)))
		# appData = ftype2.fixformat(ftype2.data, len(ftype1.data)) # alignments / padding?
		appData = ftype2.data
		nullwrap = ftype1.wrappend(b"")
		if nullwrap is None:
			return None

		swap_o = len(ftype1.data + 
			ftype1.wrappend(b""))

		Hit(ftype1.TYPE, ftype2.TYPE)
		writeFile(
			"S(%x)-%s-%s" % (swap_o, ftype1.TYPE, ftype2.TYPE),
			[ext(fn2), ext(fn1)],
			ftype1.data + 
			ftype1.wrappend(appData),
			[swap_o]
		)


def Parasite(ftype1, ftype2, fn1, fn2):
	if isParasiteOk(ftype1, ftype2):
		print(("Parasite: hosting of File2 (type %s) in File1 (type %s)" % (
			ftype2.TYPE, ftype1.TYPE)))
		# host file may have to validate parasite contents
		parasitized, swaps = ftype1.parasitize(ftype2)
		if parasitized is None:
			return

		# TODO: make this for all layouts ?
		# Optional alignment via wrappending
		filealig = len(parasitized) % 16
		if getVar("AESGCM") and filealig > 0:
			# we need to know which sides wrappends
			wrap = ftype1
			if len(ftype2.wrappend(b"")) != 0:
				wrap = ftype2

			for i in range(17, 32):
				aligned = parasitized + wrap.wrappend(b"\0" * i)
				if len(aligned) % 16 == 0:
					break
			if wrap == ftype2:
				swaps += [len(parasitized)] # before wrappending
			parasitized = aligned


		swapstr = "(%s)" % "-".join("%x" % s for s in swaps) if swaps != [] else ""
		Hit(ftype1.TYPE, ftype2.TYPE)
		writeFile(
			"P%s-%s[%s]" % (swapstr, ftype1.TYPE, ftype2.TYPE),
			[ext(fn1), ext(fn2)],
			parasitized,
			swaps
		)


def Zipper(ftype1, ftype2, fn1, fn2):
	if isZipperOk(ftype1, ftype2):
		# host file may have to validate parasite contents
		# appData = ftype2.fixformat(len(ftype1.data)) # alignments / padding?
		# parasite = ftype2.fixformat(ftype1.parasite_o)
		zipper, swaps = ftype1.zipper(ftype2)
		if (zipper, swaps) == (None, []):
			return
		print(("Zipper: interleaving of File1 (type %s) and File2 (type %s)" % (
			ftype1.TYPE, ftype2.TYPE)))
		swapstr = "(%s)" % "-".join("%x" % s for s in swaps) if swaps != [] else ""
		Hit(ftype1.TYPE, ftype2.TYPE)
		writeFile(
			"Z%s-%s^%s" % (swapstr, ftype1.TYPE, ftype2.TYPE),
			[ext(fn1), ext(fn2)],
			zipper,
			swaps
		)


def Cavity(ftype1, ftype2, fn1, fn2):
	if isCavOk(ftype1, ftype2):
		print(("Cavity: File1 (type %s) into File2 (type %s)" % (ftype1.TYPE, ftype2.TYPE)))

		# TODO: requires any normalization ?
		filling = ftype1.data
		filling_l = len(filling + ftype1.wrappend(b"")) # FIXME: variable length not supported
		filled = filling + ftype1.wrappend(ftype2.data[filling_l:])
		swap = filling_l
		Hit(ftype1.TYPE, ftype2.TYPE)
		writeFile(
			"C(%x)-%s-%s" % (swap, ftype1.TYPE, ftype2.TYPE),
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

	pad = getVar("PAD")
	fdata1 += b"\1" * (pad - len(fdata1))
	fdata2 += b"\1" * (pad - len(fdata2))


	ftype1 = None
	ftype2 = None

	for parser in PARSERS:
		ftype = parser.parser
		f = ftype(fdata1)
		if f.identify():
			ftype1 = f
		f = ftype(fdata2)
		if f.identify():
			ftype2 = f

	print("%s" % fn1)
	if ftype1 is None:
			print("ERROR: Unknown type file 1 - aborting.")
			sys.exit()
	print("File 1: %s" % ftype1.DESC)

	print("%s" % fn2)
	if ftype2 is None:
		if getVar("FORCE"):
			ftype2 = blob.reader(fdata2)
		else:
			print("ERROR: Unknown type file 2 (try -f ?) - aborting.")
			sys.exit()

	print("File 2: %s" % ftype2.DESC)
	print("")

	if ftype1.TYPE == ftype2.TYPE:
		print("ERROR: Same file types - aborting.")
		sys.exit()


	DoAll(ftype1, ftype2, fn1, fn2)
	if getVar("REVERSE"):
		dprint("REVERSE: Switching files order")
		dprint("")
		DoAll(ftype2, ftype1, fn2, fn1)

if __name__ == "__main__":
	main()

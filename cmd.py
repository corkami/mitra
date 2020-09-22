import argparse


ARGS = {
	"VERBOSE" : False,
	"REVERSE" : False,
	"SPLIT"   : True,
	"SPLITDIR": "",
	"OUTDIR"  : "",
	"NOFILE"  : False,
	"PAD"     : 0 * 1024, # FTR: 128b DICOM / 1024 kb PDF / 32Kb ISO
}


def GetArgs(l):
	global ARGS
	return [ARGS[i] for i in l]


def GetArg(k):
	global ARGS
	return ARGS[k]


def SetArg(k, v):
	global ARGS
	ARGS[k] = v


def dprint(s):
	if GetArg("VERBOSE"):
		print(("> " + s))


def Setup(desc):
	parser = argparse.ArgumentParser(description="Generate binary polyglots.")
	parser.add_argument('file1',
		help="first (top) input file.")
	parser.add_argument('file2',
		help="second (bottom) input file.")
	parser.add_argument("-v", "--version", action="version", version=desc)
	parser.add_argument('--verbose', default=False, action="store_true",
		help="verbose output.")
	parser.add_argument('-n', '--nofile', default=False, action="store_true",
		help="Don't write any file.")
	parser.add_argument('-o', '--outdir',
		help="directory where to write polyglots.")
	parser.add_argument('-r', '--reverse', action="store_true",
		help="Try also with <file2> <file1> - in reverse order.")
	parser.add_argument('-s', '--split', action="store_true",
		help="split polyglots in separate files (off by default).")

	parser.add_argument('--splitdir', default='',
		help="directory for split payloads.")
	parser.add_argument('--pad', nargs=1, type=int, default=0,
		help="padd payloads in Kb (for expert).")

	args = parser.parse_args()

	if args.verbose:
		SetArg("VERBOSE", True)
		dprint("Arguments parsing:")
		dprint("Verbose is ON")

	if args.nofile:
		SetArg("NOFILE", True)
		dprint("NoFile is ON")

	if args.reverse:
		SetArg("REVERSE", True)
		dprint("Reverse is ON")

	if args.split:
		SetArg("SPLIT", True)
		dprint("Split is ON")

	if args.splitdir:
		SetArg("SPLITDIR", args.splitdir)
		dprint("Split directory output is %s" % repr(GetArg("SPLITDIR")))

	if args.outdir:
		SetArg("OUTDIR", args.outdir)
		dprint("Polyglots directory output is %s" % repr(GetArg("OUTDIR")))

	if args.pad != 0:
		pad = args.pad[0] * 1024
		SetArg("PAD", pad)
		dprint("Padding set to 0x%x" % pad)
	dprint("")
	return args

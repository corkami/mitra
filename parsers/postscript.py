#!/usr/bin/env python3

from args import *
from parsers import FType

class parser(FType):
	DESC = "PS / PostScript"
	TYPE = "PS"
	MAGIC = b"%!PS" # the magic actually shouldn't be at offset 0 but it's usually present.


	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data

		self.bParasite = True

		self.FunctionPar = True # Function parasite or inline parasite

		if self.FunctionPar:
			self.PREWRAP = b"/{(" # nameless function declaration
			self.POSTWRAP = b")}"
			self.validate = bBalancedPar
		else:
			self.PREWRAP = b"%" # nameless function declaration
			self.POSTWRAP = b"\r\n"
			self.validate = bNoNL

		# Magic can be actually further but only valid characters
		# and postscript logic must be present.
		self.start_o = 0

		self.cut = 0
		self.prewrap = len(self.PREWRAP)
		self.postwrap = len(self.POSTWRAP)

		self.parasite_o = self.prewrap   # right after the function declaration
		self.parasite_s = 0xFFFFFF       # quite unclear


	def wrap(self, data, bEnd=False):
		if bEnd:
			return b"stop\r\n" + data

		val_pos = self.validate(data)
		if val_pos != -1:
			if getVar("VERBOSE"):
				dprint("PostScript: parasite data (length %i) invalid at offset %i: ...%s..." % (len(data), val_pos, repr(data[val_pos - 2:val_pos+2])[2:-1]))
			return None
		wrapped = b"".join([
			self.PREWRAP,      
			data,
			self.POSTWRAP,
		])
		return wrapped


# for function parasites
def bBalancedPar(p):
	"""check if parenthesis are balanced no matter the content"""
	l = 0
	for i, c in enumerate(p):
		if c == ord(b"("):
			l += 1
		elif c == ord(b")"):
			l -= 1
			if l < 0:
				return i

	if l != 0:
		return i + 1
	return -1

assert bBalancedPar(b"") == -1
assert bBalancedPar(b"(") == 1
assert bBalancedPar(b")") == 0
assert bBalancedPar(b"()") == -1
assert bBalancedPar(b"())") == 2
assert bBalancedPar(b"(()") == 3
assert bBalancedPar(b"dcjdkwj(wljcwk)cwkejcwek") == -1
assert bBalancedPar(b"dcjdkwj(wljcwk)cwkejcw)k") == 22
assert bBalancedPar(b"dcjdkwj(wljcwk)cwkejcwe)") == 23
assert bBalancedPar(b"(dcjdkwj(wljcwk)wkejcwek") == 24
assert bBalancedPar(b"(dcjdkwj(wljcwk)wkejcwe)") == -1


# for inline comments parasites
def bNoNL(p):
	"""check if contains any RC, NL or FF chars"""
	for i, c in enumerate(p):
		if c in [0xA, 0xC, 0xD]:
			return i
	return -1

assert bNoNL(b"") == -1
assert bNoNL(b"\x0a") == 0
assert bNoNL(b"\x0c") == 0
assert bNoNL(b"\x0d") == 0
assert bNoNL(b" \x0d ") == 1
assert bNoNL(
	bytes([i for i in range(0,0xA)]) +
	bytes([i for i in range(0xE,256)])
	) == -1

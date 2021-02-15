#!/usr/bin/env python3

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

		if self.validate(data) == False:
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
	for c in p:
		if c == ord(b"("):
			l += 1
		elif c == ord(b")"):
			l -= 1
			if l < 0:
				return False

	if l != 0:
		return False
	return True

assert bBalancedPar(b"") == True
assert bBalancedPar(b"(") == False
assert bBalancedPar(b")") == False
assert bBalancedPar(b"()") == True
assert bBalancedPar(b"())") == False
assert bBalancedPar(b"())") == False
assert bBalancedPar(b"dcjdkwj(wljcwk)cwkejcwek") == True
assert bBalancedPar(b"dcjdkwj(wljcwk)cwkejcwe)") == False
assert bBalancedPar(b"(dcjdkwj(wljcwk)wkejcwek") == False
assert bBalancedPar(b"(dcjdkwj(wljcwk)wkejcwe)") == True


# for inline comments parasites
def bNoNL(p):
	"""check if contains any RC, NL or FF chars"""
	for c in p:
		if c in [0xA, 0xC, 0xD]:
			return False
	return True

assert bNoNL(b"") == True
assert bNoNL(b"\x0a") == False
assert bNoNL(b"\x0c") == False
assert bNoNL(b"\x0d") == False
assert bNoNL(b" \x0d ") == False
assert bNoNL(
	bytes([i for i in range(0,0xA)]) +
	bytes([i for i in range(0xE,256)])
	) == True

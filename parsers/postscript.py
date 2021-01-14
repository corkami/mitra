#!/usr/bin/env python3

from parsers import FType

# function parasites shouldn't contain unbalanced parenthesis

class parser(FType):
	DESC = "PS / PostScript"
	TYPE = "PS"
	MAGIC = b"%!PS" # the magic actually shouldn't be at offset 0 but it's usually present.
	PREWRAP = b"/{(" # nameless function declaration
	POSTWRAP = b"\n)\n}\n"

	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data

		self.bParasite = True

		# Magic can be actually further but only valid characters
		# and postscript logic must be present.
		self.start_o = 0

		self.cut = 0
		self.prewrap = len(self.PREWRAP)
		self.postwrap = len(self.POSTWRAP)

		self.parasite_o = self.prewrap   # right after the function declaration
		self.parasite_s = 0xFFFFFF       # quite unclear

		
	def wrap(self, data):
		wrapped = b"".join([
			self.PREWRAP,      
			data,
			self.POSTWRAP,
		])
		return wrapped

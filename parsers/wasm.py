#!/usr/bin/env python3

# WebAssembly

from parsers import FType
from helpers import int2b

def toLEB128(n):
	buf = []
	while True:
		out = n & 0x7f
		n >>= 7
		if n:
			buf += [out | 0x80]
		else:
			buf += [out]
			break
	return bytes(buf)

assert toLEB128(128) == b'\x80\x01'
assert toLEB128(127) == b'\x7f'

class parser(FType):
	DESC = "WASM / WebAssembly"
	TYPE = "WASM"
	MAGIC = b"\0asm\1\0\0\0"

	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data

		self.bAppData = False  # :(

		self.bParasite = True
		self.parasite_o = 0xC
		self.parasite_s = 0xFFFFFFFF

		self.cut = 8
		self.prewrap = 4


	def getPrewrap(self, parasite_s):
		parasite__ = b"\0" * parasite_s
		wrapped = self.wrap(parasite__)
		delta = len(wrapped) - parasite_s
		assert delta >= self.prewrap

		self.prewrap = delta
		return delta


	def wrap(self, parasite, name=b""):
		wrapped = int2b(len(name)) + name + parasite
		wrapped = b"\0" + toLEB128(len(wrapped)) + wrapped
		return wrapped

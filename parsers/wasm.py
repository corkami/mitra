#!/usr/bin/env python

# WebAssembly

from parsers import FType
import struct

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

class WASMparser(FType):
	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data
		self.type = "WASM"

		self.bAppData = False  # :(

		self.bParasite = True
		self.parasite_o = 0xC
		self.parasite_s = 0xFFFFFFFF

		self.cut = 8
		self.prewrap = 5 #TODO: it's variable, but not supported case yet


	def identify(self):
		return self.data.startswith(b"\0asm\1\0\0\0")


	def wrap(self, parasite, name=b""):
		wrapped = struct.pack(">H", len(name)) + name + parasite
		wrapped = b"\0" + toLEB128(len(wrapped)) + wrapped
		return wrapped

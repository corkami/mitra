#!/usr/bin/env python

# Executable and Linkable Format

# possible parasite strategies:
# 1. move Program Header further, right after File Header
# 2. move parasite after headers and between content (sections / segments)


from parsers import FType

from helpers import *

class ELFparser(FType):
	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data
		self.type = "ELF"
		self.bParasite = True
		self.parasite_o = 0x40 # dependant on the host file
		self.parasite_s = 0xFFFFFFFF
		self.cut = 0xb8


	def identify(self):
		d = self.data
		if not d.startswith(b"\x7fELF"):
			return False

		self.bits = 32 if d[4:4+1] == bytes([1]) else 64

		self.ph_o = get4l(d, 0x1c) if self.bits == 32 else get8l(d, 0x20)
		self.ph_s = get2l(d, 0x2a) if self.bits == 32 else get2l(d, 0x36)
		self.ph_c = get2l(d, 0x2c) if self.bits == 32 else get2l(d, 0x38)

		self.sh_o = get4l(d, 0x20) if self.bits == 32 else get8l(d, 0x28)
		self.sh_s = get2l(d, 0x2e) if self.bits == 32 else get2l(d, 0x3a)
		self.sh_c = get2l(d, 0x30) if self.bits == 32 else get2l(d, 0x3c)
		return True


	def getCut(self):
		# it's actually *after* all sections but I can't get anything to work yet :(
		d = self.data

		# rely on the section header table
		max_ = 0
		o = self.sh_o + self.sh_s
		for i in range(self.sh_c - 1):
			so = get4l(d, o+0x10) if self.bits == 32 else get8l(d, o+0x18)
			ss = get4l(d, o+0x14) if self.bits == 32 else get8l(d, o+0x20)
			max_ = max(max_, so + ss)
			o += self.sh_s
		self.cut = max_

		return self.cut


	def fixformat(self, d, delta):
		# update e_shoff in File Header
		d = inc4l(d,0x20, delta) if self.bits == 32 else inc8l(d, 0x28, delta)

		# fix Program header table - actually not required ?
		# o = self.ph_o
		# for i in range(self.ph_c):
		# 	d = inc4l(d, o+0x4, delta) if self.bits == 32 else inc8l(d, o+0x8, delta)
		# 	o += self.ph_s

		# fix section header table
		o = self.sh_o + delta # it has been moved down
		o += self.sh_s        # skip first entry
		for i in range(self.sh_c - 1): 
			d = inc4l(d, o+0x10, delta) if self.bits == 32 else inc8l(d, o+0x18, delta)
			o += self.sh_s

		return d

#!/usr/bin/env python3

from parsers import FType
from helpers import *


class parser(FType):
	DESC = "Java Class"
	TYPE = "Java"
	MAGIC = b"\xca\xfe\xba\xbe"

	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data

		self.bParasite = True # append an UTf8 buffer at the end of constant pool
		self.parasite_o = 0x9
		self.parasite_s = 0xffff

		self.bAppData = False # rejected - end wrapping via attributes or bytecount extension ?

		self.cut = 0x0a
		self.poolcount_o = 8
		self.prewrap = 3


	def identify(self):
		if not self.data.startswith(self.MAGIC): # potential collision with old school Mach-O binaries
			return False

		off = self.poolcount_o
		self.poolcount = get2b(self.data, off)
		return True


	def getCut(self):
		host = self.data
		off = 0x0a
		for _ in range(self.poolcount-1):
			type_ = host[off]
			off += 1
			if type_ == 1: # utf8
				string_l = get2b(host, off)
				off += string_l + 2

			elif type_ == 7: # class ref
				off += 2
			elif type_ == 8 : # string
				off += 2
			elif type_ == 16 : # method type
				off += 2

			elif type_ == 15 : # method handle
				off += 3

			elif type_ == 3 : # integer
				off += 4
			elif type_ == 4 : # float
				off += 4
			elif type_ == 9: # field ref
				off += 4
			elif type_ == 10: # method ref
				off += 4
			elif type_ == 11: # interface methodref
				off += 4
			elif type_ == 12 : # name and type
				off += 4
			elif type_ == 18 : # invoke dynamic
				off += 4

			elif type_ == 5 : # long
				off += 8
			elif type_ == 6 : # double
				off += 8
			else:
				# other cases not handled - module / package ?
				print("error", _, off, type_)
				return None

		self.cut = off
		self.parasite_o = self.cut + self.prewrap
		return self.cut


	def wrap(self, parasite):
		wrapped = b"\1" + int2b(len(parasite)) + parasite
		return wrapped


	def fixformat(self, d, delta):
		off = self.poolcount_o
		d = d[:off] + int2b(self.poolcount + 1) + d[off+2:]
		return d

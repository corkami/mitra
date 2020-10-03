#!/usr/bin/env python

# MP3 (with an ID3v2.3/4 header)

from parsers import FType
import struct


def _7to8(d):
	b3, b2, b1, b0 = struct.unpack('>4B', d[:4])
	assert b3 < 0x80
	assert b2 < 0x80
	assert b1 < 0x80
	assert b0 < 0x80
	return (((b3 * 0x80 + b2) * 0x80 + b1) * 0x80 + b0)

assert _7to8(b"\0\0\0\x7F") == 127
assert _7to8(b"\0\0\1\0")   == 128
assert _7to8(b"\0\0\x6a\x7F") == 13695


def _8to7(n):
	l = []
	for i in range(4):
		l += [n % 0x80]
		n = n // 0x80
	return bytes(l[::-1])

assert _8to7(127) == b"\0\0\0\x7f"
assert _8to7(128) == b"\0\0\1\0"
assert _8to7(13695) == b"\0\0\x6a\x7F"


class parser(FType):
	DESC = "ID3v2 [Tag]"
	TYPE = "ID3v2"
	MAGIC = b"ID3\3\0"

	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data
		self.bParasite = True
		self.cut = 0xA
		self.parasite_o = 0x14
		self.parasite_s = 0xffffff # ?

		# the ID3 header prevents the appended data from being interpreted
		# but it can conflict with an ID3v1 footer if also present
		self.bAppData = True

		self.prewrap = 4+4+2


	def wrap(self, data, type_=b"JUNK"):
		wrapped = b"".join([
			type_,
			_8to7(len(data)),
			b"\0\0",
			data,
		])
		return wrapped


	def fixformat(self, d, delta):
		SizeOff = 6
		SizeLen = 4
		d = b"".join([
			d[:SizeOff],
			_8to7(_7to8(d[SizeOff:SizeOff+SizeLen]) + delta),
			d[SizeOff+SizeLen:]])
		return d

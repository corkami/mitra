import struct
import binascii


BIG = ">"
LITTLE = "<" 


def pd(d, o):
	print("%04x: %s" % (o, binascii.hexlify(d[o:o+10])))


def get2l(d, o):
	return struct.unpack("<H", d[o:o+2])[0]

def get4l(d, o):
	return struct.unpack("<I", d[o:o+4])[0]

def get8l(d, o):
	return struct.unpack("<Q", d[o:o+8])[0]

def get2b(d, o):
	return struct.unpack(">H", d[o:o+2])[0]

def get4b(d, o):
	return struct.unpack(">I", d[o:o+4])[0]

def get8b(d, o):
	return struct.unpack(">Q", d[o:o+8])[0]


def get2(d, o, e):
	assert e[0] in "<>"
	return struct.unpack(e[0] + "H", d[o:o+2])[0]

def get4(d, o, e):
	assert e[0] in "<>"
	return struct.unpack(e[0] + "I", d[o:o+4])[0]


def inc4l(d, o, delta):
	s = 4
	v = struct.unpack("<I", d[o:o+s])[0]
	v += delta
	d = d[:o] + struct.pack("<I", v) + d[o+s:]
	return d

def inc4b(d, o, delta):
	s = 4
	v = struct.unpack(">I", d[o:o+s])[0]
	v += delta
	d = d[:o] + struct.pack(">I", v) + d[o+s:]
	return d

def inc4(d, o, delta, e):
	assert e[0] in "<>"
	s = 4
	v = struct.unpack(e[0] + "I", d[o:o+s])[0]
	v += delta
	d = d[:o] + struct.pack(e[0] + "I", v) + d[o+s:]
	return d

def inc8l(d, o, delta):
	s = 8
	v = struct.unpack("<Q", d[o:o+s])[0]
	v += delta
	d = d[:o] + struct.pack("<Q", v) + d[o+s:]
	return d

def inc8b(d, o, delta):
	s = 8
	v = struct.unpack(">Q", d[o:o+s])[0]
	v += delta
	d = d[:o] + struct.pack(">Q", v) + d[o+s:]
	return d


def int2b(i):
	return int2(i, BIG)

def int2l(i):
	return int2(i, LITTLE)

def int2(i, e):
	assert e[0] in "<>"
	return struct.pack(e[0] + "H", i)


def int4b(i):
	return int4(i, BIG)

def int4l(i):
	return int4(i, LITTLE)

def int4(i, e):
	assert e[0] in "<>"
	return struct.pack(e[0] + "I", i)


def getd(d, o, s):
	return d[o:o+s]

#!/usr/bin/env python3

# https://wiki.wireshark.org/Development/LibpcapFileFormat#Packet_Data
# A PCAP is just a sequence of packets after a fixed size header
# Just add a packet header and its data in the sequence

from parsers import FType
from helpers import *


class parser(FType):
	DESC = "PCAP / Packet Capture"
	TYPE = "PCAP"
	MAGIC = b"\xd4\xc3\xb2\xa1" # regular, swapped

	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data

		self.bAppData = False # end-wrapping is ok

		self.bParasite = True
		self.parasite_o = 0x5E
		self.parasite_s = 2621444 # 512^2 - hard limit MAXIMUM_SNAPLEN in netdissect.h

		self.cut = 0x18
		self.prewrap = 70


	def wrap(self, parasite):
		header = b"".join([
			# Packet
				2*b"\0\0\0\0",               # timestamps
				2*int4l(len(parasite) + 54), # lengths
			# Ethernet
				2*(6 * b"\0"), # dest/src
				b"\x08\0",     # type (IPV4)
			# IPV4
				b"\x45",                  # ver/len
				b"\0",                    # services
				b"\0\0",                  # len
				b"\0\0",                  # id
				b"\x40\0",                # flags (no frag)
				b"\0",                    # TTL
				b"\6",                    # Protocol (TCP)
				b"\0\0",                  # checksum
				b"\0\0\0\1", b"\0\0\0\1", # source / dest
				b"\0\0", b"\0\0",         # ports
			# TCP
				b"\0\0\0\0", b"\0\0\0\0", # nums
				b"\x50",                  # hdrlen
				b"\x18",                  # Flags (PSH + ACK)
				b"\2\0",                  # Windows
				b"\0\0",                  # checksum
				b"\0\0"                   # urgentptr
			])
		return header + parasite

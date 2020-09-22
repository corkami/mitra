#!/usr/bin/env python

__all__ = [
# containers
	"ebml",         # Extensible Binary Meta Language: Matroska, WebM...
	"flv",          # Flash Video
	"mp4",          # Atom/Box MP4.1 QuickTime .MOV MP4 
	"riff",         # Resource Interchange File Format: WAV AVI WebP...

# images
	"bpg",          # Better Portable Graphics
	"dcm",          # DICOM Digital Imaging and Communications in Medicine
	"icc",          # Color profiles
	"ico",          # Windows Icons (00 00 01 00)
	"ilda",         # International Laser Display Association
	"bmp",          # Bitmap image file
	"gif",          # Graphics Interchange Format
	"jpg",          # JFIF Joint Photographic Experts Group File Interchange Format
	"jp2",          # JPEG 2000
	"png",          # Portable Network Graphics
	"tiff",         # Tagged Image File Format
	"svg",          # Scalable Vector Graphics (XML-based images)

# documents
	"pdf",          # Portable Document Format
	"postscript",   # PostScript
	"rtf",          # Rich Text Format

# executables
	"elf",          # executable and linkable format
	"pe_hdr",       # portable executable (via PE header)
	"pe_sec",       # portable executable (via sections)
	"nes",          # iNES format rom
	"wasm",         # Web Assembly
	"java",         # Java class

# archives
	"_7z",
  "ar",
	"arj",
	"cpio",
	"gzip",
	"bzip2",
	"iso",
	"rar",
	"tar",
	"xz",
	"zip_",

# audio
	"id3v1",
	"id3v2",
	"flac",
	"ogg",

# misc
  "lnk",

# captures
	"pcap",         # Packet Capture
	"pcapng",       # Packet Capture Next Generation

	"php",          # PHP
	"js",           # JavaScript with html
#	"dummy",
]


class FType(object):

	def __init__(self, data=""):
		self.type = ""
		self.data = data

		self.cut = None # minimal cut generic to that format - updated by getCut

		# TODO: is it always self.parasite_o - self.cut ?
		self.prewrap = 0        #
		self.postwrap = 0       # data size to be added after the parasite - usually none

		self.start_o = 0        # where the format should start in the file

		self.bAppData = True    # does it tolerate appended data - quite common

		self.bParasite = False  # does it tolerate any parasite - quite common
		self.parasite_o = None  # min offset of a parasite (=cut + prewrap ?)
		self.parasite_s = None  # max size of a parasite

		self.precav_s = 0       # (max) size of pre-cavity


	def fixformat(self, data, delta=0):
		"""fixes the format data to be valid at a different offset"""
		return data # most format don't need relocations


	def wrap(self, data):
		"""Wrap a parasite into its containing element"""
		return data


	def getCut(self):
		"""return cut offset according to actual file data"""
		return self.cut


	def identify(self):
		"""returns True if this file matches the format """
		return False


	def fixparasite(self, parasite):
		"""fix parasite before wrapping (alignments,...)"""
		return parasite


	def normalize(self):
		"""normalize the host data for easier patching"""
		return


	def wrappend(self, data):
		"""wrapps appended data"""
		return data


	def parasitize(self, fparasite):
		self.normalize()
		host = self.data
		parasite = fparasite.data
		parasite = self.fixparasite(parasite)
		if len(parasite) > self.parasite_s:
			return None, []

		#TODO: need to do a pre-check before?
		cut = self.getCut()

		wrapped = self.wrap(parasite)
		delta = len(wrapped)
		prewrap = delta - len(parasite) - self.postwrap
		swaps = [
			cut + prewrap,
			cut + delta - self.postwrap,
		]

		merged = self.data[:cut] + wrapped + self.data[cut:]

		merged = self.fixformat(merged, delta)

		return merged, swaps


	def zipper(self, fhost):
		return None, []

#!/usr/bin/env python3

__all__ = [
# containers
	"ebml",         # Extensible Binary Meta Language: Matroska, WebM...
	"flv",          # Flash Video
	"ogg",          # Vorbis, Opus, Ogg Flac, Theora, Dirac
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
	"psd",          # Adobe Photoshop
	"tiff",         # Tagged Image File Format
	"svg",          # Scalable Vector Graphics (XML-based images)

# documents
	"pdf",          # Portable Document Format
	"pdfc",         # Portable Document Format (cavity)
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
	"cab",
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

# misc
  "lnk",          # Microsoft Shell Link

# captures
	"pcap",         # Packet Capture
	"pcapng",       # Packet Capture Next Generation

	"blob",
]


class FType(object):

	def __init__(self, data=""):
		self.type = ""
		self.data = data

		self.cut = None         # minimal cut generic to that format - updated by getCut

		# TODO: is it always self.parasite_o - self.cut ?
		self.prewrap = 0        # [minimal] size of data to be added before the parasite - updated by getPrewrap
		self.postwrap = 0       # [minimal] size of data to be added after the parasite - usually none

		self.start_o = 0        # where the format should start in the file

		self.bAppData = True    # does it tolerate appended data - quite common

		self.bParasite = False  # does it tolerate any parasite - quite common
		self.parasite_o = None  # min offset of a parasite (=cut + prewrap ?)
		self.parasite_s = None  # max size of a parasite

		self.bZipper = False

		self.precav_o = 0				# (fixed) offset of a pre-cavity
		self.precav_s = 0       # (max) size of pre-cavity


	def identify(self):
		"""returns True if this file matches the format """
		return self.data.startswith(self.MAGIC)


	def fixformat(self, data, delta=0):
		"""fixes the format data to be valid at a different offset"""
		return data # most format don't need relocations


	def wrap(self, data):
		"""Wrap a parasite into its containing element"""
		return data


	def getCut(self):
		"""return cut offset according to actual file data"""
		return self.cut


	def getPrewrap(self, parasite_s):
		"""return prewrap size according to size of parasite"""
		return self.prewrap


	def fixparasite(self, parasite):
		"""fix parasite before wrapping (alignments,...)"""
		return parasite


	def normalize(self):
		"""normalize the host data for easier patching"""
		return


	def wrappend(self, data):
		"""wrapps appended data"""
		return data


	def wrapparasite(self, fparasite, d, cut):
		# handle wrappending in parasite format
		deltaw0 = len(fparasite.wrappend(b""))
		if deltaw0 != 0:
			# only depends on the length, not the content
			# postwrap is always the same size
			wrappended = b"\0" * self.postwrap + self.data[cut:]

			wrappend = fparasite.wrappend(wrappended)
			deltaw = len(wrappend) - len(wrappended)

			d += wrappend[:deltaw]
		return d


	def cutparasite(self, fparasite, d, cut):
    # handle pre-cavity in parasite format
		prewrap_s = self.getPrewrap(len(d))
		if fparasite.precav_s > 0:
			# estimating just length changes
			prewrap2_l = self.getPrewrap(len(d[cut+prewrap_s:]))
			if prewrap2_l != prewrap_s: # the size change also changed the size of the prewrap
				return None, []  # TOCHECK: happens with ogg/xz ?

			d = d[cut+prewrap_s:]
		return prewrap_s, d


	def parasitize(self, fparasite):
		self.normalize()
		host = self.data
		parasite = fparasite.data
		parasite = self.fixparasite(parasite)
		if len(parasite) > self.parasite_s:
			return None, []

		#TODO: need to do a pre-check before?
		cut = self.getCut()

		parasite = self.wrapparasite(fparasite, parasite, cut)
		prewrap_s, parasite = self.cutparasite(fparasite, parasite, cut)
		if prewrap_s is None:
			return None, []

		wrapped = self.wrap(parasite)
		delta = len(wrapped)
		swaps = [
			cut + prewrap_s,
			cut + delta - self.postwrap,
		]

		merged = self.data[:cut] + wrapped + self.data[cut:]

		merged = self.fixformat(merged, delta)

		return merged, swaps


	def zipper(self, fhost):
		return None, []

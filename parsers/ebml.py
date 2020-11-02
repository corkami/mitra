#!/usr/bin/env python3

# strategy: attach a file, maybe change elements order, skip mimetype 
# TODO: experiment with ebmlite and XML editing


info = """
<Attachments id="0x1941A469" offset="780" size="163" sizeLength="2" type="list">
	<AttachedFile id="0x61A7" offset="786" size="159" sizeLength="2" type="list">
	<FileName id="0x466E" offset="790" size="7" sizeLength="1" type="unicode" value="zip.zip" />
	<FileMimeType id="0x4660" offset="800" size="15" sizeLength="1" type="str" value="application/zip" />
	<FlieUID id="0x46AE" offset="818" size="8" sizeLength="1" type="int" value="8942428418664394696" />
	<FileData id="0x465C" offset="829" size="117" sizeLength="1" type="bytearray">UEsDB...</FileData>
	</AttachedFile>
</Attachments>
"""

from parsers import FType

class parser(FType):
	DESC = "EBML / Extensible Binary Meta Language [container]"
	TYPE = "EBML"
	MAGIC = b"\x1A\x45\xDF\xA3"

	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data

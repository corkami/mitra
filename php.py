#!/usr/bin/env python



from parsers import FType


class parser(FType):
	DESC = "PHP / Hypertext Preprocessor"
	TYPE = "PHP"
	MAGIC = b"<PHP"

		def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data

		self.bParasite = False

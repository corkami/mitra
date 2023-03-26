#!/usr/bin/env python3

from parsers import FType
from helpers import *


class parser(FType):
    DESC = "Zstandard / LZ4"
    TYPE = "ZST"
    MAGICS = [
        b"\x04\x22\x4D\x18",  # LZ4 Frame
        b"\x02\x21\x4C\x18",  # Legacy Frame
        b"\x50\x2A\x4D\x18",  # Skippable Frame 0
        b"\x51\x2A\x4D\x18",  # Skippable Frame 1
        b"\x52\x2A\x4D\x18",  # Skippable Frame 2
        b"\x53\x2A\x4D\x18",  # Skippable Frame 3
        b"\x54\x2A\x4D\x18",  # Skippable Frame 4
        b"\x55\x2A\x4D\x18",  # Skippable Frame 5
        b"\x56\x2A\x4D\x18",  # Skippable Frame 6
        b"\x57\x2A\x4D\x18",  # Skippable Frame 7
        b"\x58\x2A\x4D\x18",  # Skippable Frame 8
        b"\x59\x2A\x4D\x18",  # Skippable Frame 9
        b"\x5A\x2A\x4D\x18",  # Skippable Frame A
        b"\x5B\x2A\x4D\x18",  # Skippable Frame B
        b"\x5C\x2A\x4D\x18",  # Skippable Frame C
        b"\x5D\x2A\x4D\x18",  # Skippable Frame D
        b"\x5E\x2A\x4D\x18",  # Skippable Frame E
        b"\x5F\x2A\x4D\x18",  # Skippable Frame F
        b"\x28\xB5\x2F\xFD",  # Zstandard Frame
    ]

    def __init__(self, data=""):
        FType.__init__(self, data)
        self.data = data
        self.bParasite = True
        self.parasite_o = 8
        self.parasite_s = 0xFFFFFFFF

        self.bAppData = True  # issued warning: Stream followed by undecodable data at position

        self.cut = 0
        self.prewrap = 2 * 4  # Magic, length

    def identify(self):
        for magic in self.MAGICS:
            if self.data.startswith(magic):
                return True
        return False

    def wrap(self, data):
        return b"\x50\x2A\x4D\x18" + int4l(len(data)) + data

    def wrappend(self, data):
        return self.wrap(data)

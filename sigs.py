mocks = {
  # "DOS":[0, b"MZ"],
  "jpg":[0, b"\xff\xd8"],
  # "Gzip":[0, b"\x1f\xb8"],
  "Compress":[0, b"\x1f\x9d"],

  "arj":[2, b"\x60\xEA"],
  "lha":[2, b"-LH1-"],

  "jp2":[4, b"jP"],
  "mp4":[4, b"ftyp"],
  "REDCode":[4, b"RED1"],
  "Clipper_trace":[4, b"pipe"],
  "Clipper_profile":[4, b"prof"],
  "Mathematica":[4, b" A~"],
  "QDos":[4, b"\x4a\xfb\x00\x00"],

  "unicos":[6, b"\x01\x07"],
  "Type1":[6, b"%!FontType1"],
  "AdobeType1":[6, b"%!PS-AdobeFont-1."],


  "ACE":[7, b"**ACE**"],
  # "DOS code page font data":[7, b"\x41\x47\x45\x00"],
  # "DOS code page font data (from Linux?)":[7, b"\x44\x49\x56\x00"],

  "Symbian":[8, b"\x19\x04\x00\x10"],
  "arc":[9, b"PSUR"],

  "snd":[12, b"SNDH"],
  "Bacula":[12, b"BB02"],
  "BerkeleyDB":[12, b"\x88\x09\x04\x00"],

  # "BIN-Header":[14, b"U2ND"],
  "jar":[14, b"\x1aJar\x1b"],

  # "NRO":[16, b"NRO0"],

  "wdk":[18, b"WDK\x202.0\x00"],

  "zoo":[20, b"\xdc\xa7\xc4\xfd"],

  "Wii":[24, b"\x5D\x1C\x9E\xA3"],

  "SoundFont":[26, b"sfArk"],

  # "AppleFileSystem":[32, b"NXSB"],

  "icc":[36, b"acsp"],
  "zImage":[36, b"\x18\x28\x6f\x01"],

  "VICAR":[43, b"SFDU_LABEL"],

  "PolyTracker ":[44, b"PTMF"],

  "SymbOs":[48, b"SymExe"],

  "netbsd_ktraceS":[56, b"hpux"],

  "SoundFX":[60, b"SONG"],
  "Mobipocket":[60, b"BOOKMOBI"],
  "Compack":[60, b"W Collis\x00\x00"],

  "WindowsCE": [63, b"\x00ECEC"],

  "VirtualBox":[64, b"\x7f\x10\xda\xbe"],

  "MacPaint":[65, b"PNTGMPNT"],

#  "BibTeX":[73, b"%%%  "],

  "ScreamTracker":[76, b"SCRS"],

  "Plot84":[92, b"PLOT%%84"],

  "ezd":[109, b"MAP ("],

  "dicom":[128, b"DICM"],

  "ds":[192, b"\x24\xff\xae\x51\x69\x9a\xa2\x21"],

  "CCP4":[208, b"MAP "],

  "DRDOS":[252, b"Must have DOS version"],

  "3ds":[256, b"NCCH"],

#  "TAR":[257, b"ustar"], # requires extra padding

  "gb":[260, b"\xCE\xED\x66\x66\xCC\x0D\x00\x0B"],

  "pif":[369, b"MICROSOFT PIFEX\x00"],

  "LockStream":[384, b"LockStream"],

  "mbr":[510, b"\x55\xAA"],

  "rootFS":[514, b"HdrS"],

  "Ultrix":[596, b"X\x0DF\xFF\xFF"],

  "Files-11":[1008, b"DECFILE11"],

  "F2FS":[1024, b"\x10\x20\xF5\xF2"],
  "HFSex":[1024, b"\x48\x2b"], 

  "MAR":[1028, b"MMX\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"],

  "Adlib":[1062, b"MaDoKaN96"],
  "AMUSIC":[1068, b"RoR"],

  "FastTracker":[1080, b"4CHN"],

  "IBM_OS400":[1090, b"\x19\xDB\xD8\xE2\xD9\xC4\xE2\xE2\xD7\xC3"],

  "KodakPCD":[2048, b"PCD_IPI"],
  "Minix":[2048, b"\x46\xfc\x27\x00"],

  "RAID":[4096, b"\xfc\x4e\x2b\xa9"],
  "DOSFONT2":[4098, b"DOSFONT"],

  "FastFS-1":[9564, b"\x54\x19\x01\x00"],

  "iso1":[32769, b"CD001"],

  "CDRom":[32777, b"CDROM"],

  "iso2":[37633, b"CD001"],

  "FastFS-2":[42332, b"\x19\x01\x54\x19"],

  "ReiserFS":[65588, b"ReIsEr2Fs"],

  "FastFS-22":[66908, b"\x19\x01\x54\x19"],

  "d64":[91392, b"\x12\x01\x41\x00"],
}



def getMocks(offset, maxlen):
  sigs = []
  result = b""
  for i, mock in enumerate(sorted(mocks, key=lambda l:mocks[l][0])):
    mock_o = mocks[mock][0]
    mock_l = len(mocks[mock][1])

    if mock_o < offset + len(result):
      continue
    if mock_o >= offset + maxlen:
      return result, sigs

    if mock_o + mock_l <= offset + maxlen:
      result += b"\0" * (mock_o - len(result) - offset)
      assert len(result) + offset == mock_o
      result += mocks[mock][1]
      sigs += [mock]


tests = [
  [0, 0, b""], 
  [0, 1, b""],                 # can't fit a sig
  [0, 2, b"\xff\xd8"],         # can fit a sig
  [0, 3, b"\xff\xd8"],         # can't fit anything more - no padding
  [0, 4, b"\xff\xd8\x60\xEA"], # can fit a 2nd sig
  [1, 2, b""],                 # can't fit a sig at that offset
  [2, 2, b"\x60\xEA"],
  [1, 3, b"\x00\x60\xEA"],
  [6, 2, b"\x01\x07"],
  [6, 8, b"\x01\x07\x19\x04\x00\x10"],
  [7, 7, b"**ACE**"],         # can get a different sig starting at 7
]

for i, test in enumerate(tests):
  off, len_, result = test
  testresult, _ = getMocks(off, len_)
  if testresult != result:
    print("ERROR test %i (0x%X, 0x%X): got" % (i, off, len_))
    print(testresult)
    print("instead of")
    print(result)
    import sys
    sys.exit()
# print("Tests completed")

def makeMocks():
  for mock in mocks:
    fn = mock
    offset, sig = mocks[mock]
    print(fn, offset, sig)
    with open(fn, "wb") as f:
      f.write(offset*b"\x00")
      f.write(sig)

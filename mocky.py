#!/usr/bin/env python3

# a polymock file maker:
#  adds extra mock signature(s) to a file of a known type while keeping it valid

# Ange Albertini MIT 2022


from parsers import *
import argparse
import os.path
from sigs import *


PARSERS = [
# magic at 0
  arj, ar, bmp, bpg, cpio, cab, ebml, elf, flac, flv, gif, icc, ico, ilda, java,
  jp2, jpg, lnk, id3v2, nes, ogg, pcap, pcapng, pe_sec, pe_hdr, png, psd, riff,
  svg, tiff, wad, wasm, xz,

# magic potentially further but checked at 0
  _7z, mp4, pdf, gzip, bzip2, postscript, zip_, rar, rtf,

# magic further
  dcm, tar, pdfc, iso,
]


def main():

  parser = argparse.ArgumentParser(description="Generate binary polymocks.")

  parser.add_argument('file', help="Input file.")

  parser.add_argument('-o', '--outdir', help="Set output directory.", default="")
  parser.add_argument('-f', '--force', help="Force raw file type.", action='store_true') 
  parser.add_argument('-m', '--maxoffset',
    help="Maximum mock signature offset (default = 0x200).", type=int, default=0x200)
  
  group = parser.add_mutually_exclusive_group(required=True)
  group.add_argument('-t', '--mocktype',
    help="Set a specific mocked file type.")
  group.add_argument('-a', '--all', action='store_true',
    help="All mock types will be tried independently, generating a separate file.")
  group.add_argument('-c', '--combined', action='store_true',
    help="All mock types will be tried together in a single file.")

  args = parser.parse_args()
  mocktype = args.mocktype
  bForce = args.force
  MAX = args.maxoffset
  outdir = args.outdir

  with open(args.file, "rb") as f:
    fdata = f.read()

  ftype = None
  for parser in PARSERS:
    f = parser.parser(fdata)
    if f.identify():
      ftype = f
      break

  if ftype is None:
    if bForce:
      ftype = blob.reader(fdata)
    else:
      print("No file type found in '%s'" % os.path.basename(args.file))
      return

  if mocktype is not None:
    if mocktype not in list(mocks):
      print("ERROR: Mock type '%s' not found in list:\n  %s" % (mocktype, " ".join(sorted(mocks))))
      return

  file_l = len(fdata)
  print("Filetype:", ftype.DESC)

  if args.combined:
    sigsc = []
    sigsp = []
    # pre-cavity
    if ftype.precav_s > 0:
      cav, sigsc = getMocks(0, ftype.precav_s)
      ftype.data = fdata = cav + b"\x00" * (ftype.precav_s - len(cav)) + fdata[ftype.precav_s:]
      print("Cavity-combined sig(s):", " / ".join(sigsc))

    # parasite
    if ftype.bParasite:
      parasite, sigsp = getMocks(
        ftype.getCut() + ftype.prewrap,
        min(ftype.parasite_s, MAX - ftype.parasite_o))
      if len(parasite) > 0:
        parasitized, _ = ftype.parasitize(blob.reader(parasite))

        if parasitized is not None:
          fdata = parasitized
          print("Parasite-combined sig(s):", " / ".join(sigsp))
    fdata = fixtarsum(fdata)
    fn = "mA-%s" % (os.path.basename(args.file))
    if sigsc + sigsp != []:
      print("> Combined Mock:", fn)
      fn = os.path.join(outdir, fn)
      with open(fn, "wb") as f:
        f.write(fdata)

    return 0


  for mock in mocks:
    if mocktype is not None:
      if mock != mocktype:
        continue
    sig_o, sig = mocks[mock]
    sig_l = len(sig)
    if sig_o > MAX:
      continue


    def precavity():
      if ftype.precav_s == 0:
        return
      if sig_o + sig_l > ftype.precav_s:
        return
      cav = b"\0" * sig_o + sig + fdata[sig_o+sig_l:]
      cav = fixtarsum(cav)

      fn = "mC-%s.%s" % (os.path.basename(args.file), mock)
      print("> Cavity Mock:", fn)
      fn = os.path.join(outdir, fn)
      with open(fn, "wb") as f:
        f.write(cav)
      return


    def parasitize():
      if not ftype.bParasite:
        return
      if ftype.parasite_o > sig_o:
        return
      if ftype.parasite_s < sig_l:
        return
      parasite = (sig_o - ftype.parasite_o) * b"\0" + sig
      if len(parasite) > ftype.parasite_s:
        return

      parasitized, _ = ftype.parasitize(blob.reader(parasite))
      if parasitized is None:
        print("ERROR: Parasitizing failure.")
        return
      parasitized = fixtarsum(parasitized)

      fn = "mP-%s.%s" % (os.path.basename(args.file), mock)
      fn = os.path.join(outdir, fn)
      print("> Parasite Mock:", fn)
      with open(fn, "wb") as f:
        f.write(parasitized)
      return


    def append():
      if not ftype.bAppData:
        return
      if file_l > sig_o:
        return

      appdata = (sig_o - file_l) * b"\0" + sig
      appended = fixtarsum(fdata + appdata)
      fn = "mS-%s.%s" % (os.path.basename(args.file), mock)
      fn = os.path.join(outdir, fn)
      print("> Stack Mock:", fn)
      with open(fn, "wb") as f:
        f.write(appended)
      return


    def wrappend():
      if ftype.bAppData:
        return
      if file_l + ftype.prewrap > sig_o:
        return

      parasite = (sig_o - file_l - ftype.prewrap) * b"\0" + sig
      if ftype.parasite_s is None or ftype.parasite_s < len(parasite):
        return
      wrappend = ftype.wrap(parasite)
      if wrappend is None:
        return
      wrappended = fdata + wrappend
      wrappended = fixtarsum(wrappended)
      fn = "mW-%s.%s" % (os.path.basename(args.file), mock)
      fn = os.path.join(outdir, fn)
      print("> Wrappended Mock:", fn)
      with open(fn, "wb") as f:
        f.write(wrappended)
      return


    precavity()
    parasitize()
    append()
    wrappend()



if __name__ == "__main__":
  main()

# Mitra

A tool to generate binary polyglots.

Loosely named after [Μιθραδάτης](https://en.wikipedia.org/wiki/Mithridates_VI_of_Pontus), a famous polyglot.
Pronounced `mɪtrə`.


# Features

For example, `mitra.py file1.png file2.dcm` gives you a working PNG/DICOM polyglot.

It tries different layouts:
Stacks (appended data), Cavities (blank space), Parasites (comments), Zippers (mutual comments).

It returns the offsets where the payloads 'switch sizes' for multi-ciphertexts.
Ex: `Z(80-162-286)-DICOM^TIFF.be3b767b.dcm.tif` is a DICOM/TIFF zipper
where the payloads switch side at offsets `0x80`, `0x162` and `0x286`.
The `-s` option extracts the 2 payloads separately, mixed with pseudo-random bytes.


Check Corkami [mini](https://github.com/corkami/pocs/tree/master/mini)
or [tiny](https://github.com/corkami/pocs/tree/master/tiny) PoCs for input files.
and the formats [repository](https://github.com/corkami/formats/tree/WIP) for some extra technical info.

It doesn't support crypto-polyglots or any polyglots with overlapping bytes.


## Goals

The goal of this project was to explore polyglots layouts, formats abuses,
and understand which format features makes which kind of abuse possible.

You really don't need to understand a file format totally to abuse it:
in a chunk-based format, just find where to `cut` the file,
then wrap foreign data in a new chunk.


# Status

```
                               Delayed           Magic at offset zero,               No appended
          Any offset   Cavities start           tolerated appended data                  data     Footer

         Z 7 A R J P   P I D T   P M   A B B C E E F F G G I I I I J J N O P P R R T   B J P P W   I X
         i Z r A a H   D S I A   S P   r M z P B L L l I z C C D L P P E g E N I T I   P a C C A   D Z
         p i j R v P   F O C R     4     P i I M F V a F i C O 3 D 2 G S g   G F F F   G v A A S   3
           p     a         O               p O L     c   p     v A             F   F     a P P M   v
                 S         M               2                   2                             N     1
                 c                                                                           G

Zip      . X X X X X   X X X X   X X   X X X X X X X X X X X X X X X X X X X X X X X   X X X X X       39
7Zip     X . X X X X   X X X X   X X   X X X X X X X X X X X X X X X X X X X X X X X   X X X X X       39
Arj      X X . X X X   X X X X   X X   X X X X X X X X X X X X X X X X X X X X X X X   X X X X X       39
RAR      X X X . X X   X X X X   X X   X X X X X X X X X X X X X X X X X X X X X X X   X X X X X       39
JavaSc   X X X X . X   X X X X   X X   X X X X X X X X X X X X X X X X X X X X X X X   X X X X X       39
PHP      X X X X X .   X X X X   X X   X X X X X X X X X X X X X X X X X X X X X X X   X X X X X       39

PDF      X X X X X X   . X X X   X X   X X X X X X X X X X X X X X X X X X X X X X X   X X X X X       39
ISO      X X X X X X   X . X X   X X   X X X X X X X X X X X X X X X X X X X X X X X                   34
DICOM    X X X X X X   X X .     X X   X   X X     X X X X   X X X X X X X X X X X X                   29
TAR      X X X X X X   X X   .   X X   X     X     X X   X   X X X X X   X   X X X X   X   X X X       29

PS       X X X X X X   X X X X   . X                                                                   11
MP4      X X X X X X   X X X X   X .                                                                   11

Ar       X X X X X X   X X X X         .                                                               10
BMP      X X X X X X   X X               .                                                              8
Bzip2    X X X X X X   X X X               .                                                            9
CPIO     X X X X X X   X X X X               .                                                         10
EBML     X X X X X X   X X                     .                                                        8
ELF      X X X X X X   X X                       .                                                      8
FLV      X X X X X X   X X X X                     .                                                   10
Flac     X X X X X X   X X X X                       .                                                 10
GIF      X X X X X X   X X X                           .                                                9
Gzip     X X X X X X   X X X X                           .                                             10
ICC      X X X X X X   X X                                 .                                            8
ICO      X X X X X X   X X X X                               .                                         10
ID3v2    X X X X X X   X X X X                                 .                                       10
ILDA     X X X X X X   X X X X                                   .                                     10
JP2      X X X X X X   X X X X                                     .                                   10
JPG      X X X X X X   X X X X                                       .                                 10
NES      X X X X X X   X X X                                           .                                9
Ogg      X X X X X X   X X X X                                           .                             10
PE       X X X X X X   X X X                                               .                            9
PNG      X X X X X X   X X X X                                               .                         10
RIFF     X X X X X X   X X X X                                                 .                       10
RTF      X X X X X X   X X X X                                                   .                     10
TIFF     X X X X X X   X X X X                                                     .                   10

BPG      X X X X X X   X     X                                                         .                8
Java     X X X X X X   X                                                                 .              7
PCAP     X X X X X X   X     X                                                             .            8
PCAPNG   X X X X X X   X     X                                                               .          8
WASM     X X X X X X   X     X                                                                 .        8

ID3v1                                                                                              .    0
XZ                                                                                                   .  0

Filetypes combinations: 322
```

Notes that some formats are containers and apply to several file types.

OTOH some container-based types aren't supporting all features and
can't be abused like other formats using the same container:
for example, `JUNK` chunks in `RIFF` containers...

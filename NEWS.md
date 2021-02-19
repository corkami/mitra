# 2021/02/19 v0.3

New:
- overlapping polyglots (flag '-o')
 - generic
 - specific for PE
- support w/ parasite: WAD
- tool: [AES-CTR exploit](utils/ctr/README.md)
- PostScript:
 - alternate parasite strategy
 - parasite validation
 - distinction between classic parasites and wrappending.
Fixes:
- gzip parasite in proper subfield in the extra field
- fixed PostScript wrap sizes
- fixed parasite offsets: BMP, BPG, FLAC, JAVA, CPIO, OGG, PSD, RIFF, CAB


# 2020/10/03 v0.2

New:
- support w/ parasite: Cab, PSD
- basic support: LNK
- flag '-f' to force parasiting of arbitrary data
- block padding option
- tool: [AES-GCM exploit](utils/gcm/README.md)

Fixes:
- fixed PostScript wrap sizes
- support cavity parasite and wrappending (ISO, DICOM)


# 2020/09/22 v0.1 Initial release

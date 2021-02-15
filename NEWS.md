# 2021/02/15 v0.2

New:
- support w/ parasite: Cab, PSD, Wad
- basic support: LNK
- flag '-f' to force parasiting of arbitrary data
- block padding option
- tool: [AES-GCM exploit](utils/gcm/README.md)
- PostScript:
 - alternate parasite strategy
 - parasite validation
 - distinction between classic parasites and wrappending.

Fixes:
- gzip parasite in proper subfield in the extra field
- fixed PostScript wrap sizes
- support cavity parasite and wrappending (ISO, DICOM)


# 2020/09/22 v0.1 Initial release

Examples of AES-GCM ciphertexts that decrypts to 2 valid plaintexts.

Use [decrypt.py](../) to test and decrypt them.


Polyglots:
- Standard (different formats starting at different offsets):
  - dicom-pe.gcm
  - gif-dicom.gcm
  - gzip-pdf.gcm
  - gzip-rar4.gcm
  - mp3-zip.gcm
  - mp4-pdf.gcm
  - ogg-rar.gcm
  - pcapng-iso.gcm
  - png-7z.gcm
  - psd-arj.gcm
  - tar-flv.gcm


- Overlap "crypto" polyglots (w/ bruteforced nonce):
  - 1 byte (PostScript)
    - ps-jpg.gcm
    - ps-pe.gcm [hand-made zipper]
    - ps-png.gcm
  - 2 bytes (Portable Executable)
    - png-pe.gcm
    - mp3-pe.gcm
    - bpg-pe.gcm
    - pdf-pe.gcm
    - jpg-pe.gcm
    - pe-pcapng.gcm
    - pdf-viewer.gcm (complete PDF article a PDF viewer PE)
    - wasm-pe.gcm
  - 5 bytes (JPG) - required manual post-processing for proper parasite length after encryption
    - jpg-bmp.gcm
    - jpg-png.gcm

Ambiguous files (same type):
- pdf-pdf.gcm
- jpg-jpg.gcm (overlap)
- zip-zip.gcm

These files where generated with Mitra but some were manually post-processed to overcome some limitations.

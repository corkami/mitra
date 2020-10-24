A tool to generate from a Mitra polyglot
a ciphertext that decrypts via AES-CTR as 2 valid files.


# Limitations

It currently doesn't identify any file format, so it's not able to:
- fix checksums that will be invalid when the other plaintext ranges are decrypted with the foreign key (TAR, ZIP, PNG...).

Some of the [available examples](examples/) may have been manually post-processed to fix these issues.


# How to


## Generate

First, generate a polyglot from two files:
```
$ mitra.py gzip.gz rar4.rar
```

A valid GZip/RAR polyglot is generated, named (in our case, depending on your actual input files) `S(24)-GZ-RAR.a7bccab6.rar.gz`.

- `S` indicates that it's a stack (concatenation).
- `(24)` is the list of hexadecimal offset(s) where the content of the polyglot change size. This list is likely to change with your input files.


## Exploit

Then, generate the ciphertext from that file:

```
$ exploit.py "S(24)-GZ-RAR.a7bccab6.rar.gz" gzip-rar4.ctr
Generated output: gzip-rar4.ctr
Tests:
 openssl enc -in gzip-rar4.ctr -out output1.rar -aes-128-ctr -iv 0 -K 4e6f773f
 openssl enc -in gzip-rar4.ctr -out output2.gz  -aes-128-ctr -iv 0 -K 4c34743372212121
```

It generates `gzip-rar4.ctr`:
```
0000: 38 15 D9 20 C8 5A F3 96 0B 70 D5 D3 DF A2 2B 2C  8 ┘ ╚Z≤û p╒╙▀ó+,
0010: E0 2B 7E A3 7C 8C 29 89 32 60 2D F4 88 33 4A BE  α+~ú|î)ë2`-⌠ê3J╛
0020: 9A 8F 22 9D 5E 37 DA 6C 1D 8C FB D0 E1 AD 2F F7  ÜÅ"¥^7┌l î√╨ß¡/≈
0030: D4 F0 0E EA A7 BF 42 CF 07 F9 17 63 F9 16 1B 08  ╘≡ Ωº┐B╧ ∙ c∙   
0040: CE 6D CB 10 20 F9 AE B7 89 00 47 C3 BC BD 08 6D  ╬m╦  ∙«╖ë G├╝╜ m
0050: 11 33 10 57 9D 51 BB 75 BC 0F 43 8E DC 2F 37 4D   3 W¥Q╗u╝ CÄ▄/7M
0060: 7E CC 90 1A 60 36 60 98 FD BD 84 3D D4 54 03 ED  ~╠É `6`ÿ²╜ä=╘T φ
```


## Test

Run the openssl statements to decrypt both files so that you can test their validity.

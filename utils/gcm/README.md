A tool to generate from a Mitra polyglot
a ciphertext that decrypts (with authentication) via AES-GCM as 2 valid files.


# Limitations

It currently doesn't identify any file format, so it's not able to:
- determine which block to use for bruteforcing - you might just want to append data if both file formats are supporting it.
- fix checksums that will be invalid when the other plaintext ranges are decrypted with the foreign key (TAR, ZIP, PNG...).

Some of the [available examples](examples/) have been manually post-processed to fix these issues.


# How to


## Generate

First, generate a polyglot from two files:
```
$ mitra.py mp4.mp4 pdf.pdf
```

A valid PDF/MP4 polyglot is generated, named (in our case, depending on your actual input files) `P(8-1ea)-MP4[PDF].54fdf8e6.mp4.pdf`.

- `P` indicates that it's a parasite.
- `0x8` and `0x1ea` are the offsets where the content of the polyglot change size. These offsets are likely to change with your input files.


## Exploit

Then, generate the ciphertext from that file:

```
$ meringue.py "P(8-1ea)-MP4[PDF].54fdf8e6.mp4.pdf" mp4-pdf.gcm
key 1: Now?
key 2: L4t3r!!!
ad   : MyVoiceIsMyPass!
 blocks: 87

Computing 89 coefficients.
Coef to be inverted: 4494a66081751930eed248b6fd11c74e (not present)
Inverting the coefficient (takes a few mins)...
```

It generates `mp4-pdf.gcm`:
```
key1: 4e6f773f000000000000000000000000
key2: 4c347433722121210000000000000000
adata: 4d79566f69636549734d795061737321
nonce: 000000000000000000000000
ciphertext: 9e8f2377a30df2c722dbbf595cef...424d3335e1cebbe78ca
tag: 6641372040f0f06640ffe463a1bb15dd
exts: mp4 pdf
origin: P(8-1ea)-MP4[PDF].54fdf8e6.mp4.pdf
```


## Test

Optionally, If you run `test.py mp4-pdf.gcm`,
it will test the correct authenticated decryption of both plaintexts,
and save them to files so that you can test their validity.


## Overlapping bytes (nonce bruteforcing)

Mitra generates standard polyglots, with no overlapping bytes.

However, you can bruteforce a nonce so that for a given set of bytes and encryption keys,
you find corresponding nonce values.

The bruteforcing operation only depends on the xor of the byte values,
for example for identical bytes (2 JGP headers), the xor values will be null.

`nonce.py` is a nonce bruteforcer.

Example of output (here for a dual JPG/JPG crypto-polyglot):
```
key1: 4e6f773f ('Now?')
key2: 4c34743372212121 ('L4t3r!!!')
hdr1: ffd8fffe ('\xff\xd8\xff\xfe')
hdr2: ffd8fffe ('\xff\xd8\xff\xfe')
start: 2 (GCM)
Results:
- nonce: 8108314280 (0x1E34B0EA8)
```

### JPG/JPG crypto-polyglot

`FF D8 FF FE` `XX XX` declares a JPG file and a comment segment of length `XX XX`.
In a crypto-polyglot, the next bytes will depend on the encryption keys, so the next bytes will depend on encryption keys.

So an abitrary set of two JPEG pictures can be merged into a crypto-polyglot that will be exploitable with `exploit.py` script.

```
jpg.py yes.jpg no.jpg
Generated file:
Z(0-6-a-208c-21af-21b3-2203).jpg.jpg
```

Which can then be exploited with the same keys and the bruteforced nonce (JPG supports appended data, so the default `-1` value is a valid block index):
```
meringue.py -n 8108314280 "Z(0-6-a-208c-21af-21b3-2203).jpg.jpg" jpg-jpg.gcm
key 1: Now?
key 2: L4t3r!!!
ad   : MyVoiceIsMyPass!
blocks: 556

Computing 558 coefficients.
Coef to be inverted: 4494a66081751930eed248b6fd11c74e (already computed)
```

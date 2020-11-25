Polyglot generators that exceed Mitra limitations
(ex: same file types, nonce overlap).


# PDF/PE polyglot with signature overlap

## Merge PDF and PE

`pdfpe.py paper.pdf SumatraPDF18fixed.exe`:

```
 * normalizing, merging with a dummy page
 * removing dummy page reference
 * fixing object references
 * aligning PE header
 * finalizing main PDF
 * generating polyglot
Success!
```


## Craft ciphertext

The block index depends on the PE.
The nonce is bruteforced according to the keys.

The nonce was 

`../gcm/meringue.py -i 135488 -n 59334 'Z(2-33-211420).exe.pdf' test.gcm`:

```
key 1: Now?
key 2: L4t3r!!!
ad   : MyVoiceIsMyPass!
blocks: 154060

Computing 154062 coefficients.
Coef to be inverted: 78a9f0686e9b7972252c8ca3796e3100 (already computed)
```


## Decrypt and test

`../gcm/test.py test.gcm`:
```
key1: b'Now?'
key1: b'L4t3r!!!'
ad: b'MyVoiceIsMyPass!'
nonce: 59334
tag: b'67d97a5e052efd0bd47f1db2d9a06067'
Success!

plaintext1: b'4d5a1526c3461a3f30486ccfd93e4a95' ...
plaintext2: b'255044462d312e330a25c2b5c2b60a0a' ...
```

# PDF/PDF crypto-polyglot

- make a PDF parasite inside another PDF
- move startxref away
- split contents
- adjust XREFS in both sides
- merge contents


## Merge PDFs

`pdfpdf.py host.pdf parasite.pdf`:

```
 * merging host with a dummy page
 * removing dummy page reference
 * fixing object references
 * normalizing parasite
  parasite cuts:
   00000010> \n  % C2 B5 C2 B6 \n \n  |   1     0     o  b  j \n
   00000140> \n  e  n  d  o  b  j \n  |  \n  x  r  e  f \n  0
   00000217>  4  B  3  >  ]  >  > \n  |   s  t  a  r  t  x  r  e
 * inserting parasite
 * splitting & fixing payloads
  polyglot cuts:
   00000030> \n  s  t  r  e  a  m \n  |  \n  %  P  D  F  -  1  .
   00000250> \n  % 00 00 00 00 00 00  |  \n  e  n  d  s  t  r  e
   000004d0> 00 00 00 00 00 00 00 00  |  \n  s  t  a  r  t  x  r
 * merging payloads & generating polyglot
   00000000:  %  P  D  F  -  1  .  3 \n  % C2 B5 C2 B6 \n
   00000010:     0     o  b  j \n  <  <  /  L  e  n  g  t
   00000020:     2     0     R  >  > \n  s  t  r  e  a  m
   00000030: \n  %  P  D  F  -  1  .  7 \n  % C2 B5 C2 B6
   00000040: \n  1     0     o  b  j \n  <  <  /  T  y  p
   00000050:  /  C  a  t  a  l  o  g  /  P  a  g  e  s
Success!
```


## Craft ciphertext

`../gcm/meringue.py "Z(30-48880-53640).pdf.pdf" pdfpdf.gcm`:

```
key 1: Now?
key 2: L4t3r!!!
ad   : MyVoiceIsMyPass!
blocks: 21351

Computing 21353 coefficients.
Coef to be inverted: 4494a66081751930eed248b6fd11c74e (already computed)
```


## Decrypt and test

`../gcm/test.py pdfpdf.gcm`:

```
key1: b'Now?'
key1: b'L4t3r!!!'
ad: b'MyVoiceIsMyPass!'
nonce: 0
tag: b'b86e564d0e95a201641bd4c903bfcecf'
Success!

plaintext1: b'255044462d312e330a25c2b5c2b60a31' ...
plaintext2: b'658bc0dee41811dcb2932a221d987ab7' ...
```

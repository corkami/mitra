Polyglot generators that exceed Mitra limitations
(ex: same file types, nonce overlap).


# PDF/PE polyglot with signature overlap

## Merge PDF and PE

`pdfpe.py paper.pdf SumatraPDF18fixed.exe`:

```
 * merging with a dummy page (mutool)
 * removing dummy page reference
 * fixing object references
 * aligning PE header
 * finalizing main PDF (mutool)
warning: PDF stream Length incorrect
 * generating polyglot
Success!
 * cleaning up temporary files
```


## Craft ciphertext

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
 * merging host with a dummy page (mutool)
error: cannot find startxref
warning: trying to repair broken xref
warning: repairing PDF document
 * removing dummy page reference
 * fixing object references
 * normalizing parasite (mutool)
 parasite swaps:
  00000010: \n  % C2 B5 C2 B6 \n \n  |   1     0     o  b  j \n
  00047e88: \n  e  n  d  o  b  j \n  |  \n  x  r  e  f \n  0
  0004883e:  1     0     R  >  > \n  |   s  t  a  r  t  x  r  e
 * inserting parasite
 * splitting & fixing payloads
 polyglot swaps:
  00000030: \n  s  t  r  e  a  m \n  |  \n  %  P  D  F  -  1  .
  00048880: 00 00 00 00 00 00 00 00  |  \n  e  n  d  s  t  r  e
  00053640: 00 00 00 00 00 00 00 00  |  \n  s  t  a  r  t  x  r
 * merging payloads & generating polyglot
 * cleaning up temporary files
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

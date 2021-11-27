# Malabar (bi-goût)

Ambiguous ciphertexts with different block ciphers instead of different keys.

# How to

1. Generate ambiguous file

As usual with mitra or specific tools.

`mitra/utils/extra$ pdfpdf.py yes.pdf no.pdf` => `Z(30-53e0-d600).pdf.pdf`

2. Generate ambiguous ciphertext

`mitra/utils/ofb/malabar$ malabar.py "Z(30-53e0-d600).pdf.pdf" pdfpdf.mal` => `pdfpdf.mal`

3. verify and decrypt plaintexts

`mitra/utils/ofb/malabar$ decrypt.py pdfpdf.mal` => `pdfpdf-1.85b2fe9a.pdf` and `pdfpdf-2.85b2fe9a.pdf`

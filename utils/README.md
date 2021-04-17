Tools to use with Mitra.


# Extra

File generators that don't match Mitra requirements: JPG/JPG, PDF/PDF


# Cryptographic


## AngeCryption

Encrypting (or decrypting) a valid file to another valid file: 
[slides](https://speakerdeck.com/ange/lets-play-with-crypto-v2).

- with no overlap: [ECB](ecb/).
- with overlap via IV: [CBC](cbc/), [CFB](cfb/), [OFB](ofb/).


## TimeCryption

Decrypting different valid payloads (in an authenticated way) from a single ciphertext:
[paper](https://eprint.iacr.org/2020/1456) / [slides](https://speakerdeck.com/ange/timecryption).


a.k.a Ambiguous ciphertexts, abusing one-time pad.

- without authentication (brioche): [CTR](ctr/), [OFB](ofb/).
- with authentication (meringue - w/ tag correction): [GCM](gcm/).

For GCM-SIV and OCB3, check Stephan Kölbl's [KeyCommitment repository](https://github.com/kste/keycommitment).

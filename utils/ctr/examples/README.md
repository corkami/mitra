Examples of AES-CTR ciphertext that decrypts to 2 valid plaintexts.

Use the following commands to test and decrypt them:


- `gzip-rar4.ctr`
 - `openssl enc -in gzip-rar4.ctr -out output1.gz  -aes-128-ctr -iv 0 -K 4e6f773f`
 - `openssl enc -in gzip-rar4.ctr -out output2.rar -aes-128-ctr -iv 0 -K 4c34743372212121`


These files where generated with Mitra but some were manually post-processed to overcome some limitations.

A tool to generate from a Mitra polyglot
a file that decrypts to another valid file via CFB (AngeCryption)

CFB is like CBC except that the IV computation is different, but still unique.

Since there are several sub-modes for CBC, it's important to set `segment_size` to a block size.

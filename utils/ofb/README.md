OFB (Output FeedBack) has both the IV structure of AngeCryption and the behavior of a one-time pad,
so it supports both AngeCryption and TimeCryption.

OFB's AngeCryption is like CFB: `iv = dec(p0 ^ c0)`

OFB's TimeCryption is via `IV` but not `nonce + counter`, which doesn't make much difference.

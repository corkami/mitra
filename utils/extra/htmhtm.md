Generating an ambiguous HTML/HTML dual webpage


# Ambiguous file layout

```
<!--[cut 1]-->
[page1]
<!--[cut 2]-->
[page2]
<!--
[padding]
[tag correction]
```


# Input files


## `normal.htm`

```
<html>Hello World!</html>
```

A script can be added to hide the extra 4 garbage characters that might be visible (from encrypting `<!--`), such as:
```
<html>
  <div id='mypage'>
    Hello World!
  </div>
  <script language=javascript type="text/javascript">
    document.documentElement.innerHTML = document.getElementById('mypage').innerHTML;
  </script>
</html>
```


## `evil.htm`

```
<html><a href="http://www.evil.com">Click here!</a></html>
```


# Invokations


## Generate an ambiguous HTML/HTML file

```
mitra/utils/extra$ htmhtm.py normal.htm evil.htm
```

Output: 
```
Creating '(4-26)7.d3f286cd.htm.htm'
 128 bytes
```


### Result (ambiguous html file)

In hex:
```
 00000000:  3C 21 2D 2D 2D 2D 3E 3C 68 74 6D 6C 3E 48 65 6C  <!----><html>Hel   << top file
 00000010:  6C 6F 20 57 6F 72 6C 64 21 3C 2F 68 74 6D 6C 3E  lo World!</html>
 00000020:  0D 0A 3C 21 2D 2D 2D 2D 3E 3C 68 74 6D 6C 3E 3C    <!----><html><   << bottom file
 00000030:  61 20 68 72 65 66 3D 22 68 74 74 70 3A 2F 2F 77  a href="http://w
 00000040:  77 77 2E 65 76 69 6C 2E 63 6F 6D 22 3E 43 6C 69  ww.evil.com">Cli
 00000050:  63 6B 20 68 65 72 65 21 3C 2F 61 3E 3C 2F 68 74  ck here!</a></ht
 00000060:  6D 6C 3E 3C 21 2D 2D 00 00 00 00 00 00 00 00 00  ml><!--            << padding
 00000070:  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00                     << block for tag correction
```

In text (minus padding):
```
<!----><html>Hello World!</html>
<!----><html><a href="http://www.evil.com">Click here!</a></html><!--
```

The file is padded, and the last block can be used for the tag correction, which is given by the filename.

In this case, block number `7`, to be used with Meringue.


## Generate an ambiguous GCM ciphertext

```
mitra/utils/gcm$ meringue.py -i 7 "(4-26)7.d3f286cd.htm.htm" attack.gcm
```

```
key 1: Now?
key 2: L4t3r!!!
ad   : MyVoiceIsMyPass!
blocks: 8

Computing 10 coefficients.
Coef to be inverted: 4494a66081751930eed248b6fd11c74e (already computed)
```


### Result (ambiguous ciphertext)

An `attack.gcm` file detailing the ciphertext and all the parameters.

```
key1: 4e6f773f000000000000000000000000
key2: 4c347433722121210000000000000000
adata: 4d79566f69636549734d795061737321
nonce: 000000000000000000000000
ciphertext: a2ae0fb0217b96716fff96734f964a9bb59f2ebdc8cd2eab9f5f4c2b1d567732c367f7350dd475a0d5bee16653632beb2434eed2da237066ea0201e8b24598e07fb80beff391eb5c7a2152f8717a808fa54182b27e43b3e313099aa9b9d871814148d0ab905f6ed42d590da42454acf9f1f58e1e080df5e9998346b59cdbad5b
tag: cf0e2d3f7d5c88f94087d6c64f805a68
exts: htm htm
origin: (4-26)7.d3f286cd.htm.htm
```


## Generate payloads

```
mitra/utils/gcm$ decrypt.py attack.gcm
```

```
key1: b'Now?'
key1: b'L4t3r!!!'
ad: b'MyVoiceIsMyPass!'
nonce: 0
tag: b'd9576e00f216f35d00fbc10cba40e124'
Success!

plaintext1: b'3c212d2de40401d3d0c285fbe16615ea' ...
plaintext2: b'7cfaa9b52d2d3e3c68746d6c3e48656c' ...
```


### Results (payload)

`attack-1.7b2a3b1d.htm`:

```
00000000:  3C 21 2D 2D E4 04 01 D3 D0 C2 85 FB E1 66 15 EA  <!--Σ  ╙╨┬à√ßf Ω
00000010:  7C 5D 12 E7 BD 42 56 80 D1 0A 7D 5E 88 BE 24 AD  |] τ╜BVÇ╤ }^ê╛$¡
00000020:  2E F2 A0 A5 00 9A                                .≥áÑ Ü          
      +6:  .. .. .. .. .. .. 2D 2D 3E 3C 68 74 6D 6C 3E 3C        --><html><    << bottom file
00000030:  61 20 68 72 65 66 3D 22 68 74 74 70 3A 2F 2F 77  a href="http://w
00000040:  77 77 2E 65 76 69 6C 2E 63 6F 6D 22 3E 43 6C 69  ww.evil.com">Cli
00000050:  63 6B 20 68 65 72 65 21 3C 2F 61 3E 3C 2F 68 74  ck here!</a></ht
00000060:  6D 6C 3E 3C 21 2D 2D                             ml><!--         
      +7:  .. .. .. .. .. .. .. 00 00 00 00 00 00 00 00 00                      << padding
00000070:  97 66 DA A7 E2 4C 2D 67 C6 CE BB 87 C1 02 D7 16  ùf┌ºΓL-g╞╬╗ç┴ ╫     << tag correction
```

`attack-2.7b2a3b1d.htm`:

```
00000000:  7C FA A9 B5                                      |·⌐╡            
      +4:  .. .. .. .. 2D 2D 3E 3C 68 74 6D 6C 3E 48 65 6C      --><html>Hel    << top file
00000010:  6C 6F 20 57 6F 72 6C 64 21 3C 2F 68 74 6D 6C 3E  lo World!</html>
00000020:  0D 0A 3C 21 2D 2D                                  <!--          
      +6:                    DB 15 FD 8A 87 3D FB 47 11 D6        █ ²èç=√G ╓
00000030:  28 37 F6 85 67 72 CB 13 24 6C 30 52 40 1E D7 D9  (7÷àgr╦ $l0R@ ╫┘
00000040:  01 C4 21 A9 03 F5 CA 96 B3 58 EB BE A5 6E 84 62   ─!⌐ ⌡╩û│Xδ╛Ñnäb
00000050:  30 A6 11 EA A6 D8 0D DF 52 E5 34 76 65 7C C3 31  0ª Ωª╪ ▀Rσ4ve|├1
00000060:  CE 5B 68 CF A8 8C 33 A6 8D E2 F8 8C 19 97 C0 3F  ╬[h╧¿î3ªìΓ°î ù└?

00000070:  84 D3 61 88 2B 93 E4 89 EF D9 09 28 2E 38 53 50  ä╙aê+ôΣë∩┘ (.8SP    << tag correction
```

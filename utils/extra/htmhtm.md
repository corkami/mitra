Generating an ambiguous HTML/HTML dual webpage

# Input files

## `normal.htm`

```
<html>
Hello World!
</html>
```

A script can be added to hide the extra 4 garbage characters that might be visible (from encrypting `<!--`):
```
<html>
<div id='mypage'>
Hello World!
</div>
<script language=javascript type="text/javascript">document.documentElement.innerHTML = document.getElementById('mypage').innerHTML;</script>
</html>
```

## `evil.htm`

```
<html>
<a href="http://www.evil.com">Click here!</a>
</html>
```

# Invokation

## Generate an ambiguous HTML/HTML

```
mitra/utils/extra$ htmhtm.py normal.htm evil.htm
```

Output: 
```
Creating '(4-d4)28.d26b6456.htm.htm'
 464 bytes
```

The file is padded, and the last block can be used for the tag, which is given by the filename. In this case, `28`.


## Generate an ambiguous GCM ciphertext

```
mitra/utils/gcm$ meringue.py -i 28 "(4-d4)28.d26b6456.htm.htm" attack.gcm
```

```
key 1: Now?
key 2: L4t3r!!!
ad   : MyVoiceIsMyPass!
blocks: 29

Computing 31 coefficients.
Coef to be inverted: 4494a66081751930eed248b6fd11c74e (already computed)
```

## Payloads verification

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

plaintext1: b'3c212d2de40401d3d0c285fbe1237aba' ...
plaintext2: b'7cfaa9b52d2d3e3c68746d6c3e0d0a3c' ...
```

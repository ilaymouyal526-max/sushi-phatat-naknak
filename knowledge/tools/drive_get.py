#!/usr/bin/env python3
"""Download Yoko Ono Drive photos/videos by catalog code (free, no login needed).

Usage: python3 knowledge/tools/drive_get.py OUT_DIR Y347 Y421 R145 ...
       python3 knowledge/tools/drive_get.py OUT_DIR --find "tataki"     (search titles)
Codes and ids are in knowledge/drive-inventory.json; what each photo shows is in knowledge/ASSETS.md.
HEIC files (R026-R119) are fetched as a full-size JPEG through Drive's thumbnail service.
"""
import json, os, subprocess, sys
INV = json.load(open(os.path.join(os.path.dirname(__file__), '..', 'drive-inventory.json')))
BY = {x['code']: x for x in INV if x['code']}
out, args = sys.argv[1], sys.argv[2:]
if args[:1] == ['--find']:
    q = args[1].lower()
    for x in INV:
        if q in x['title'].lower(): print(x['code'], x['folder'], x['title'])
    sys.exit()
os.makedirs(out, exist_ok=True)
for c in args:
    x = BY[c]
    heic = x['mime'] == 'image/heif'
    name = f"{c}_{x['title'].replace('/', '_')}" + ('.jpg' if heic else '')
    url = (f"https://drive.google.com/thumbnail?id={x['id']}&sz=w4000" if heic
           else f"https://drive.usercontent.google.com/download?id={x['id']}&export=download&confirm=t")
    subprocess.run(['curl', '-sSL', '--retry', '3', '-o', os.path.join(out, name), url], check=True)
    print(os.path.join(out, name))

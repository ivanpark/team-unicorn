#!/usr/bin/env python3
"""Verify files against SHA256SUMS in this curated research release (stdlib only)."""
from pathlib import Path
import hashlib,sys
root=Path(__file__).resolve().parents[1]
manifest=root/'SHA256SUMS'
if not manifest.exists(): raise SystemExit('Missing SHA256SUMS')
count=0
for row in manifest.read_text(encoding='utf8').splitlines():
    if not row.strip():continue
    digest, rel=row.split('  ',1)
    f=root/rel
    if not f.is_file():raise SystemExit('MISSING: '+rel)
    h=hashlib.sha256()
    with f.open('rb') as stream:
        while True:
            chunk=stream.read(1024*1024)
            if not chunk:break
            h.update(chunk)
    if h.hexdigest()!=digest:raise SystemExit('HASH MISMATCH: '+rel)
    count+=1
print('OK:',count,'files verified')

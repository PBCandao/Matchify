#!/usr/bin/env python3
"""
Contact parsing and matching: parse uploaded vCard/CSV files, extract phone numbers,
compare hashes against existing users in the in-memory graph.
"""
import csv
import hashlib
import io
import re

import graph_logic

try:
    import vobject
except ImportError:
    vobject = None

def process_upload(file):
    """
    Read a file (vCard or CSV), extract phone numbers, SHA256-hash them,
    and return a list of user_ids whose 'phoneHash' matches any hash.
    """
    data = file.read()
    try:
        text = data.decode('utf-8')
    except Exception:
        text = data.decode('latin-1', errors='ignore')

    phones = []
    fname = getattr(file, 'filename', '').lower()
    if fname.endswith('.vcf') and vobject:
        for vcard in vobject.readComponents(text):
            for tel in vcard.contents.get('tel', []):
                phones.append(tel.value)
    else:
        buf = io.StringIO(text)
        reader = csv.DictReader(buf)
        cols = [h for h in (reader.fieldnames or []) if 'phone' in h.lower()]
        for row in reader:
            for col in cols:
                val = row.get(col)
                if val:
                    phones.append(val)

    matches = []
    for raw in phones:
        num = re.sub(r"\D", "", raw)
        if not num:
            continue
        h = hashlib.sha256(num.encode('utf-8')).hexdigest()
        for node, attrs in graph_logic.G.nodes(data=True):
            if attrs.get('phoneHash') == h and node not in matches:
                matches.append(node)
    return matches

def request_intro(data):
    """
    Stub: start an introduction workflow. Accepts a dict with keys such as
    'from', 'to', 'via'. Returns a status dict.
    """
    # TODO: implement introduction logic
    return {'status': 'requested', **data}

def approve_intro(data):
    """
    Stub: approve one hop of an introduction. Returns a status dict.
    """
    # TODO: implement approval logic
    return {'status': 'approved', **data}

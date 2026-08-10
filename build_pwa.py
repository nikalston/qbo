#!/usr/bin/env python3
"""
Rebuild the Quality order PWA from items.csv.

Reads ../items.csv (or a path you pass in), injects the SKU list into
index.html between the ITEMS_START / ITEMS_END markers, and bumps the
service-worker cache name so phones pick up the change instead of
serving the old list forever.

Usage: python3 build_pwa.py [items.csv]
"""

import csv
import hashlib
import json
import os
import re
import sys
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))


def load(path):
    sections = OrderedDict()
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            sec = (row.get("section") or "").strip()
            item = (row.get("item") or "").strip()
            if not item:
                continue
            sections.setdefault(sec, []).append(item)
    return [{"name": k, "items": v} for k, v in sections.items()]


def main():
    csv_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "items.csv")
    if not os.path.exists(csv_path):
        csv_path = os.path.join(HERE, "items.csv")

    data = load(csv_path)
    n_items = sum(len(s["items"]) for s in data)
    blob = json.dumps(data, indent=2, ensure_ascii=False)

    # --- inject into index.html ---
    idx = os.path.join(HERE, "index.html")
    html = open(idx, encoding="utf-8").read()
    new_block = (
        "// ITEMS_START \u2014 regenerate with build_pwa.py, do not hand-edit between markers\n"
        f"const ITEMS = {blob};\n"
        "// ITEMS_END"
    )
    html, n = re.subn(
        r"// ITEMS_START.*?// ITEMS_END",
        lambda _: new_block,
        html,
        flags=re.S,
    )
    if n != 1:
        sys.exit("could not find the ITEMS_START / ITEMS_END markers in index.html")
    # --- bump version stamp ---
    ver_match = re.search(r"\$\('ver'\)\.textContent = 'v(\d+)';", html)
    ver = int(ver_match.group(1)) + 1 if ver_match else 1
    html = re.sub(
        r"// VERSION_STAMP.*?// VERSION_END",
        f"// VERSION_STAMP\n$('ver').textContent = 'v{ver}';\n// VERSION_END",
        html,
        flags=re.S,
    )

    open(idx, "w", encoding="utf-8").write(html)

    # --- bump the cache name (hash full HTML so any code change busts cache) ---
    stamp = hashlib.sha1(html.encode("utf-8")).hexdigest()[:8]
    swp = os.path.join(HERE, "sw.js")
    sw = open(swp, encoding="utf-8").read()
    sw = re.sub(r"const CACHE = '[^']*';", f"const CACHE = 'qbo-{stamp}';", sw, count=1)
    open(swp, "w", encoding="utf-8").write(sw)

    # --- XP theme variant ---
    xp_idx = os.path.join(HERE, "xp", "index.html")
    if os.path.exists(xp_idx):
        xp_html = open(xp_idx, encoding="utf-8").read()
        xp_html, xn = re.subn(
            r"// ITEMS_START.*?// ITEMS_END",
            lambda _: new_block,
            xp_html,
            flags=re.S,
        )
        if xn == 1:
            xp_ver_match = re.search(r"\$\('ver'\)\.textContent = 'v(\d+)';", xp_html)
            xp_ver = int(xp_ver_match.group(1)) + 1 if xp_ver_match else 1
            xp_html = re.sub(
                r"// VERSION_STAMP.*?// VERSION_END",
                f"// VERSION_STAMP\n$('ver').textContent = 'v{xp_ver}';\n// VERSION_END",
                xp_html,
                flags=re.S,
            )
            open(xp_idx, "w", encoding="utf-8").write(xp_html)

            xp_stamp = hashlib.sha1(xp_html.encode("utf-8")).hexdigest()[:8]
            xp_swp = os.path.join(HERE, "xp", "sw.js")
            if os.path.exists(xp_swp):
                xp_sw = open(xp_swp, encoding="utf-8").read()
                xp_sw = re.sub(r"const CACHE = '[^']*';", f"const CACHE = 'qbo-xp-{xp_stamp}';", xp_sw, count=1)
                open(xp_swp, "w", encoding="utf-8").write(xp_sw)
            print(f"  xp: cache qbo-xp-{xp_stamp}")

    print(f"built: {len(data)} sections, {n_items} SKUs, cache qbo-{stamp}")


if __name__ == "__main__":
    main()

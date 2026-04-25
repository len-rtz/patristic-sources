#!/usr/bin/env python3
"""
gen_psc_index.py
----------------
Generates psc_index.json from:
  - sources_catalogue.csv  (church_father, CF_ID, Bullinger_ID, work, language, source, editor)
  - church_fathers.csv     (CF_ID; bullinger_ID; Name; gnd_id; cc_id; class; ogl_id; pta_id)

Run from the directory containing both CSV files:
  python gen_psc_index.py

Output: output/graph/psc_index.json
"""

import csv
import json
import sys
from pathlib import Path

SOURCES_CSV = Path("sources_catalogue.csv")
FATHERS_CSV = Path("church_fathers.csv")
OUTPUT_JSON = Path("output/graph/psc_index.json")

# Load CC lookup if available
cc_lookup = {}
cc_path = Path("cc_url_lookup.csv")
if cc_path.exists():
    with open(cc_path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            cc_lookup[row["source_filename"]] = row["browser_url"]

# Then in parse_sources(), add to each work dict:
"source_url": cc_lookup.get(source) or scaife_url(source),

def scaife_url(source: str) -> str | None:
    name = source.replace(".xml", "")
    import re
    if re.match(r"tlg\d+\.tlg\d+\.", name):
        return f"https://scaife.perseus.org/reader/urn:cts:greekLit:{name}/"
    return None


def parse_fathers(path: Path) -> dict:
    print(f"  Parsing: {path}")
    fathers = {}
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            cf_id = row.get("CF_ID", "").strip().lower()
            if not cf_id:
                continue

            def val(key):
                v = row.get(key, "").strip()
                return v if v else None

            fathers[cf_id] = {
                "id":           cf_id,
                "name":         val("Name"),
                "bullinger_id": val("bullinger_ID"),
                "gnd_id":       val("gnd_id"),
                "cc_id":        val("cc_id"),
                "class":        val("class"),
                "ogl_id":       val("ogl_id"),
                "pta_id":       val("pta_id"),
                "works":        [],
            }
    print(f"  Found {len(fathers)} church fathers")
    return fathers


def parse_sources(path: Path, fathers: dict):
    print(f"  Parsing: {path}")
    works_added = 0
    unknown = set()

    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cf_id = row.get("CF_ID", "").strip().lower()
            if not cf_id:
                continue

            if cf_id not in fathers:
                unknown.add(cf_id)
                fathers[cf_id] = {
                    "id":           cf_id,
                    "name":         row.get("church_father", "").strip(),
                    "bullinger_id": row.get("Bullinger_ID", "").strip() or None,
                    "gnd_id":       None,
                    "cc_id":        None,
                    "class":        None,
                    "ogl_id":       None,
                    "pta_id":       None,
                    "works":        [],
                }

            source  = row.get("source", "").strip()
            work_id = source[:-4] if source.endswith(".xml") else source

            fathers[cf_id]["works"].append({
                "work_id":  work_id,
                "title":    row.get("work",     "").strip(),
                "language": row.get("language", "").strip() or None,
                "source":   source,
                "editor":   row.get("editor",   "").strip() or None,
            })
            works_added += 1

    if unknown:
        print(f"  [WARN] CF_IDs in sources but not in fathers CSV: {unknown}")
    print(f"  Added {works_added} works")


def main():
    for path in [SOURCES_CSV, FATHERS_CSV]:
        if not path.exists():
            sys.exit(f"[ERROR] File not found: {path}")

    print("[1/2] Parsing church_fathers.csv...")
    fathers = parse_fathers(FATHERS_CSV)

    print("[2/2] Parsing sources_catalogue.csv...")
    parse_sources(SOURCES_CSV, fathers)

    result = {"fathers": sorted(fathers.values(), key=lambda f: f["id"])}

    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    size_kb = OUTPUT_JSON.stat().st_size / 1024
    n_works = sum(len(f["works"]) for f in result["fathers"])
    print(f"\n✓  {OUTPUT_JSON} ({size_kb:.1f} KB)")
    print(f"   {len(result['fathers'])} fathers, {n_works} works")


if __name__ == "__main__":
    main()
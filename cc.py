#!/usr/bin/env python3
"""
gen_cc_urls.py
--------------
Re-queries the Corpus Corporum navigate API to reconstruct
filename → browser URL mappings for all CC authors.

Output: cc_url_lookup.csv  (source_filename, browser_url)
"""

import os
import time
import csv
import requests
import xml.etree.ElementTree as ET
import pandas as pd
from pathlib import Path

CSV_PATH = "church-fathers.csv"
OUTPUT   = "cc_url_lookup.csv"
BASE_API = "https://mlat.uzh.ch/php_modules/navigate.php?load="
BASE_HOST = "https://mlat.uzh.ch"
NS = {"cc": "http://mlat.uzh.ch/2.0"}

session = requests.Session()
session.headers.update({"User-Agent": "tei-url-mapper/1.0"})

def fetch_xml_root(url):
    r = session.get(url, timeout=20)
    r.raise_for_status()
    return ET.fromstring(r.content)

def normalize_xml_path_to_url(xml_path_text):
    s = xml_path_text.strip()
    idx = s.find("/data/")
    if idx != -1:
        return BASE_HOST + s[idx:]
    if s.startswith("/var/www/html"):
        idx2 = s.find("/data/")
        if idx2 != -1:
            return BASE_HOST + s[idx2:]
    if s.startswith("/data"):
        return BASE_HOST + s
    return BASE_HOST + "/" + s.lstrip("/")

def browser_url(author_id, work_id, text_id=None):
    path = f"{author_id}/{work_id}"
    if text_id:
        path += f"/{text_id}"
    return f"{BASE_HOST}/browser?path={path}"

def get_works(author_id):
    root = fetch_xml_root(f"{BASE_API}{author_id}&group_by=")
    works = []
    for w in root.findall(".//cc:work", NS):
        wid  = w.findtext("cc:idno",    default="", namespaces=NS).strip()
        if wid:
            works.append(wid)
    return works

def get_texts(author_id, work_id):
    root = fetch_xml_root(f"{BASE_API}{author_id}/{work_id}&group_by=")
    texts = []
    for t in root.findall(".//cc:contents/cc:text", NS):
        tid = t.findtext("cc:idno", default="", namespaces=NS).strip()
        if tid:
            texts.append(tid)
    return texts

def get_filename_and_url(author_id, work_id, text_id=""):
    url = f"{BASE_API}{author_id}/{work_id}"
    if text_id:
        url += f"/{text_id}"
    url += "&group_by="
    root = fetch_xml_root(url)

    xml_path_elem    = root.find(".//cc:xml_file_path", NS)
    downloadable_el  = root.find(".//cc:xml_file_downloadable", NS)
    downloadable     = True
    if downloadable_el is not None and downloadable_el.text:
        downloadable = downloadable_el.text.strip().lower() == "true"

    if xml_path_elem is None or not xml_path_elem.text or not downloadable:
        return None, None

    file_url  = normalize_xml_path_to_url(xml_path_elem.text)
    filename  = os.path.basename(file_url)
    burl      = browser_url(author_id, work_id, text_id or None)
    return filename, burl

def main():
    df = pd.read_csv(CSV_PATH, sep=";", encoding="utf-8")
    df_cc = df[df["cc_id"].notna() & df["CF_ID"].notna()].copy()
    print(f"Processing {len(df_cc)} authors with CC IDs")

    rows = []
    for _, row in df_cc.iterrows():
        author_id = str(int(float(row["cc_id"])))
        print(f"\nAuthor: {row['Name']} (cc_id={author_id})")
        try:
            works = get_works(author_id)
        except Exception as e:
            print(f"  Failed to get works: {e}")
            continue

        for wid in works:
            try:
                texts = get_texts(author_id, wid)
            except Exception as e:
                print(f"  Failed to get texts for work {wid}: {e}")
                continue

            if not texts:
                try:
                    fname, burl = get_filename_and_url(author_id, wid)
                    if fname and burl:
                        rows.append({"source_filename": fname, "browser_url": burl})
                        print(f"  {fname} → {burl}")
                except Exception as e:
                    print(f"  Failed: {e}")
            else:
                for tid in texts:
                    try:
                        fname, burl = get_filename_and_url(author_id, wid, tid)
                        if fname and burl:
                            rows.append({"source_filename": fname, "browser_url": burl})
                            print(f"  {fname} → {burl}")
                        time.sleep(0.15)
                    except Exception as e:
                        print(f"  Failed text {tid}: {e}")
            time.sleep(0.15)
        time.sleep(0.5)

    with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["source_filename", "browser_url"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n✓ Written {len(rows)} mappings to {OUTPUT}")

if __name__ == "__main__":
    main()
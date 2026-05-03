#!/usr/bin/env python3
"""Convert JSON datasets (lexicon, corpus, attestations) into a single SQLite DB.

Usage:
  python3 pipeline/export/json_to_sqlite.py --lexicon data/lexicon.json --corpus data/corpus.json --attestations data/attestations.json --output data/puo_gold_migrated.db

Note: This simple converter loads JSON into memory. For very large files, consider using ijson for streaming.
"""
import argparse
import json
import sqlite3
from pathlib import Path
import sys


def create_tables(conn):
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS lexicon (
        entry_id TEXT PRIMARY KEY,
        entry_json TEXT NOT NULL
    );""")
    cur.execute("""CREATE TABLE IF NOT EXISTS corpus (
        corpus_id TEXT PRIMARY KEY,
        source TEXT,
        ref TEXT,
        sesotho_text TEXT,
        english_text TEXT,
        corpus_json TEXT
    );""")
    cur.execute("""CREATE TABLE IF NOT EXISTS attestations (
        attestation_id TEXT PRIMARY KEY,
        sense_id TEXT,
        corpus_id TEXT,
        match_terms TEXT,
        score REAL,
        method TEXT,
        attestation_json TEXT
    );""")
    conn.commit()


def load_json(path):
    p = Path(path)
    if not p.exists():
        print(f"Skipping missing file: {path}")
        return None
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def insert_lexicon(conn, items):
    cur = conn.cursor()
    count = 0
    for item in items:
        entry_id = item.get("entry_id") or item.get("id")
        if not entry_id:
            # generate as fallback
            continue
        cur.execute("INSERT OR REPLACE INTO lexicon (entry_id, entry_json) VALUES (?, ?)",
                    (entry_id, json.dumps(item, ensure_ascii=False)))
        count += 1
    conn.commit()
    return count


def insert_corpus(conn, items):
    cur = conn.cursor()
    count = 0
    for item in items:
        corpus_id = item.get("corpus_id") or item.get("id")
        if not corpus_id:
            continue
        source = item.get("source")
        ref = item.get("ref")
        sesotho = item.get("sesotho_text") or item.get("sesotho") or item.get("content_st")
        english = item.get("english_text") or item.get("english") or item.get("content_en")
        cur.execute("INSERT OR REPLACE INTO corpus (corpus_id, source, ref, sesotho_text, english_text, corpus_json) VALUES (?, ?, ?, ?, ?, ?)",
                    (corpus_id, source, ref, sesotho, english, json.dumps(item, ensure_ascii=False)))
        count += 1
    conn.commit()
    return count


def insert_attestations(conn, items):
    cur = conn.cursor()
    count = 0
    for item in items:
        att_id = item.get("attestation_id") or item.get("id")
        if not att_id:
            continue
        sense_id = item.get("sense_id")
        corpus_id = item.get("corpus_id")
        match_terms = json.dumps(item.get("match_terms") or [])
        score = item.get("score")
        method = item.get("method")
        cur.execute("INSERT OR REPLACE INTO attestations (attestation_id, sense_id, corpus_id, match_terms, score, method, attestation_json) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (att_id, sense_id, corpus_id, match_terms, score, method, json.dumps(item, ensure_ascii=False)))
        count += 1
    conn.commit()
    return count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lexicon", default="data/lexicon.json")
    parser.add_argument("--corpus", default="data/corpus.json")
    parser.add_argument("--attestations", default="data/attestations.json")
    parser.add_argument("--output", default="data/puo_gold_migrated.db")
    parser.add_argument("--force", action="store_true", help="Overwrite existing DB")
    args = parser.parse_args()

    outp = Path(args.output)
    if outp.exists() and not args.force:
        print(f"Output DB {outp} exists. Use --force to overwrite.")
        sys.exit(1)

    data = {}
    print("Loading lexicon...", end=" ")
    lex = load_json(args.lexicon)
    print("done" if lex is not None else "skipped")

    print("Loading corpus...", end=" ")
    corpus = load_json(args.corpus)
    print("done" if corpus is not None else "skipped")

    print("Loading attestations...", end=" ")
    att = load_json(args.attestations)
    print("done" if att is not None else "skipped")

    conn = sqlite3.connect(str(outp))
    create_tables(conn)

    if lex:
        print(f"Inserting {len(lex)} lexicon records...")
        n1 = insert_lexicon(conn, lex)
        print(f"Inserted {n1}")
    if corpus:
        print(f"Inserting {len(corpus)} corpus records...")
        n2 = insert_corpus(conn, corpus)
        print(f"Inserted {n2}")
    if att:
        print(f"Inserting {len(att)} attestation records...")
        n3 = insert_attestations(conn, att)
        print(f"Inserted {n3}")

    conn.close()
    print(f"Migration complete. DB at: {outp}")


if __name__ == "__main__":
    main()

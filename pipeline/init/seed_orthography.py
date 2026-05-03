#!/usr/bin/env python3
"""Seed orthography mappings into existing pems_core.db from JSON file with upsert behavior.
Usage: python3 pipeline/init/seed_orthography.py --db data/pems_core.db --seeds data/pems_orthography_seeds.json
"""
import argparse
import json
import sqlite3
from pathlib import Path


def seed_orthography(db_path: str, json_seeds: str, provenance='morija_1906') -> int:
    p = Path(db_path)
    if not p.exists():
        raise SystemExit(f"DB not found at {db_path}")
    conn = sqlite3.connect(str(p))
    cur = conn.cursor()

    # Ensure provenance exists
    cur.execute('INSERT OR IGNORE INTO provenance (source_id, author, publication_year, region, reliability_score) VALUES (?, ?, ?, ?, ?)',
                (provenance, 'Mabille & Dieterlen', 1906, 'Lesotho', 1.0))

    # Ensure columns for provenance_source and description exist
    cur.execute("PRAGMA table_info('orthography_mappings')")
    existing_cols = [r[1] for r in cur.fetchall()]
    if 'provenance_source' not in existing_cols:
        cur.execute("ALTER TABLE orthography_mappings ADD COLUMN provenance_source TEXT")
    if 'description' not in existing_cols:
        cur.execute("ALTER TABLE orthography_mappings ADD COLUMN description TEXT")

    # Read seeds
    s = Path(json_seeds)
    if not s.exists():
        raise SystemExit(f"Seeds file not found: {json_seeds}")
    with s.open('r', encoding='utf-8') as f:
        seeds = json.load(f)

    inserted = 0
    for seed in seeds:
        pattern = seed.get('pattern')
        replacement = seed.get('replacement')
        scope = seed.get('scope')
        priority = int(seed.get('priority', 100))
        description = seed.get('description')
        prov = seed.get('provenance_source', provenance)
        if not pattern or replacement is None:
            continue
        # Check existing by pattern+scope
        cur.execute('SELECT id FROM orthography_mappings WHERE pattern = ? AND scope = ?', (pattern, scope))
        row = cur.fetchone()
        if row:
            cur.execute('''UPDATE orthography_mappings SET replacement = ?, priority = ?, provenance_source = ?, description = ? WHERE id = ?''',
                        (replacement, priority, prov, description, row[0]))
        else:
            cur.execute('''INSERT INTO orthography_mappings (pattern, replacement, scope, priority, provenance_source, description) VALUES (?, ?, ?, ?, ?, ?)''',
                        (pattern, replacement, scope, priority, prov, description))
            inserted += 1

    conn.commit()
    conn.close()
    return inserted


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', default='data/pems_core.db')
    parser.add_argument('--seeds', default='data/pems_orthography_seeds.json')
    parser.add_argument('--provenance', default='morija_1906')
    args = parser.parse_args()
    n = seed_orthography(args.db, args.seeds, provenance=args.provenance)
    print(f"Inserted {n} new orthography mappings into {args.db}")

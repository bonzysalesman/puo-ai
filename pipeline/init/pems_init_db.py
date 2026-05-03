#!/usr/bin/env python3
"""Initialize pems_core.db with refined schema and seed initial noun class concords.
Usage: python3 pipeline/init/pems_init_db.py --output data/pems_core.db --force
"""
import argparse
import sqlite3
from pathlib import Path

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS provenance (
    source_id TEXT PRIMARY KEY,
    author TEXT,
    publication_year INTEGER,
    region TEXT,
    reliability_score REAL
);

CREATE TABLE IF NOT EXISTS noun_class_concords (
    class_id INTEGER PRIMARY KEY,
    class_name TEXT,
    prefix TEXT,
    subj_concord TEXT,
    obj_concord TEXT,
    possessive TEXT,
    relative TEXT,
    adj_concord TEXT,
    nasal_context BOOLEAN,
    strict_enforcement BOOLEAN DEFAULT 1
);

CREATE TABLE IF NOT EXISTS orthography_mappings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern TEXT NOT NULL,
    replacement TEXT NOT NULL,
    scope TEXT,
    priority INTEGER DEFAULT 100
);

CREATE TABLE IF NOT EXISTS morphology (
    root_id TEXT PRIMARY KEY,
    root_atom TEXT UNIQUE NOT NULL,
    semantic_domain TEXT,
    rehabilitation_notes TEXT
);

CREATE TABLE IF NOT EXISTS lexicon (
    entry_id TEXT PRIMARY KEY,
    headword_st TEXT UNIQUE,
    headword_en TEXT,
    senses_json TEXT,
    provenance_source TEXT,
    FOREIGN KEY (provenance_source) REFERENCES provenance(source_id)
);

CREATE TABLE IF NOT EXISTS morphological_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    context TEXT NOT NULL,
    input_char TEXT NOT NULL,
    output_char TEXT NOT NULL,
    description TEXT,
    provenance_source TEXT,
    FOREIGN KEY (provenance_source) REFERENCES provenance(source_id)
);

CREATE TABLE IF NOT EXISTS noun_class_lexicon (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    term TEXT UNIQUE NOT NULL,
    class_id INTEGER NOT NULL,
    FOREIGN KEY (class_id) REFERENCES noun_class_concords(class_id)
);

CREATE INDEX IF NOT EXISTS idx_noun_class_id ON noun_class_concords(class_id);
CREATE INDEX IF NOT EXISTS idx_orthography_priority ON orthography_mappings(priority);
CREATE INDEX IF NOT EXISTS idx_morphology_context ON morphological_rules(context);
CREATE INDEX IF NOT EXISTS idx_noun_lexicon ON noun_class_lexicon(term);
"""

SEED_NOUN_CLASSES = [
    (1, 'Personal Singular', 'mo-', 'o', 'mo', 'oa', 'ea', 'e mo-', 0),
    (2, 'Personal Plural', 'ba-', 'ba', 'ba', 'ba', 'ba', 'ba ba-', 0),
    (7, 'Instrumental/Language', 'se-', 'se', 'se', 'sa', 'se', 'se se-', 0),
    (9, 'Animal/Object Singular', 'n-', 'e', 'e', 'ea', 'e', 'e n-', 1),
]

def init_db(path, force=False):
    p = Path(path)
    if p.exists() and not force:
        print(f"DB {path} exists. Use --force to overwrite or inspect existing DB.")
        return
    if p.exists() and force:
        p.unlink()

    conn = sqlite3.connect(str(p))
    cur = conn.cursor()
    cur.executescript(SCHEMA_SQL)

    # Seed provenance example (Morija 1906)
    cur.execute('INSERT OR IGNORE INTO provenance (source_id, author, publication_year, region, reliability_score) VALUES (?, ?, ?, ?, ?)',
                ('morija_1906', 'Mabille & Dieterlen', 1906, 'Lesotho', 1.0))

    # Seed noun class concords
    for row in SEED_NOUN_CLASSES:
        cur.execute('''INSERT OR REPLACE INTO noun_class_concords (class_id, class_name, prefix, subj_concord, obj_concord, possessive, relative, adj_concord, nasal_context, strict_enforcement)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)''', row)

    # Load orthography seeds from JSON if available, else use example seeds
    seeds_path = Path('data/pems_orthography_seeds.json')
    # Ensure orthography_mappings has a provenance_source column (backwards-compatible)
    cur.execute("PRAGMA table_info('orthography_mappings')")
    cols = [r[1] for r in cur.fetchall()]
    if 'provenance_source' not in cols:
        cur.execute("ALTER TABLE orthography_mappings ADD COLUMN provenance_source TEXT")

    if seeds_path.exists():
        import json

        with seeds_path.open('r', encoding='utf-8') as sf:
            try:
                seeds = json.load(sf)
            except Exception:
                seeds = []
        for s in seeds:
            pattern = s.get('pattern')
            replacement = s.get('replacement')
            scope = s.get('scope')
            priority = s.get('priority', 100)
            prov = s.get('provenance_source', 'morija_1906')
            if pattern and replacement:
                cur.execute('INSERT INTO orthography_mappings (pattern, replacement, scope, priority, provenance_source) VALUES (?, ?, ?, ?, ?)',
                            (pattern, replacement, scope, priority, prov))
    else:
        orth_seeds = [
            ('tjh', 'ch', 'consonant', 10),
            ('ya', 'ea', 'vowel_glide', 20),
        ]
        for pattern, replacement, scope, priority in orth_seeds:
            cur.execute('INSERT INTO orthography_mappings (pattern, replacement, scope, priority) VALUES (?, ?, ?, ?)',
                        (pattern, replacement, scope, priority))

    # Create unique index to prevent duplicate orthography mappings per provenance
    cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_ortho_pattern_prov ON orthography_mappings (pattern, provenance_source);")

    conn.commit()
    conn.close()
    print(f"Initialized DB at {path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='data/pems_core.db')
    parser.add_argument('--force', action='store_true')
    args = parser.parse_args()
    init_db(args.output, force=args.force)

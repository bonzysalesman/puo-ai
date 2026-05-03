import json
import sqlite3
import argparse


def seed_exceptions(db_path: str, json_file: str, provenance_id: str = None):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    # Create table if missing
    cur.execute('''
    CREATE TABLE IF NOT EXISTS exceptions_registry (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        term TEXT UNIQUE NOT NULL,
        category TEXT DEFAULT 'loanword',
        provenance_id TEXT,
        added_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (provenance_id) REFERENCES provenance(source_id)
    );
    ''')
    cur.execute('CREATE INDEX IF NOT EXISTS idx_exception_term ON exceptions_registry (term);')

    with open(json_file, 'r') as fh:
        items = json.load(fh)
        for it in items:
            term = it.get('term')
            cat = it.get('category', 'loanword')
            prov = provenance_id or it.get('provenance_id')
            if term:
                cur.execute('INSERT OR REPLACE INTO exceptions_registry (term, category, provenance_id) VALUES (?, ?, ?)', (term.lower(), cat, prov))

    conn.commit()
    conn.close()
    print(f"Seeded {len(items)} exceptions into {db_path}")


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--db', default='data/pems_core.db')
    p.add_argument('--json', default='data/pems_exceptions.json')
    p.add_argument('--provenance', default=None)
    args = p.parse_args()
    seed_exceptions(args.db, args.json, args.provenance)

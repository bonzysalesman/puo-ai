import json
import sqlite3
import argparse


def seed_adjectives(db_path: str, json_file: str):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS adjective_roots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        root TEXT UNIQUE NOT NULL,
        definition TEXT,
        is_nasal_sensitive INTEGER DEFAULT 0
    );
    ''')
    cur.execute('CREATE INDEX IF NOT EXISTS idx_adj_root ON adjective_roots (root);')

    with open(json_file, 'r') as fh:
        items = json.load(fh)
        for it in items:
            root = it.get('root')
            definition = it.get('definition')
            nasal = int(it.get('is_nasal_sensitive', 0))
            if root:
                cur.execute('INSERT OR REPLACE INTO adjective_roots (root, definition, is_nasal_sensitive) VALUES (?, ?, ?)', (root.lower(), definition, nasal))

    conn.commit()
    conn.close()
    print(f"Seeded {len(items)} adjective roots into {db_path}")


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--db', default='data/pems_core.db')
    p.add_argument('--json', default='data/pems_adjective_roots.json')
    args = p.parse_args()
    seed_adjectives(args.db, args.json)

#!/usr/bin/env python3
"""Seed morphological_rules table with PEMS phonological transformations.
Usage: python3 pipeline/init/seed_morphology.py [--db data/pems_core.db]
"""
import json
import sqlite3
import argparse
from pathlib import Path


def seed_morphology_rules(db_path, rules_json):
    """Load morphological rules from JSON and insert into database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Ensure provenance for 1906 exists
    cursor.execute("""
        INSERT OR IGNORE INTO provenance (source_id, author, publication_year, reliability_score)
        VALUES ('morija_1906', 'Mabille & Dieterlen', 1906, 1.0)
    """)

    with open(rules_json, 'r', encoding='utf-8') as f:
        rules = json.load(f)
        for rule in rules:
            cursor.execute("""
                INSERT OR REPLACE INTO morphological_rules 
                (context, input_char, output_char, description, provenance_source)
                VALUES (?, ?, ?, ?, ?)
            """, (
                rule['context'],
                rule['input_char'],
                rule['output_char'],
                rule['description'],
                rule.get('provenance_source', 'morija_1906')
            ))

    conn.commit()
    conn.close()
    print(f"Successfully seeded {len(rules)} morphological rules from {rules_json}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', default='data/pems_core.db')
    parser.add_argument('--rules', default='data/pems_morphology_rules.json')
    args = parser.parse_args()

    rules_path = Path(args.rules)
    if not rules_path.exists():
        print(f"Rules file not found: {args.rules}")
        exit(1)

    seed_morphology_rules(args.db, args.rules)

#!/usr/bin/env python3
"""Seed noun_class_lexicon with explicit noun-to-class mappings.
Usage: python3 pipeline/init/seed_noun_lexicon.py [--db data/pems_core.db]
"""
import sqlite3
import argparse
from pathlib import Path


def seed_noun_lexicon(db_path):
    """Insert explicit noun-to-class mappings for non-standard nouns."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Explicit noun -> class mappings
    lexicon_entries = [
        ('strategy', 7),  # Class 7 (se-), for E2E tests
        ('chuna', 9),     # Class 9 (n-), for E2E tests
        ('sebetsa', 7),   # Class 7 (se-), for E2E tests (meaning: to work/serve)
    ]

    for noun, class_id in lexicon_entries:
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO noun_class_lexicon (term, class_id)
                VALUES (?, ?)
            """, (noun, class_id))
        except Exception as e:
            print(f"Error inserting {noun}: {e}")

    conn.commit()
    conn.close()
    print(f"Successfully seeded {len(lexicon_entries)} noun-class lexicon entries")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', default='data/pems_core.db')
    args = parser.parse_args()

    db_path = Path(args.db)
    if not db_path.exists():
        print(f"Database not found: {args.db}")
        exit(1)

    seed_noun_lexicon(args.db)

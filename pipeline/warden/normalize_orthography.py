#!/usr/bin/env python3
"""Warden normalization tool: apply orthography_mappings from pems_core.db
This is a lightweight first-pass implementation that respects mapping priorities.
"""
import sqlite3
import re
from pathlib import Path
from typing import List, Tuple
from pipeline.warden.protector import Protector


class Warden:
    def __init__(self, db_path: str = 'data/pems_core.db'):
        self.db_path = db_path
        self.protector = Protector(self.db_path)
        self.mappings = self.load_mappings()

    def load_mappings(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute('SELECT pattern, replacement, scope, priority FROM orthography_mappings ORDER BY priority ASC, id ASC')
        rows = cur.fetchall()
        conn.close()
        # return list of dicts for richer behavior
        mappings = []
        for r in rows:
            if not r:
                continue
            mappings.append({'pattern': r[0], 'replacement': r[1], 'scope': r[2], 'priority': r[3]})
        return mappings

    def apply_mappings(self, text: str) -> str:
        out = text
        for m in self.mappings:
            pattern = m.get('pattern')
            replacement = m.get('replacement')
            scope = (m.get('scope') or '').lower()
            # special-case: single-letter consonant mappings (e.g., 'g'->'h') should only apply before vowels
            try:
                if scope == 'consonant' and len(pattern) == 1:
                    regex = re.compile(re.escape(pattern) + r'(?=[aeiouAEIOU])', flags=re.IGNORECASE)
                else:
                    regex = re.compile(re.escape(pattern), flags=re.IGNORECASE)
                out = regex.sub(replacement, out)
            except re.error:
                # fallback to literal replace
                out = re.sub(re.escape(pattern), replacement, out, flags=re.IGNORECASE)
        return out

    def normalize(self, text: str, clusters=None):
        # default anchors and PEMS protect list
        anchors = ['tjh', 'ny', 'ng']
        pems_list = ['tš', 'š']
        clusters = clusters or anchors

        # Protector: mask exceptions (Immunity tokens)
        protected_text, imm_map = self.protector.protect(text)

        # Step 1: protect anchors on the already-protected text
        protect_func = __import__('pipeline.core.naked_parser', fromlist=['protect_clusters']).protect_clusters
        protected, pm = protect_func(protected_text, clusters)

        # Build map from original cluster -> placeholder for selective replacements
        ph_to_orig = {ph: orig for (ph, orig) in pm}
        orig_to_ph = {orig: ph for (ph, orig) in pm}

        # Step 2: apply mappings while anchors are protected to avoid collisions,
        # but record any anchor-specific replacements without restoring placeholders yet.
        mapped = protected
        ph_replacements = {}
        for m in self.mappings:
            pattern = m.get('pattern')
            replacement = m.get('replacement')
            if pattern in orig_to_ph:
                # record that this placeholder should become 'replacement' later
                ph = orig_to_ph[pattern]
                ph_replacements[ph] = replacement
            else:
                mapped = re.sub(re.escape(pattern), replacement, mapped, flags=re.IGNORECASE)

        # After all mappings applied, restore placeholders to their intended replacement (or original)
        for ph, orig in pm:
            repl = ph_replacements.get(ph, orig)
            mapped = mapped.replace(ph, repl)

        # Step 3: protect any PEMS chars introduced by mapping (e.g., 'š','tš')
        from pipeline.core.naked_parser import protect_clusters as protect2, strip_diacritics, restore_clusters
        mapped_protected, pm2 = protect2(mapped, pems_list)

        # Step 4: strip diacritics
        stripped = strip_diacritics(mapped_protected)

        # Step 5: restore PEMS placeholders and original anchors
        restored_pm2 = restore_clusters(stripped, pm2)
        restored = restore_clusters(restored_pm2, pm)

        # Finally restore immunity tokens back to original exception terms
        restored = self.protector.restore(restored, imm_map)

        return restored


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', default='data/pems_core.db')
    parser.add_argument('--text', default=None)
    parser.add_argument('--clusters', default='tjh,ya')
    args = parser.parse_args()

    w = Warden(db_path=args.db)
    if args.text:
        t0 = args.text
    else:
        t0 = 'Sample: tjhā ya ö'
    clusters = [c.strip() for c in args.clusters.split(',') if c.strip()]
    print(w.normalize(t0, clusters=clusters))

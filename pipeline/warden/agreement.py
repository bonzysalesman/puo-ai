from typing import Optional
from pipeline.core.noun_class import NounClassDB
from pipeline.core.naked_parser import strip_diacritics
from pipeline.core.architect import MorphologicalArchitect
import re
import sqlite3


class AgreementEngine:
    """Enforce simple noun class agreement rules using noun_class_concords.

    Includes possessive and adjectival (double-concord) correction.
    Integrates MorphologicalArchitect for nasal and other morphological transformations.
    """

    def __init__(self, db_path: str = 'data/pems_core.db'):
        self.db = NounClassDB(db_path=db_path)
        self.architect = MorphologicalArchitect(db_path=db_path)
        self._load_adjective_roots()

    def _load_adjective_roots(self):
        conn = sqlite3.connect(self.db.db_path)
        cur = conn.cursor()
        try:
            cur.execute('SELECT root, is_nasal_sensitive FROM adjective_roots')
            rows = cur.fetchall()
        except Exception:
            rows = []
        conn.close()
        # store metadata for adjective roots
        self.adj_roots = []
        self.adj_meta = {}
        for r in rows:
            root = r[0]
            nasal = bool(r[1]) if len(r) > 1 else False
            if root:
                self.adj_roots.append(root)
                self.adj_meta[root] = {'is_nasal_sensitive': nasal}
        # sort by length desc for longest-first matching
        self.adj_roots.sort(key=lambda x: len(x), reverse=True)
        # container for mutation zones discovered during a pass
        self.mutation_zones = []

    def _preserve_case(self, original: str, new: str) -> str:
        if original.istitle():
            return new.capitalize()
        if original.isupper():
            return new.upper()
        return new

    def apply_possessive_agreement(self, phrase: str) -> str:
        """Detect pattern: <noun> <possessive> ... and correct possessive according to noun class."""
        if not phrase or not phrase.strip():
            return phrase
        tokens = phrase.split()
        if len(tokens) < 2:
            return phrase

        # build set of known possessives
        all_possessives = self.db.all_possessives

        # scan tokens to find noun + possessive patterns anywhere
        for i in range(len(tokens) - 1):
            noun = tokens[i]
            poss = tokens[i + 1]
            noun_lookup = strip_diacritics(noun)
            cls = self.db.get_by_prefix(noun_lookup)
            if not cls:
                continue
            expected = (cls.get('possessive') or '').strip()
            if not expected:
                continue
            if poss.lower() in all_possessives and poss.lower() != expected.lower():
                corrected = self._preserve_case(poss, expected)
                tokens[i + 1] = corrected
                return ' '.join(tokens)
        return phrase

    def apply_adjective_agreement(self, phrase: str) -> str:
        """Apply double-concord (relative + adjectival concord) corrections.

        Heuristics:
        - If noun is followed by an adjective root token (e.g., 'motle' ending with 'tle'),
          insert expected relative and adjust adjectival concord prefix.
        - If noun is followed by relative + adjective, ensure both relative and adjective prefix match the noun class.
        """
        if not phrase or not phrase.strip():
            return phrase
        tokens = phrase.split()
        changed = False
        i = 0
        # prepare known relative tokens across classes for detection
        all_relatives = set()
        for c in self.db.classes.values():
            rel = c.get('subj_concord')
            if rel:
                all_relatives.add(rel.lower())

        while i < len(tokens):
            noun = tokens[i]
            noun_lookup = strip_diacritics(noun)
            cls = self.db.get_by_prefix(noun_lookup)
            if not cls:
                i += 1
                continue

            # use subj_concord as the relative particle (matches expected usage)
            expected_rel = (cls.get('subj_concord') or '').strip()
            expected_adj = (cls.get('adj_concord') or '').strip()
            # extract adjectival prefix token (prefer the token containing '-')
            tokens_adj = expected_adj.split()
            adj_token = None
            for t in reversed(tokens_adj):
                if '-' in t:
                    adj_token = t
                    break
            if not adj_token:
                adj_token = tokens_adj[-1] if tokens_adj else expected_adj
            expected_adj_prefix = adj_token.replace('-', '').strip().lower()
            expected_rel_norm = expected_rel.lower()

            # Scan ahead up to 5 tokens to find an adjective root occurrence
            found = False
            max_scan = min(len(tokens), i + 6)
            for j in range(i + 1, max_scan):
                tok_j = tokens[j]
                adj_root_match = None
                for root in self.adj_roots:
                    if tok_j.lower().endswith(root):
                        adj_root_match = root
                        break
                if not adj_root_match:
                    continue

                # We found an adjective occurrence at j
                found = True
                root = adj_root_match
                is_nasal = self.adj_meta.get(root, {}).get('is_nasal_sensitive', False)
                
                # Apply morphological mutation if nasal context + nasal-sensitive root
                transformed_root = root
                if cls.get('nasal_context') and is_nasal:
                    self.mutation_zones.append({'noun': noun, 'root': root, 'class_id': cls.get('class_id')})
                    print(f"Nasal mutation zone: noun={noun} class={cls.get('class_id')} root={root}")
                    # Call Architect to apply transformation
                    transformed_root = self.architect.mutate(root, context='nasal')
                    print(f"  Transformed: {root} -> {transformed_root}")

                # Determine if there is an explicit relative immediately before adjective
                prev_index = j - 1
                if prev_index >= i + 1 and tokens[prev_index].lower() in all_relatives:
                    # replace existing relative with expected and replace adjective
                    tokens[prev_index] = self._preserve_case(tokens[prev_index], expected_rel)
                    tokens[j] = self._preserve_case(tokens[j], expected_adj_prefix + transformed_root)
                else:
                    # insert expected relative before j and replace adjective at j (shifted)
                    tokens[j] = self._preserve_case(tokens[j], expected_adj_prefix + transformed_root)
                    tokens.insert(j, self._preserve_case(tokens[j], expected_rel))

                changed = True
                # move i forward past the handled tokens
                i = j + 1
                break

            if found:
                continue

            i += 1

        if changed:
            return ' '.join(tokens)
        return phrase

    def apply_subject_agreement(self, phrase: str) -> str:
        """Adjust subject concords (e.g., 'o'/'oa' -> 'e'/'ea') following noun anchor."""
        tokens = phrase.split()
        for i in range(len(tokens)):
            noun = tokens[i]
            noun_lookup = strip_diacritics(noun)
            cls = self.db.get_by_prefix(noun_lookup)
            if not cls:
                continue
            expected_subj = (cls.get('subj_concord') or '').strip()
            if not expected_subj:
                continue
            # look ahead for subjects (e.g., 'o', 'oa') within next 3 tokens
            for j in range(i+1, min(len(tokens), i+4)):
                tok = tokens[j]
                m = re.match(r'^(o)(.*)$', tok, flags=re.IGNORECASE)
                if m:
                    suffix = m.group(2)
                    newtok = expected_subj + suffix
                    tokens[j] = self._preserve_case(tok, newtok)
                    return ' '.join(tokens)
        return phrase

    def apply_all_agreement(self, phrase: str) -> str:
        # run possessive then adjective passes
        out = self.apply_possessive_agreement(phrase)
        out = self.apply_adjective_agreement(out)
        out = self.apply_subject_agreement(out)
        return out

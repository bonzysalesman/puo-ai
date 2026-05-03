import sqlite3
from functools import lru_cache
from typing import Optional, Dict, List


class NounClassDB:
    """Simple accessor for noun_class_concords table providing prefix-based lookup.

    Assumes table noun_class_concords exists with columns:
      class_id, class_name, prefix, subj_concord, obj_concord, possessive, relative, adj_concord, nasal_context
    """

    def __init__(self, db_path: str = 'data/pems_core.db'):
        self.db_path = db_path
        self._load()

    def _load(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        try:
            cur.execute('SELECT class_id, class_name, prefix, subj_concord, obj_concord, possessive, relative, adj_concord, nasal_context FROM noun_class_concords')
            rows = cur.fetchall()
        except sqlite3.Error:
            rows = []
        conn.close()

        self.classes: Dict[int, Dict] = {}
        self.prefix_map: List[Dict] = []  # list of {prefix_norm, class_id}
        for r in rows:
            if not r:
                continue
            class_id = r[0]
            class_name = r[1]
            prefix = r[2] or ''
            # normalize prefix (remove trailing hyphen if present)
            prefix_norm = prefix.replace('-', '').lower()
            self.classes[class_id] = {
                'class_id': class_id,
                'class_name': class_name,
                'prefix': prefix,
                'prefix_norm': prefix_norm,
                'subj_concord': r[3],
                'obj_concord': r[4],
                'possessive': r[5],
                'relative': r[6],
                'adj_concord': r[7],
                'nasal_context': bool(r[8])
            }
            if prefix_norm:
                self.prefix_map.append({'prefix': prefix_norm, 'class_id': class_id})

        # sort by prefix length desc so longest match is preferred
        self.prefix_map.sort(key=lambda x: len(x['prefix']), reverse=True)

        # cache set of all possessives for quick checks
        self.all_possessives = set()
        for c in self.classes.values():
            poss = c.get('possessive')
            if poss:
                self.all_possessives.add(poss.lower())

        # load explicit noun->class mappings (lexicon override)
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        try:
            cur.execute('SELECT term, class_id FROM noun_class_lexicon')
            rows2 = cur.fetchall()
        except sqlite3.Error:
            rows2 = []
        conn.close()
        self.lexicon_map = {}
        for term, cid in rows2:
            if term and cid in self.classes:
                self.lexicon_map[term.lower()] = cid

    @lru_cache(maxsize=1024)
    def get_by_prefix(self, noun: str) -> Optional[Dict]:
        """Return class dict for given noun (by exact lexicon match or matching prefix) or None."""
        if not noun:
            return None
        noun_l = noun.lower()
        # check explicit lexicon mapping first
        if hasattr(self, 'lexicon_map') and noun_l in self.lexicon_map:
            cid = self.lexicon_map.get(noun_l)
            return self.classes.get(cid)
        for p in self.prefix_map:
            pref = p['prefix']
            if pref and noun_l.startswith(pref):
                return self.classes.get(p['class_id'])
        return None

    def get_by_class_id(self, class_id: int) -> Optional[Dict]:
        return self.classes.get(class_id)

    def concord_for(self, class_id: int, role: str) -> Optional[str]:
        """Return concord string for a given class and role.
        role: one of 'possessive','subj','obj','adj','relative'
        """
        cls = self.get_by_class_id(class_id)
        if not cls:
            return None
        role_map = {
            'possessive': 'possessive',
            'subj': 'subj_concord',
            'obj': 'obj_concord',
            'adj': 'adj_concord',
            'relative': 'relative'
        }
        col = role_map.get(role)
        if not col:
            return None
        return cls.get(col)

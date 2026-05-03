import re
import sqlite3
from typing import Tuple, Dict


class Protector:
    """Protect and restore exception terms using immunity tokens.

    Usage:
        prot = Protector(db_path)
        protected_text, token_map = prot.protect(text)
        # run normalizations on protected_text
        restored = prot.restore(processed_text, token_map)
    """

    def __init__(self, db_path: str = 'data/pems_core.db'):
        self.db_path = db_path
        self.exceptions = self._load_exceptions()

    def _load_exceptions(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        try:
            cur.execute('SELECT term FROM exceptions_registry')
            rows = [r[0] for r in cur.fetchall()]
        except sqlite3.Error:
            rows = []
        conn.close()
        # normalize to lower for matching convenience
        return [r.lower() for r in rows]

    def protect(self, text: str) -> Tuple[str, Dict[str, str]]:
        """Replace exception terms with tokens and return token map."""
        token_map = {}
        out = text
        # simple word-boundary matching, case-insensitive
        for i, term in enumerate(self.exceptions):
            if not term:
                continue
            token = f"__IMMUNE_{i}__"
            # use regex to replace whole words case-insensitively and preserve original case
            pattern = re.compile(r"\b" + re.escape(term) + r"\b", flags=re.IGNORECASE)

            def _repl(m):
                token_map[token] = m.group(0)
                return token

            out, n_subs = pattern.subn(_repl, out)
        return out, token_map

    def restore(self, text: str, token_map: Dict[str, str]) -> str:
        out = text
        for token, term in token_map.items():
            out = out.replace(token, term)
        return out

#!/usr/bin/env python3
"""Morphological Architect: Applies phonological transformations to roots.
Transforms roots when they follow nasal classes (e.g., be -> mpe for Class 9 n-).
"""
import sqlite3


class MorphologicalArchitect:
    """Surgical phonological transformation engine for PEMS."""

    def __init__(self, db_path='data/pems_core.db'):
        self.db_path = db_path
        self.rules = {}  # Cache: context -> {input_char -> output_char}
        self.load_rules()

    def load_rules(self):
        """Load morphological rules from database into memory cache."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT context, input_char, output_char FROM morphological_rules")
        rows = cursor.fetchall()
        conn.close()

        for context, input_char, output_char in rows:
            if context not in self.rules:
                self.rules[context] = {}
            self.rules[context][input_char] = output_char

    def mutate(self, root, context='nasal'):
        """Apply nasal or other phonological mutation to the initial character of root.
        
        Args:
            root: The adjective root (e.g., 'be', 'fubelu', 'raro')
            context: The mutation context (e.g., 'nasal' for Class 9 n- prefix)
        
        Returns:
            Transformed root with initial character mutated, or original if no rule found.
        """
        if not root:
            return root

        # Get the first character (may be Unicode-aware)
        first_char = root[0]
        rest = root[1:]

        # Look up mutation rule
        if context in self.rules and first_char in self.rules[context]:
            replacement = self.rules[context][first_char]
            return replacement + rest

        # No mutation rule found
        return root

    def mutate_for_class(self, root, class_id):
        """Convenience method: Apply mutation based on noun class.
        Only Class 9 (nasal_context=1) triggers nasal mutations.
        
        Args:
            root: The adjective root
            class_id: The noun class ID
        
        Returns:
            Transformed root if class has nasal context, else original root.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT nasal_context FROM noun_class_concords WHERE class_id = ?", (class_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return root

        nasal_context = row[0]
        if nasal_context:
            return self.mutate(root, context='nasal')
        return root

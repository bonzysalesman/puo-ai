#!/usr/bin/env python3
"""
Debug enrichment matching
"""

import json
import re

def contains_term(text, term):
    term = term.strip()
    if not term:
        return False
    pattern = re.compile(rf'(?<!\w){re.escape(term)}(?!\w)', re.IGNORECASE)
    return bool(pattern.search(text))

# Load lexicon
with open('data/lexicon.json', 'r', encoding='utf-8') as f:
    lexicon = json.load(f)

# Test verse text from Genesis 1:1
test_verse = "Tšimolohong Molimo o ile a bōpa maholimo le lefatše."

print(f"Testing verse: {test_verse}")
print("="*60)

# Find entries with key terms
key_terms = ['lefatše', 'Molimo', 'maholimo', 'leseli']
matches_found = []

for entry in lexicon:
    for sense in entry.get('senses', []):
        st_terms = sense.get('sesotho_term', [])
        for term in st_terms:
            # Check if this term appears in our test verse
            if contains_term(test_verse, term):
                matches_found.append({
                    'entry_id': entry.get('entry_id'),
                    'term': term,
                    'definition': sense.get('definition_en', ''),
                    'sense_id': sense.get('sense_id')
                })

print(f"Direct matches found: {len(matches_found)}")
for match in matches_found:
    print(f"✅ '{match['term']}' -> {match['definition'][:50]}...")

print("\n" + "="*60)
print("Checking for potential matches with key terms:")

for key_term in key_terms:
    print(f"\nLooking for entries containing '{key_term}':")
    count = 0
    for entry in lexicon:
        for sense in entry.get('senses', []):
            st_terms = sense.get('sesotho_term', [])
            for term in st_terms:
                if key_term.lower() in term.lower():
                    count += 1
                    if count <= 3:  # Show first 3
                        print(f"  - '{term}' -> {sense.get('definition_en', '')[:40]}...")
    print(f"  Total found: {count}")

# Test the exact matching logic from enricher
print("\n" + "="*60)
print("Testing exact matching logic:")

# Test specific terms that should match
test_terms = ['lefatše', 'Molimo', 'maholimo']
for term in test_terms:
    result = contains_term(test_verse, term)
    print(f"'{term}' in '{test_verse}': {result}")
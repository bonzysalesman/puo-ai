

#!/usr/bin/env python3
"""
extract_undefined_words.py
--------------------------
Extracts undefined English and Sesotho words from the lexicon and corpus files.
Cross-references definitions and usage examples against the existing headwords
to identify "missing" vocabulary.

Outputs two reports:
- reports/undefined_english.csv
- reports/undefined_sesotho.csv
"""

import json
import re
import csv
from collections import Counter
from pathlib import Path

# Common English stop words
EN_STOP_WORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "in", "on", "at", "to", "for", "of", "with", "by", "from", "as", "into",
    "and", "but", "or", "nor", "so", "yet", "if", "because", "while",
    "it", "he", "she", "they", "we", "i", "you", "them", "us", "him", "her",
    "this", "that", "these", "those", "which", "who", "whom", "whose", "what",
    "has", "have", "had", "do", "does", "did", "can", "could", "will", "would",
    "shall", "should", "may", "might", "must", "not", "no", "yes",
    "all", "any", "some", "many", "much", "more", "most", "other", "such",
    "only", "own", "same", "very", "too", "also", "then", "than", "there", "when", "where", "how", "why",
    "up", "down", "out", "about", "over", "under", "after", "before", "between", "through",
    "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "first", "second",
    "its", "their", "our", "my", "your", "his", "hers", "theirs", "ours", "mine", "yours",
    "make", "made", "used", "using", "use", "person", "people", "act", "state", "action", "someone", "something"
}

# Common Sesotho particles/stop words
ST_STOP_WORDS = {
    "ha", "ho", "ea", "oa", "ba", "le", "se", "bo", "li", "a", "e", "u", "re",
    "me", "joang", "eng", "mang", "ke", "na", "ka", "tse", "tsa", "ba", "la",
    "oo", "ee", "ane", "hona", "sena", "tsena", "bana", "mona", "koana", "mane",
    "hore", "moo", "empa", "kapa", "leha", "hoba", "hobane", "joale", "feela"
}

def tokenize(text: str) -> list[str]:
    """Lowercase and extract alphabetical words."""
    if not text:
        return []
    # simple word extraction (ignoring numbers and punctuation)
    return re.findall(r"\b[a-zš]+\b", text.lower())

def load_headwords(lexicon_path: Path) -> tuple[set[str], set[str]]:
    en_headwords = set()
    st_headwords = set()
    
    with open(lexicon_path, "r", encoding="utf-8") as f:
        lexicon = json.load(f)
        
    for entry in lexicon:
        hw_en = entry.get("headword_english", "")
        # Add the exact headword (lowercased)
        if hw_en:
            en_headwords.add(hw_en.lower())
            # Also add individual words if it's a multi-word phrase
            for token in tokenize(hw_en):
                en_headwords.add(token)
                # primitive stemming for English
                if token.endswith("s") and len(token) > 3:
                    en_headwords.add(token[:-1])
                
        for hw_st_obj in entry.get("headword_sesotho", []):
            st = hw_st_obj.get("orthographic", "")
            if st:
                st_headwords.add(st.lower())
                for token in tokenize(st):
                    st_headwords.add(token)
                    
    return en_headwords, st_headwords

def main():
    lexicon_path = Path("data/lexicon.json")
    corpus_path = Path("data/corpus.json")
    
    if not lexicon_path.exists():
        print(f"Error: {lexicon_path} not found.")
        return
        
    en_headwords, st_headwords = load_headwords(lexicon_path)
    print(f"Loaded {len(en_headwords)} English headwords/tokens and {len(st_headwords)} Sesotho headwords/tokens.")
    
    missing_en_counter = Counter()
    missing_en_examples = {} # word -> example context
    
    missing_st_counter = Counter()
    missing_st_examples = {} # word -> example context

    with open(lexicon_path, "r", encoding="utf-8") as f:
        lexicon = json.load(f)
        
    for entry in lexicon:
        for sense in entry.get("senses", []):
            def_en = sense.get("definition_en", "")
            for token in tokenize(def_en):
                # Apply simple plural stripping fallback
                base_token = token[:-1] if token.endswith("s") and len(token) > 3 else token
                
                if token not in en_headwords and base_token not in en_headwords and token not in EN_STOP_WORDS:
                    missing_en_counter[token] += 1
                    if token not in missing_en_examples:
                        missing_en_examples[token] = def_en
                        
            # Sesotho terms inside the dictionary definition
            for st_term in sense.get("sesotho_term", []):
                for token in tokenize(st_term):
                    if token not in st_headwords and token not in ST_STOP_WORDS:
                        missing_st_counter[token] += 1
                        if token not in missing_st_examples:
                            missing_st_examples[token] = st_term

    # Process corpus.json for usage examples
    if corpus_path.exists():
        with open(corpus_path, "r", encoding="utf-8") as f:
            corpus = json.load(f)
            
        for row in corpus:
            st_text = row.get("sesotho", "")
            for token in tokenize(st_text):
                if token not in st_headwords and token not in ST_STOP_WORDS:
                    missing_st_counter[token] += 1
                    if token not in missing_st_examples:
                        missing_st_examples[token] = st_text
                        
            en_text = row.get("english", "")
            for token in tokenize(en_text):
                base_token = token[:-1] if token.endswith("s") and len(token) > 3 else token
                if token not in en_headwords and base_token not in en_headwords and token not in EN_STOP_WORDS:
                    missing_en_counter[token] += 1
                    if token not in missing_en_examples:
                        missing_en_examples[token] = en_text

    # Write English Report
    Path("reports").mkdir(exist_ok=True)
    with open("reports/undefined_english.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Word", "Frequency", "Example Context"])
        for word, count in missing_en_counter.most_common(500): # Top 500
            writer.writerow([word, count, missing_en_examples[word]])
            
    # Write Sesotho Report
    with open("reports/undefined_sesotho.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Word", "Frequency", "Example Context"])
        for word, count in missing_st_counter.most_common(500): # Top 500
            writer.writerow([word, count, missing_st_examples[word]])
            
    print(f"Extracted {len(missing_en_counter)} unique missing English words. Top 500 saved to reports/undefined_english.csv")
    print(f"Extracted {len(missing_st_counter)} unique missing Sesotho words. Top 500 saved to reports/undefined_sesotho.csv")

if __name__ == "__main__":
    main()

import json
import re
import argparse

def extract_unique_words(input_file, output_file):
    print(f"Loading {input_file}...")
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    unique_words = set()
    
    # regex to keep only letters and apostrophes (for things like "don't" or "Israel's")
    # also handles digits if needed, but usually a word list implies alphabetical
    word_pattern = re.compile(r"[a-zA-Z']+")
    
    print("Processing books...")
    for book, chapters in data.items():
        for chapter, verses in chapters.items():
            for verse_num, text in verses.items():
                # Find all words
                tokens = word_pattern.findall(text)
                for token in tokens:
                    # Clean token (remove leading/trailing apostrophes)
                    word = token.strip("'").lower()
                    if word:
                        unique_words.add(word)
                        
    # Sort alphabetically
    sorted_words = sorted(list(unique_words))
    
    print(f"Extracted {len(sorted_words)} unique words.")
    
    with open(output_file, "w", encoding="utf-8") as f:
        for word in sorted_words:
            f.write(word + "\n")
            
    print(f"Saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract unique words from NKJV JSON.")
    parser.add_argument("--input", default="NEW KING JAMES VERSION.json", help="Path to NKJV JSON file")
    parser.add_argument("--output", default="nkjv_wordlist.txt", help="Path to output word list file")
    args = parser.parse_args()
    
    extract_unique_words(args.input, args.output)

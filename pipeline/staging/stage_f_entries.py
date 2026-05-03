import json
import re
import argparse
from bs4 import BeautifulSoup

def clean_text(text):
    # Remove typical JW inline markers and normalize whitespace.
    text = re.sub(r"[+*]", " ", text)
    text = re.sub(r"^\d+\s*", "", text)
    text = text.replace("\u2019", "'")
    text = text.replace(" 'a", "'a")
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def contains_term(text, term):
    term = term.strip()
    if not term:
        return False
    # Match whole term only
    pattern = re.compile(rf"(?<!\w){re.escape(term)}(?!\w)", re.IGNORECASE)
    return bool(pattern.search(text))

def custom_load_corpus(corpus_files):
    corpus_refs = {}
    for st_file, en_file, source_prefix in corpus_files:
        try:
            with open(st_file, "r", encoding="utf-8") as f:
                st_soup = BeautifulSoup(f, "html.parser")
            with open(en_file, "r", encoding="utf-8") as f:
                en_soup = BeautifulSoup(f, "html.parser")
        except FileNotFoundError:
            print(f"Warning: Could not find {st_file} or {en_file}")
            continue
            
        st_verses = st_soup.find_all("span", class_="v") or st_soup.find_all("span", class_="verse")
        en_verses = en_soup.find_all("span", class_="v") or en_soup.find_all("span", class_="verse")
        
        st_dict = {v.get("id"): clean_text(v.get_text()) for v in st_verses if v.get("id")}
        en_dict = {v.get("id"): clean_text(v.get_text()) for v in en_verses if v.get("id")}
        
        for vid, st_text in st_dict.items():
            if vid in en_dict:
                corpus_refs[f"{source_prefix} ({vid})"] = {
                    "sesotho": st_text,
                    "english": en_dict[vid]
                }
    return corpus_refs

def stage_and_enrich_casalis(input_file, output_file, corpus_refs):
    with open(input_file, "r", encoding="utf-8") as f:
        raw_data = json.load(f)
        
    staged_entries = []
    
    pos_map = {
        "v.": "verb",
        "n.": "noun",
        "adj.": "adjective",
        "adv.": "adverb",
        "prep.": "preposition",
        "conj.": "conjunction",
        "interj.": "interjection",
        "v. t.": "verb",
        "v. i.": "verb",
        "n. & adj.": "noun", # Simplified
    }
    
    for entry in raw_data:
        hw_en = entry["headword_english"].lower().strip()
        pos_raw = entry["pos"].strip()
        sesotho_def = entry["sesotho"]
        
        # Extract Sesotho terms
        # 1. Split by semicolon (separates meanings/examples)
        parts = sesotho_def.split(';')
        term_part = parts[0]
        # 2. Split by comma (separates synonyms)
        raw_terms = [t.strip() for t in term_part.split(',')]
        
        cleaned_terms = []
        for t in raw_terms:
            # Remove text in parentheses
            t = re.sub(r'\(.*?\)', '', t).strip()
            if not t:
                continue
            cleaned_terms.append(t)

        if not cleaned_terms:
            continue
            
        hw_st = cleaned_terms[0]
        mapped_pos = pos_map.get(pos_raw, "unknown")
        
        valid_examples = []
        for ref_label, verse_data in corpus_refs.items():
            en_text = verse_data['english']
            st_text = verse_data['sesotho']
            
            # Match by English headword in English text
            if contains_term(en_text, hw_en):
                valid_examples.append({
                    "sesotho": st_text,
                    "english": en_text,
                    "source": ref_label
                })
                
        new_entry = {
            "headword_english": [hw_en.capitalize()],
            "pos": [mapped_pos],
            "headword_sesotho": {
                "orthographic": hw_st
            },
            "senses": [
                {
                    "definition": sesotho_def,
                    "usage_examples": valid_examples,
                    "sesotho_term": cleaned_terms
                }
            ]
        }
        staged_entries.append(new_entry)
            
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(staged_entries, f, indent=4, ensure_ascii=False)
        
    print(f"Staging complete for {input_file}.")
    print(f"Staged {len(staged_entries)} entries.")
    found_examples = [bool(e['senses'][0]['usage_examples']) for e in staged_entries].count(True)
    print(f"Found valid corpus examples for {found_examples} entries.")

def main():
    parser = argparse.ArgumentParser(description="Stage Casalis F entries.")
    parser.add_argument("--input", default="historical/casalis/f/casalis_f_cleaned_ocrsplit.json")
    parser.add_argument("--output", default="historical/staged/staged_casalis_f_final.json")
    args = parser.parse_args()

    corpus_files = [
        ("sources/bible/st_gen1.html", "sources/bible/en_gen1.html", "Gen1"),
        ("sources/bible/st_gen2.html", "sources/bible/en_gen2.html", "Gen2"),
        ("sources/bible/st_ps103.html", "sources/bible/en_ps103.html", "Ps103"),
        ("sources/bible/st_rom13.html", "sources/bible/en_rom13.html", "Rom13"),
    ]
    corpus_refs = custom_load_corpus(corpus_files)
    stage_and_enrich_casalis(args.input, args.output, corpus_refs)

if __name__ == "__main__":
    main()

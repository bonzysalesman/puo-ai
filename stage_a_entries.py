import json
import re
from bs4 import BeautifulSoup
from enricher import clean_text, contains_term, find_best_match

def custom_load_corpus(corpus_files):
    corpus_refs = {}
    for st_file, en_file, source_prefix in corpus_files:
        with open(st_file, "r") as f:
            st_soup = BeautifulSoup(f, "html.parser")
        with open(en_file, "r") as f:
            en_soup = BeautifulSoup(f, "html.parser")
            
        st_verses = st_soup.find_all("span", class_="v")
        en_verses = en_soup.find_all("span", class_="v")
        
        # Build dicts for quick lookup by verse ID
        st_dict = {v.get("id"): clean_text(v.get_text()) for v in st_verses if v.get("id")}
        en_dict = {v.get("id"): clean_text(v.get_text()) for v in en_verses if v.get("id")}
        
        # Merge them
        for vid, st_text in st_dict.items():
            if vid in en_dict:
                corpus_refs[vid] = {
                    "sesotho": st_text,
                    "english": en_dict[vid]
                }
    return corpus_refs

def stage_and_enrich_casalis(input_file, output_file, corpus_refs):
    with open(input_file, "r", encoding="utf-8") as f:
        raw_data = json.load(f)
        
    staged_entries = []
    
    # Simple pos mapping
    pos_map = {
        "v.": "verb",
        "n.": "noun",
        "adj.": "adjective",
        "adv.": "adverb",
        "prep.": "preposition",
        "conj.": "conjunction"
    }
    
    for entry in raw_data:
        hw_en = entry["headword_english"].lower().strip()
        pos_raw = entry["pos"].strip()
        sesotho_def = entry["sesotho"]
        
        # Extract the first Sesotho word (rough heuristic for headword)
        st_words = re.findall(r'[a-zA-Zš\’\']+', sesotho_def)
        if not st_words:
            continue
            
        # Often Casalis defines verbs starting with 'ho '
        hw_st = st_words[0]
        if hw_st == 'ho' and len(st_words) > 1:
            hw_st = f"ho {st_words[1]}"
            
        mapped_pos = pos_map.get(pos_raw, "unknown")
        
        # -----------------------------
        # Corpus Enrichment Filtering
        # -----------------------------
        match_found = False
        valid_examples = []
        
        for verse_id, verse_data in corpus_refs.items():
            en_text = verse_data['english']
            st_text = verse_data['sesotho']
            
            en_match = contains_term(en_text, hw_en) 
            
            if en_match:
                best_st, best_en = find_best_match(st_text, en_text, hw_en)
                
                valid_examples.append({
                    "sesotho": best_st,
                    "english": best_en,
                    "source": verse_id
                })
                
        # Stage ALL entries regardless of whether an example was found
        new_entry = {
            "headword_english": [hw_en.capitalize()],
            "pos": [mapped_pos],
            "headword_sesotho": {
                "orthographic": hw_st
            },
            "senses": [
                {
                    "definition": sesotho_def,
                    "usage_examples": valid_examples
                }
            ]
        }
        staged_entries.append(new_entry)
            
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(staged_entries, f, indent=4, ensure_ascii=False)
        
    print(f"Staging complete. Out of {len(raw_data)} raw Casalis entries, "
          f"all {len(staged_entries)} were staged for integration. "
          f"Found valid corpus examples for {[bool(e['senses'][0]['usage_examples']) for e in staged_entries].count(True)} entries.")

def stage_and_enrich_mabille(input_file, output_file, corpus_refs):
    with open(input_file, "r", encoding="utf-8") as f:
        raw_data = json.load(f)
        
    staged_entries = []
    
    pos_map = {
        "v. t.": "verb", "v. i.": "verb", "v.": "verb",
        "n.": "noun", "adj.": "adjective", "adv.": "adverb",
        "prep.": "preposition", "conj.": "conjunction", "int.": "interjection"
    }
    
    for entry in raw_data:
        hw_st = entry["headword_sesotho"].strip()
        pos_raw = entry["pos"].strip()
        en_def = entry["definition_en"]
        
        mapped_pos = pos_map.get(pos_raw, "unknown")
        
        valid_examples = []
        
        # For Mabille, we search corpus by Sesotho headword
        for verse_id, verse_data in corpus_refs.items():
            en_text = verse_data['english']
            st_text = verse_data['sesotho']
            
            st_match = contains_term(st_text, hw_st) 
            
            if st_match:
                best_st, best_en = find_best_match(st_text, en_text, hw_st)  # This function expects hw_st as term to highlight
                valid_examples.append({
                    "sesotho": best_st,
                    "english": best_en,
                    "source": verse_id
                })
                
        # Stage ALL entries regardless of whether an example was found
        new_entry = {
            "headword_english": [],  # Since it's Sesotho-English, we don't have a strict English headword list yet
            "pos": [mapped_pos],
            "headword_sesotho": {
                "orthographic": hw_st
            },
            "senses": [
                {
                    "definition": en_def,
                    "usage_examples": valid_examples
                }
            ]
        }
        staged_entries.append(new_entry)
            
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(staged_entries, f, indent=4, ensure_ascii=False)
        
    print(f"Staging complete. Out of {len(raw_data)} raw Mabille entries, "
          f"all {len(staged_entries)} were staged for integration. "
          f"Found valid corpus examples for {[bool(e['senses'][0]['usage_examples']) for e in staged_entries].count(True)} entries.")

corpus_files = [
    ('st_gen1.html', 'en_gen1.html', 'Gen1'),
    ('st_gen2.html', 'en_gen2.html', 'Gen2'),
    ('st_ps103.html', 'en_ps103.html', 'Ps103')
]

corpus_refs = custom_load_corpus(corpus_files)
stage_and_enrich_casalis("casalis_a_cleaned.json", "staged_casalis_a.json", corpus_refs)
stage_and_enrich_mabille("mabille_a_cleaned.json", "staged_mabille_a.json", corpus_refs)


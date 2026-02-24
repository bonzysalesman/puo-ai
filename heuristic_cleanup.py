import json
import re

def heuristic_clean_casalis(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    cleaned_entries = []
    
    # Regex to catch embedded entries inside definitions
    embedded_pattern = re.compile(r'([A-Z][a-z]{2,15})\s*[\,\;]?\s*(n\.|v\.|adj\.|adv\.|prep\.|conj\.)\s*(.*)')
    
    for entry in data:
        hw = entry["headword_english"].strip()
        pos = entry["pos_raw"].strip()
        raw_def = entry["definition_raw"]
        
        # Quick OCR fixes for pos
        pos = pos.replace('11.', 'n.').replace('f', '').replace(' ', '')
        
        # Split logic: sometimes a definition contains another entry like "Admimsfer, v ho lisa, tsa- maisa Administrat ion ,, n pnso, tiso."
        # We can try to split it by looking for capital words followed by v. or n.
        parts = re.split(r'(?<=\.)\s+(?=[A-Z][a-z]{2,15}\s*[,;\.]*\s*(?:n\.|v\.|adj\.|adv\.))', raw_def)
        
        main_def = parts[0]
        cleaned_entries.append({
            "headword_english": hw,
            "pos": pos,
            "sesotho": main_def.strip()
        })
        
        for part in parts[1:]:
            m = embedded_pattern.match(part)
            if m:
                emb_hw = m.group(1)
                emb_pos = m.group(2)
                emb_def = m.group(3)
                cleaned_entries.append({
                    "headword_english": emb_hw,
                    "pos": emb_pos,
                    "sesotho": emb_def.strip()
                })
            else:
                # If it doesn't match perfectly, append to previous
                cleaned_entries[-1]["sesotho"] += " " + part.strip()
                
    # Further fixes on resulting entries
    for c in cleaned_entries:
        c["sesotho"] = re.sub(r'-\s+', '', c["sesotho"]) # fix hyphenation
        c["sesotho"] = c["sesotho"].replace('tsa-', 'tsa').replace(',,', ',')
        
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(cleaned_entries, f, indent=2, ensure_ascii=False)
    print(f"Cleaned Casalis. Resulting entries: {len(cleaned_entries)}")

def heuristic_clean_mabille(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    cleaned_entries = []
    
    for entry in data:
        hw = entry["headword_sesotho_raw"].strip()
        pos = entry["pos_raw"].strip()
        raw_def = entry["definition_raw"]
        
        c_def = re.sub(r'-\s+', '', raw_def)
        c_def = c_def.lstrip(",. ")
        
        cleaned_entries.append({
            "headword_sesotho": hw,
            "pos": pos,
            "definition_en": c_def.strip()
        })
        
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(cleaned_entries, f, indent=2, ensure_ascii=False)
    print(f"Cleaned Mabille. Resulting entries: {len(cleaned_entries)}")

heuristic_clean_casalis("casalis_a_raw.json", "casalis_a_cleaned.json")
heuristic_clean_mabille("mabille_a_raw.json", "mabille_a_cleaned.json")

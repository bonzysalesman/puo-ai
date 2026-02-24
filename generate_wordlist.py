import json

def generate_wordlist(dictionary_file, output_file):
    with open(dictionary_file, "r", encoding="utf-8") as f:
        dictionary = json.load(f)

    # Need to handle dictionary being a list, since we fixed that
    entries = dictionary if isinstance(dictionary, list) else dictionary.get("entries", [])
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# PUO-AI Dictionary Wordlist\n\n")
        f.write(f"Total Entries: {len(entries)}\n\n")
        f.write("| English | Sesotho | POS |\n")
        f.write("|---|---|---|\n")
        
        for entry in entries:
            en_words = ", ".join(entry.get("headword_english", []))
            
            st_data = entry.get("headword_sesotho", [])
            if isinstance(st_data, list) and len(st_data) > 0:
                st_word = st_data[0].get("orthographic", "")
            elif isinstance(st_data, dict):
                st_word = st_data.get("orthographic", "")
            else:
                st_word = ""
                
            pos_items = entry.get("pos", [])
            pos_strs = []
            for p in pos_items:
                if isinstance(p, dict):
                    pos_strs.append(p.get("full", p.get("tag", "")))
                else:
                    pos_strs.append(str(p))
            pos = ", ".join(pos_strs)
            
            f.write(f"| {en_words} | {st_word} | {pos} |\n")
            
    print(f"Wordlist generated with {len(entries)} entries at {output_file}")

generate_wordlist("dictionary.json", "wordlist.md")

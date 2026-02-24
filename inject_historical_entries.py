import json
import uuid

def inject_staged_entries_robust(dictionary_file, staged_files):
    # Load current dictionary
    with open(dictionary_file, "r", encoding="utf-8") as f:
        dictionary = json.load(f)

    # Collect existing english and sesotho headwords to prevent exact duplication
    existing_en = set()
    existing_st = set()
    for entry in dictionary:
        if not isinstance(entry, dict):
            continue
        for en in entry.get("headword_english", []):
            existing_en.add(en.lower().strip())
        st_hw_list = entry.get("headword_sesotho", [])
        if st_hw_list and isinstance(st_hw_list, list):
            st_hw = st_hw_list[0].get("orthographic", "")
            if st_hw:
                existing_st.add(st_hw.lower().strip())

    injected_count = 0
    total_processed = 0

    for s_file in staged_files:
        with open(s_file, "r", encoding="utf-8") as f:
            staged = json.load(f)

        for entry in staged:
            total_processed += 1
            
            # Basic deduplication checking based on headwords
            en_words = [en.lower().strip() for en in entry.get("headword_english", [])]
            st_hw_list = entry.get("headword_sesotho", [])
            st_word = ""
            if st_hw_list and isinstance(st_hw_list, list):
                st_word = st_hw_list[0].get("orthographic", "").lower().strip()
            elif isinstance(st_hw_list, dict):
                st_word = st_hw_list.get("orthographic", "").lower().strip()
                
            # Convert staged headword_sesotho back to list if staged differently
            if isinstance(entry.get("headword_sesotho"), dict):
                entry["headword_sesotho"] = [entry["headword_sesotho"]]
            
            # If it's Casalis (English-Sesotho), rely on English headword collision
            if en_words and en_words[0] in existing_en:
                continue
                
            # If it's Mabille (Sesotho-English), rely on Sesotho headword collision
            if not en_words and st_word in existing_st:
                continue

            # Ensure entry_id exists
            if "entry_id" not in entry:
                entry["entry_id"] = str(uuid.uuid4())
                
            # Ensure syllables array exists for schema
            if "syllables" not in entry:
                entry["syllables"] = [""]
                if entry["headword_sesotho"] and isinstance(entry["headword_sesotho"], list):
                    entry["syllables"] = [entry["headword_sesotho"][0].get("orthographic", "")]
                
            # Ensure morphology exists
            if "morphology" not in entry:
                entry["morphology"] = {
                    "root": "",
                    "derivation": "Historical Entry",
                    "noun_class": "unknown"
                }
                
            # Ensure thesaurus exists
            if "thesaurus" not in entry:
                entry["thesaurus"] = {
                    "synonyms": [],
                    "antonyms": [],
                    "related_terms": []
                }
                
            # Ensure senses have IDs
            for i, sense in enumerate(entry["senses"]):
                if "id" not in sense:
                    sense["id"] = f"sense_{i+1}"
            
            dictionary.append(entry)
            injected_count += 1
            
            # Add to set so we don't inject duplicates from within the staged files
            if en_words: existing_en.add(en_words[0])
            if st_word: existing_st.add(st_word)

    with open(dictionary_file, "w", encoding="utf-8") as f:
        json.dump(dictionary, f, indent=4, ensure_ascii=False)

    print(f"Processed {total_processed} staged entries across files.")
    print(f"Successfully injected {injected_count} new unique historical 'A' entries into {dictionary_file}!")

staged_files = ["staged_casalis_a.json", "staged_mabille_a.json"]
inject_staged_entries_robust("dictionary.json", staged_files)

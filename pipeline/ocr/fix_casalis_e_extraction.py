import json
import re
import uuid

def clean_term(t):
    # Remove text in parentheses like (of the body)
    t = re.sub(r'\(.*?\)', '', t)
    # Remove colons and anything after them (examples)
    if ':' in t:
        t = t.split(':')[0]
    return t.strip()

def fix_lexicon():
    user_entries = [
        {"headword_english": "Every", "pos": "adj.", "sesotho": "e mong le e mong"},
        {"headword_english": "Everywhere", "pos": "adv.", "sesotho": "kahohle, kae le kae"},
        {"headword_english": "Evict", "pos": "v.", "sesotho": "ho falatsa, ho ntšetsa ntle ka matla"},
        {"headword_english": "Evil", "pos": "n. & adj.", "sesotho": "(n) bobe, bokhopo; (adj) e mpe"},
        {"headword_english": "Exact", "pos": "adj.", "sesotho": "e tšoanang hantle, e lekanyitsoeng ka hloko"},
        {"headword_english": "Exactly", "pos": "adv.", "sesotho": "ka ho nepahala, hantle"},
        {"headword_english": "Exalt", "pos": "v.", "sesotho": "ho phahamisa, ho rorisa"},
        {"headword_english": "Excite", "pos": "v.", "sesotho": "ho mofofutsa, ho hlohlella"},
        {"headword_english": "Exclaim", "pos": "v.", "sesotho": "ho hooa, ho hoeletsa, ho meketsa"},
        {"headword_english": "Exculpate", "pos": "v.", "sesotho": "ho latola molato, ho hlakola molato"},
        {"headword_english": "Execrate", "pos": "v.", "sesotho": "ho hloea haholo, ho rohaka"},
        {"headword_english": "Exert", "pos": "v.", "sesotho": "ho etsa ka matla, ho ikitlaetsa"},
        {"headword_english": "Exhalation", "pos": "n.", "sesotho": "mouvane, mouoane"},
        {"headword_english": "Exhibition", "pos": "n.", "sesotho": "tlhahiso ea lintho pepeneneng"},
        {"headword_english": "Exhort", "pos": "v.", "sesotho": "ho khothatsa, ho eletsa"},
        {"headword_english": "Expectorate", "pos": "v.", "sesotho": "ho tšoela, ho khohlela"},
        {"headword_english": "Expedition", "pos": "n.", "sesotho": "phakiso; leeto la ntoa kapa la hloela"},
        {"headword_english": "Expire", "pos": "v.", "sesotho": "ho nehela moea, ho shoa; ho fela"},
        {"headword_english": "Explicit", "pos": "adj.", "sesotho": "e utloahalang, e bonahalang hantle"},
        {"headword_english": "Exposition", "pos": "n.", "sesotho": "thlaloso, tlhahiso"},
        {"headword_english": "Extremity", "pos": "n.", "sesotho": "bofelo, pheletso"},
        {"headword_english": "Extricate", "pos": "v.", "sesotho": "ho lokolla, ho ntša, ho rarolla"}
    ]

    lexicon_file = "data/lexicon.json"
    with open(lexicon_file, "r", encoding="utf-8") as f:
        lexicon = json.load(f)

    updated_count = 0
    for update in user_entries:
        hw_en = update["headword_english"]
        found = False
        for entry in lexicon:
            if str(entry.get("headword_english", "")).strip() == hw_en:
                # Found the entry, now update terms
                raw_sesotho = update["sesotho"]
                # Split by semicolon to get the term part vs example part
                # e.g. "e 'ngoe le e 'ngoe; each man: motho ka mong" -> ["e 'ngoe le e 'ngoe", " each man: motho ka mong"]
                segments = raw_sesotho.split(';')
                term_segment = segments[0]
                
                # Split by comma to get variations
                # e.g. "nontšoe, ntsu" -> ["nontšoe", "ntsu"]
                raw_terms = term_segment.split(',')
                cleaned_terms = [clean_term(t) for t in raw_terms if clean_term(t)]
                
                if not cleaned_terms:
                    continue

                # Update entry fields
                # 1. headword_sesotho
                entry["headword_sesotho"] = [
                    {"orthographic": t, "tone_marked": "", "ipa": "", "tone_pattern": ""}
                    for t in cleaned_terms
                ]
                
                # 2. syllables (rough update)
                entry["syllables"] = cleaned_terms
                
                # 3. senses
                if "senses" in entry and entry["senses"]:
                    sense = entry["senses"][0]
                    sense["definition_en"] = raw_sesotho
                    sense["sesotho_term"] = cleaned_terms
                
                print(f"Updated: {hw_en} -> {cleaned_terms}")
                updated_count += 1
                found = True
                break
        if not found:
            print(f"Adding new entry: {hw_en}")
            raw_sesotho = update["sesotho"]
            segments = raw_sesotho.split(';')
            term_segment = segments[0]
            raw_terms = term_segment.split(',')
            cleaned_terms = [clean_term(t) for t in raw_terms if clean_term(t)]
            
            # Map user POS to standardized lexicon POS if necessary
            # e.g. "n." -> "noun", "v." -> "verb", "adj." -> "adjective"
            pos_map = {
                "n.": "noun",
                "n. pl.": "noun",
                "v.": "verb",
                "adj.": "adjective",
                "adv.": "adverb",
                "conj.": "conjunction",
                "prep.": "preposition"
            }
            standard_pos = pos_map.get(update["pos"], update["pos"])

            new_entry = {
                "entry_id": f"entry_{uuid.uuid4().hex[:16]}",
                "headword_english": hw_en,
                "pos": [standard_pos],
                "headword_sesotho": [
                    {"orthographic": t, "tone_marked": "", "ipa": "", "tone_pattern": ""}
                    for t in cleaned_terms
                ],
                "syllables": cleaned_terms,
                "morphology": {
                    "root": "",
                    "derivation": "Historical Entry",
                    "noun_class": "unknown"
                },
                "senses": [
                    {
                        "sense_id": f"sense_{uuid.uuid4().hex[:16]}",
                        "definition_en": raw_sesotho,
                        "sesotho_term": cleaned_terms
                    }
                ],
                "thesaurus": {
                    "synonyms_en": [],
                    "antonyms_en": [],
                    "synonyms_st": [],
                    "antonyms_st": []
                }
            }
            lexicon.append(new_entry)
            updated_count += 1

    with open(lexicon_file, "w", encoding="utf-8") as f:
        json.dump(lexicon, f, indent=2, ensure_ascii=False)

    print(f"\nSuccessfully updated {updated_count} entries in {lexicon_file}.")

if __name__ == "__main__":
    fix_lexicon()

import json
import re

def clean_lexicon(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        lexicon = json.load(f)

    removal_count = 0
    recovery_count = 0

    for entry in lexicon:
        # Check headword_sesotho
        hws = entry.get("headword_sesotho", [])
        new_hws = [hw for hw in hws if hw.get("orthographic", "").lower() != "to"]
        
        if len(new_hws) < len(hws):
            removal_count += (len(hws) - len(new_hws))
            entry["headword_sesotho"] = new_hws

        # Check syllables
        sylls = entry.get("syllables", [])
        new_sylls = [s for s in sylls if (isinstance(s, str) and s.lower() != "to") or (isinstance(s, dict) and s.get("orthographic", "").lower() != "to")]
        if len(new_sylls) < len(sylls):
            removal_count += (len(sylls) - len(new_sylls))
            entry["syllables"] = new_sylls

        # Check senses
        for sense in entry.get("senses", []):
            terms = sense.get("sesotho_term", [])
            new_terms = [t for t in terms if t.lower() != "to"]
            if len(new_terms) < len(terms):
                removal_count += (len(terms) - len(new_terms))
                sense["sesotho_term"] = new_terms
            
            # Recovery logic: if we have no terms now, try to find some in the definition
            if not sense.get("sesotho_term") and "definition_en" in sense:
                defn = sense["definition_en"]
                # Try to find Sesotho-looking words (e.g., after "ho " or just after the English part)
                # This is heuristic and noisy, but better than "to"
                recovered = []
                # Look for 'ho ' followed by words
                matches = re.findall(r'ho\s+([a-z\u014d\u0113\u0161]+(?:(?:\s+|,)\s*[a-z\u014d\u0113\u0161]+)*)', defn, re.IGNORECASE)
                for m in matches:
                    # Split by comma or semicolon and clean
                    for part in re.split(r'[,;]', m):
                        clean_part = part.strip().lower()
                        if clean_part and clean_part != "to":
                            recovered.append(f"ho {clean_part}")
                
                if recovered:
                    sense["sesotho_term"] = recovered
                    recovery_count += 1
                    # Also update headword if it's empty
                    if not entry.get("headword_sesotho"):
                        entry["headword_sesotho"] = [{"orthographic": recovered[0], "tone_marked": "", "ipa": "", "tone_pattern": ""}]

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(lexicon, f, ensure_ascii=False, indent=2)

    print(f"Cleanup complete.")
    print(f"Removed {removal_count} instances of 'to'.")
    print(f"Recovered {recovery_count} sense terms from definitions.")

if __name__ == "__main__":
    clean_lexicon("data/lexicon.json", "data/lexicon.json")

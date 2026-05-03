#!/usr/bin/env python3
"""
export_for_translation.py
-------------------------
Scans lexicon.json for senses that lack a 'definition_st' field and
exports a Markdown/JSON payload ready to be sent to an LLM (e.g., Gemini)
for translation into Sesotho.
"""

import json
from pathlib import Path

def main():
    lexicon_path = Path("data/lexicon.json")
    output_path = Path("reports/definitions_for_translation.json")
    
    if not lexicon_path.exists():
        print(f"Error: {lexicon_path} not found.")
        return
        
    with open(lexicon_path, "r", encoding="utf-8") as f:
        lexicon = json.load(f)
        
    translation_batch = []
    
    for entry in lexicon:
        for sense in entry.get("senses", []):
            if "definition_en" in sense and "definition_st" not in sense:
                # Add it to the batch
                translation_batch.append({
                    "entry_id": entry.get("entry_id"),
                    "sense_id": sense.get("sense_id"),
                    "headword_english": entry.get("headword_english"),
                    "definition_en": sense.get("definition_en"),
                    "definition_st": "" # Empty template for the LLM to fill
                })
                
    # We might want to limit the batch size if it's very large,
    # but for now, we'll just export all of them or up to a limit.
    batch_limit = 50 
    batch = translation_batch[:batch_limit]
    
    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(batch, f, ensure_ascii=False, indent=2)
        
    print(f"Found {len(translation_batch)} definitions missing Sesotho translation.")
    print(f"Exported top {len(batch)} to {output_path}")

if __name__ == "__main__":
    main()

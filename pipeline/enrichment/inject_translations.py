#!/usr/bin/env python3
"""
inject_translations.py
----------------------
Takes a JSON file containing translated definitions and updates the existing
lexicon.json by injecting the 'definition_st' field into the correct senses.
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
import shutil

def create_backup(lexicon_path: Path):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path(f"backups/backup_{timestamp}")
    backup_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(lexicon_path, backup_dir / lexicon_path.name)
    print(f"Backup created in {backup_dir}")

def main():
    parser = argparse.ArgumentParser(description="Inject translated definitions into lexicon.json")
    parser.add_argument("translations_file", help="Path to JSON file containing translated definitions")
    args = parser.parse_args()
    
    lexicon_path = Path("data/lexicon.json")
    trans_path = Path(args.translations_file)
    
    if not trans_path.exists():
        print(f"Error: {trans_path} not found.")
        return
        
    with open(trans_path, "r", encoding="utf-8") as f:
        translations = json.load(f)
        
    # Build a lookup for quick injection
    # {(entry_id, sense_id): definition_st}
    trans_lookup = {}
    for t in translations:
        if "entry_id" in t and "sense_id" in t and t.get("definition_st"):
            trans_lookup[(t["entry_id"], t["sense_id"])] = t["definition_st"]
            
    if not trans_lookup:
        print("No valid translations found in the input file.")
        return
        
    print(f"Found {len(trans_lookup)} translated definitions to inject.")
    
    with open(lexicon_path, "r", encoding="utf-8") as f:
        lexicon = json.load(f)
        
    create_backup(lexicon_path)
    
    injected_count = 0
    for entry in lexicon:
        entry_id = entry.get("entry_id")
        for sense in entry.get("senses", []):
            sense_id = sense.get("sense_id")
            key = (entry_id, sense_id)
            if key in trans_lookup:
                sense["definition_st"] = trans_lookup[key]
                injected_count += 1
                
    with open(lexicon_path, "w", encoding="utf-8") as f:
        json.dump(lexicon, f, ensure_ascii=False, indent=2)
        
    print(f"Successfully injected {injected_count} Sesotho definitions into lexicon.json")

if __name__ == "__main__":
    main()

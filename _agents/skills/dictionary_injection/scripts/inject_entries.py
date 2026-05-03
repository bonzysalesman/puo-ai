import json
import hashlib
import sys
import os
import shutil
from datetime import datetime
from typing import Iterable

def stable_hash(parts: Iterable[str], prefix: str, length: int = 16) -> str:
    joined = "|".join(parts)
    digest = hashlib.sha1(joined.encode("utf-8")).hexdigest()[:length]
    return f"{prefix}{digest}"

def backup_files(files):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"backups/backup_{timestamp}"
    os.makedirs(backup_dir, exist_ok=True)
    for f in files:
        if os.path.exists(f):
            # Create subdirectories if necessary (e.g. data/)
            dest = os.path.join(backup_dir, f)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copy(f, dest)
    return backup_dir

def inject_entries(input_file):
    # Standard project files
    lexicon_file = 'data/lexicon.json'
    corpus_file = 'data/corpus.json'
    attestations_file = 'data/attestations.json'
    
    # Load existing files
    try:
        with open(lexicon_file, 'r', encoding='utf-8') as f:
            lexicon = json.load(f)
        with open(corpus_file, 'r', encoding='utf-8') as f:
            corpus = json.load(f)
        with open(attestations_file, 'r', encoding='utf-8') as f:
            attestations = json.load(f)
    except FileNotFoundError as e:
        print(f"Error: Required file not found: {e.filename}")
        return
    
    # Load new entries
    with open(input_file, 'r', encoding='utf-8') as f:
        new_entries = json.load(f)
    
    print(f"Backing up files...")
    backup_path = backup_files([lexicon_file, corpus_file, attestations_file])
    print(f"Backups created in {backup_path}")

    added_count = 0
    
    # Index for fast lookup
    corpus_by_key = {}
    for row in corpus:
        key = (row.get("source", ""), row.get("ref", ""), row.get("sesotho_text", ""), row.get("english_text", ""))
        corpus_by_key[key] = row["corpus_id"]
        
    attestation_ids = {row["attestation_id"] for row in attestations}

    for idx, entry in enumerate(new_entries):
        hw_en = entry.get('headword_english', '').strip()
        if not hw_en:
            continue
            
        target_id = entry.get('entry_id')
        hw_st_list = entry.get('headword_sesotho', [])
        if not hw_st_list: continue
        ortho = hw_st_list[0].get('orthographic', '') if isinstance(hw_st_list[0], dict) else str(hw_st_list[0]).strip()
        
        # Determine if we should update or inject
        existing_idx = -1
        if target_id:
            for i, e in enumerate(lexicon):
                if e.get('entry_id') == target_id:
                    existing_idx = i
                    break
        
        if existing_idx == -1:
            for i, e in enumerate(lexicon):
                if e.get('headword_english') == hw_en:
                    for s in e.get('headword_sesotho', []):
                        if s.get('orthographic') == ortho:
                            existing_idx = i
                            break
                if existing_idx != -1: break
            
        if existing_idx != -1:
            e_id = target_id or lexicon[existing_idx].get('entry_id')
        else:
            e_id = target_id or stable_hash([hw_en, ortho, str(idx)], prefix="entry_")
        
        # Format POS
        pos_raw = entry.get('pos', [])
        pos = []
        for p in pos_raw:
            if isinstance(p, dict):
                pos.append(p.get('tag', ''))
            else:
                pos.append(str(p))

        # Format headword_sesotho
        hw_st_objs = []
        if len(hw_st_list) > 0 and isinstance(hw_st_list[0], dict):
            hw_st_objs = hw_st_list
            for obj in hw_st_objs:
                for field in ['tone_marked', 'ipa', 'tone_pattern']:
                    if field not in obj:
                        obj[field] = ""
        else:
            for hw_st in hw_st_list:
                hw_st_objs.append({
                    "orthographic": hw_st,
                    "tone_marked": "",
                    "ipa": "",
                    "tone_pattern": ""
                })
                
        # Format Syllables
        syllables = []
        for s in entry.get('syllables', []):
            if isinstance(s, dict):
                syllables.append(str(s.get('orthographic', '')).strip())
            else:
                syllables.append(str(s).strip())
            
        # Format Morphology
        morph = entry.get('morphology', {})
        derivation = morph.get('derivation', '')
        noun_class = str(morph.get('noun_class', ''))
            
        # Format Senses
        senses = []
        for s_idx, sense in enumerate(entry.get('senses', [])):
            new_sense = sense.copy()
            if 'sense_id' not in new_sense:
                new_sense['sense_id'] = f"{e_id}.sense_{s_idx+1}"
            
            # Extract and move usage_example
            example = new_sense.pop("usage_example", None)
            senses.append(new_sense)
            
            if example:
                st_text = str(example.get("sesotho", "")).strip()
                en_text = str(example.get("english", "")).strip()
                source_raw = str(example.get("source", "")).strip()
                
                # Check for existing corpus entry
                corpus_key = ("Manual Entry", f"{hw_en} Ex {s_idx+1}", st_text, en_text)
                c_id = corpus_by_key.get(corpus_key)
                if not c_id:
                    c_id = stable_hash(list(corpus_key), prefix="corpus_")
                    corpus.append({
                        "corpus_id": c_id,
                        "source": corpus_key[0],
                        "ref": corpus_key[1],
                        "sesotho_text": st_text,
                        "english_text": en_text
                    })
                    corpus_by_key[corpus_key] = c_id
                
                # Link via Attestations
                att_id = stable_hash([new_sense['sense_id'], c_id], prefix="att_")
                if att_id not in attestation_ids:
                    attestations.append({
                        "attestation_id": att_id,
                        "sense_id": new_sense['sense_id'],
                        "corpus_id": c_id,
                        "source_raw": source_raw,
                        "match_terms": new_sense.get("sesotho_term", []),
                        "score": 1.0,
                        "method": "manual_injection_v1"
                    })
                    attestation_ids.add(att_id)
                
        # Final Format
        formatted_entry = {
            "entry_id": e_id,
            "headword_english": hw_en,
            "pos": pos,
            "headword_sesotho": hw_st_objs,
            "syllables": syllables,
            "morphology": {
                "root": morph.get('root', ''),
                "derivation": derivation,
                "noun_class": noun_class
            },
            "senses": senses,
            "thesaurus": entry.get('thesaurus', {}),
            "related_words": entry.get('related_words', [])
        }
        
        if existing_idx != -1:
            lexicon[existing_idx] = formatted_entry
        else:
            lexicon.append(formatted_entry)
        added_count += 1

    lexicon.sort(key=lambda x: x.get('headword_english', '').lower())

    with open(lexicon_file, 'w', encoding='utf-8') as f:
        json.dump(lexicon, f, indent=2, ensure_ascii=False)
    with open(corpus_file, 'w', encoding='utf-8') as f:
        json.dump(corpus, f, indent=2, ensure_ascii=False)
    with open(attestations_file, 'w', encoding='utf-8') as f:
        json.dump(attestations, f, indent=2, ensure_ascii=False)

    print(f"Successfully added/updated {added_count} entries.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 inject_entries.py <input_json_file>")
    else:
        inject_entries(sys.argv[1])

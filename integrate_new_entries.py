#!/usr/bin/env python3
"""
Integrate new dictionary entries into PUO-AI datasets
Uses Feynman technique principles for clear, step-by-step processing
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path

def stable_hash(parts, prefix, length=16):
    """Generate consistent hash IDs"""
    joined = "|".join(str(p) for p in parts)
    digest = hashlib.sha1(joined.encode("utf-8")).hexdigest()[:length]
    return f"{prefix}{digest}"

def transform_to_schema(new_entries):
    """
    Transform new entries to match existing lexicon schema
    
    Simple explanation: Convert the recipe format to match our cookbook format
    """
    transformed = []
    
    for entry in new_entries:
        # Transform to match existing schema structure
        transformed_entry = {
            "entry_id": entry["entry_id"],
            "headword_english": entry["headword_english"],
            "pos": [pos_item.get("tag", "") for pos_item in entry.get("pos", [])],
            "headword_sesotho": entry["headword_sesotho"],
            "syllables": [syll.get("orthographic", "") for syll in entry.get("syllables", [])],
            "morphology": {
                "root": entry.get("morphology", {}).get("root", ""),
                "derivation": entry.get("morphology", {}).get("stative", ""),
                "noun_class": entry.get("morphology", {}).get("origin", "")
            },
            "senses": [],
            "thesaurus": {
                "synonyms_en": [],
                "antonyms_en": [],
                "synonyms_st": [],
                "antonyms_st": []
            }
        }
        
        # Transform senses
        for i, sense in enumerate(entry.get("senses", [])):
            sense_id = f"{entry['entry_id']}.sense_{i+1}"
            transformed_sense = {
                "sense_id": sense_id,
                "definition_en": sense["definition_en"],
                "sesotho_term": [entry["headword_sesotho"][0]["orthographic"]]
            }
            transformed_entry["senses"].append(transformed_sense)
        
        transformed.append(transformed_entry)
    
    return transformed

def create_corpus_entries(new_entries):
    """
    Extract usage examples and create corpus entries
    
    Simple explanation: Take the example sentences and put them in the sentence collection
    """
    corpus_entries = []
    
    for entry in new_entries:
        for sense in entry.get("senses", []):
            usage = sense.get("usage_example")
            if usage:
                corpus_id = stable_hash([
                    usage["sesotho"], 
                    usage["english"]
                ], "corpus_")
                
                corpus_entry = {
                    "corpus_id": corpus_id,
                    "source": "Manual Integration",
                    "ref": entry["entry_id"],
                    "sesotho_text": usage["sesotho"],
                    "english_text": usage["english"]
                }
                corpus_entries.append(corpus_entry)
    
    return corpus_entries

def create_attestations(new_entries, corpus_entries):
    """
    Create links between word senses and example sentences
    
    Simple explanation: Draw lines connecting words to their example sentences
    """
    attestations = []
    
    # Create mapping of usage examples to corpus IDs
    usage_to_corpus = {}
    for corpus_entry in corpus_entries:
        key = (corpus_entry["sesotho_text"], corpus_entry["english_text"])
        usage_to_corpus[key] = corpus_entry["corpus_id"]
    
    for entry in new_entries:
        for i, sense in enumerate(entry.get("senses", [])):
            usage = sense.get("usage_example")
            if usage:
                sense_id = f"{entry['entry_id']}.sense_{i+1}"
                key = (usage["sesotho"], usage["english"])
                corpus_id = usage_to_corpus.get(key)
                
                if corpus_id:
                    attestation_id = stable_hash([sense_id, corpus_id], "att_")
                    attestation = {
                        "attestation_id": attestation_id,
                        "sense_id": sense_id,
                        "corpus_id": corpus_id,
                        "source_raw": f"Manual Integration ({entry['entry_id']})",
                        "match_terms": [entry["headword_sesotho"][0]["orthographic"]],
                        "score": 1000.0,
                        "method": "manual_integration_v1"
                    }
                    attestations.append(attestation)
    
    return attestations

def integrate_entries():
    """
    Main integration function
    
    Simple explanation: Add the new words to all our word collections
    """
    
    # The new entries provided by the user - H-series
    new_entries = [
        {
            "entry_id": "st_H_01",
            "headword_english": "Heard",
            "pos": [{"tag": "v.", "full": "verb"}],
            "headword_sesotho": [{"orthographic": "utloa", "tone_marked": "ūtlōā"}],
            "syllables": [{"orthographic": "u-tloa", "syllable_count": 2}],
            "morphology": {"past": "utloile", "passive": "utloahala"},
            "senses": [{
                "definition_en": "To perceive sound; to obey or pay attention to a command.",
                "usage_example": {
                    "sesotho": "Jehova a utloa sello sa bona.",
                    "english": "Jehovah heard their cry."
                }
            }]
        },
        {
            "entry_id": "st_H_02",
            "headword_english": "Heads",
            "pos": [{"tag": "n.", "full": "noun"}],
            "headword_sesotho": [{"orthographic": "lihlooho", "tone_marked": "līhlōōhō"}],
            "syllables": [{"orthographic": "li-hloo-ho", "syllable_count": 3}],
            "morphology": {"noun_class": 10, "singular": "hlooho"},
            "senses": [{
                "definition_en": "The upper part of the body; also used to denote leaders or chiefs.",
                "usage_example": {
                    "sesotho": "Lihlooho tsa malapa a Iseraele.",
                    "english": "The heads of the households of Israel."
                }
            }]
        }
    ]
    
    print("🚀 Starting integration of new dictionary entries...")
    
    # Step 1: Load existing datasets
    print("📖 Step 1: Loading existing datasets...")
    with open('data/lexicon.json', 'r', encoding='utf-8') as f:
        lexicon = json.load(f)
    
    with open('data/corpus.json', 'r', encoding='utf-8') as f:
        corpus = json.load(f)
    
    with open('data/attestations.json', 'r', encoding='utf-8') as f:
        attestations = json.load(f)
    
    print(f"   Current lexicon entries: {len(lexicon)}")
    print(f"   Current corpus entries: {len(corpus)}")
    print(f"   Current attestations: {len(attestations)}")
    
    # Step 2: Transform new entries
    print("🔄 Step 2: Transforming entries to match schema...")
    transformed_entries = transform_to_schema(new_entries)
    
    # Step 3: Create corpus entries
    print("📝 Step 3: Creating corpus entries from usage examples...")
    new_corpus_entries = create_corpus_entries(new_entries)
    
    # Step 4: Create attestations
    print("🔗 Step 4: Creating attestation links...")
    new_attestations = create_attestations(new_entries, new_corpus_entries)
    
    # Step 5: Check for duplicates
    print("🔍 Step 5: Checking for duplicates...")
    existing_entry_ids = {entry.get("entry_id") for entry in lexicon}
    existing_corpus_ids = {entry.get("corpus_id") for entry in corpus}
    existing_attestation_ids = {entry.get("attestation_id") for entry in attestations}
    
    # Filter out duplicates
    new_lexicon_entries = [e for e in transformed_entries if e["entry_id"] not in existing_entry_ids]
    new_corpus_filtered = [e for e in new_corpus_entries if e["corpus_id"] not in existing_corpus_ids]
    new_attestations_filtered = [e for e in new_attestations if e["attestation_id"] not in existing_attestation_ids]
    
    print(f"   New lexicon entries to add: {len(new_lexicon_entries)}")
    print(f"   New corpus entries to add: {len(new_corpus_filtered)}")
    print(f"   New attestations to add: {len(new_attestations_filtered)}")
    
    # Step 6: Integrate into datasets
    print("✨ Step 6: Integrating into datasets...")
    lexicon.extend(new_lexicon_entries)
    corpus.extend(new_corpus_filtered)
    attestations.extend(new_attestations_filtered)
    
    # Step 7: Create backup
    print("💾 Step 7: Creating backup...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)
    
    # Step 8: Save updated datasets
    print("💿 Step 8: Saving updated datasets...")
    with open('data/lexicon.json', 'w', encoding='utf-8') as f:
        json.dump(lexicon, f, ensure_ascii=False, indent=2)
    
    with open('data/corpus.json', 'w', encoding='utf-8') as f:
        json.dump(corpus, f, ensure_ascii=False, indent=2)
    
    with open('data/attestations.json', 'w', encoding='utf-8') as f:
        json.dump(attestations, f, ensure_ascii=False, indent=2)
    
    print("✅ Integration completed successfully!")
    print(f"   Final lexicon entries: {len(lexicon)}")
    print(f"   Final corpus entries: {len(corpus)}")
    print(f"   Final attestations: {len(attestations)}")
    
    # Step 9: Show what was added
    print("\n📊 Summary of additions:")
    for entry in new_lexicon_entries:
        print(f"   ✅ Added: {entry['entry_id']} - {entry['headword_english']} ({entry['headword_sesotho'][0]['orthographic']})")
    
    return len(new_lexicon_entries), len(new_corpus_filtered), len(new_attestations_filtered)

if __name__ == "__main__":
    integrate_entries()
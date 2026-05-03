import json
import sys
import os

# Add project root to path to allow importing from pipeline.core
sys.path.append(os.getcwd())
from pipeline.core.linguistics import LinguisticKernel

def process_batch(lexicon_data, joined_data):
    # Initialize Kernel with taxonomy and orthography bridge
    taxonomy_path = "data/SEMANTIC_TAXONOMY.json"
    bridge_path = "data/REHABILITATION_BRIDGE.json"
    kernel = LinguisticKernel(taxonomy_path=taxonomy_path, bridge_path=bridge_path)
    processed_data = []
    
    # Map joined data by entry_id for fast lookup during audit
    joined_lookup = {item['entry_id']: item for item in joined_data if 'entry_id' in item}
    
    for entry in lexicon_data:
        # 1. Get Kernel Profile (Phases I-III)
        eng_hint = entry.get("headword_english", "")
        # Pass noun_class to get_profile for context (used in extract_root)
        profile = kernel.get_profile(entry.get("headword_sesotho", []), eng_hint)
        
        # Initialize morphology and metadata if missing
        if "morphology" not in entry: entry["morphology"] = {}
        if "metadata" not in entry: entry["metadata"] = {"flags": []}
        
        # 2. Check against Evidence (v450 Audit)
        joined_entry = joined_lookup.get(entry['entry_id'])
        if joined_entry and 'senses' in joined_entry:
            for sense in joined_entry['senses']:
                usage = sense.get('usage_example')
                if usage and usage.get('sesotho'):
                    # Pass noun_class to validate_concord
                    validation = kernel.validate_concord(profile['noun_class'], usage['sesotho'])
                    
                    if not validation['is_valid']:
                        entry['metadata']['flags'].append({
                            "type": "MATURITY_MISMATCH",
                            "suggested_class": validation['detected_class'],
                            "evidence_source": usage.get('source', 'Unknown'),
                            "evidence_text": usage['sesotho']
                        })
        
        # 3. Update entry with Kernel data
        entry['morphology'].update({
            "root": profile['root'],
            "noun_class": profile['noun_class']
        })
        
        # Protocol Phase IV Tags
        entry['metadata'].update({
            "rehabilitated": profile['rehabilitated'],
            "deconstructed": profile['deconstructed'],
            "source_maturity": profile['source_maturity'],
            "shift_detected": profile['shift_detected'] # Add shift_detected flag
        })
        
        if profile['is_diminutive']:
            entry['metadata']['flags'].append({"type": "DIMINUTIVE_DETECTED"})
        if profile['rehabilitated']:
            entry['metadata']['flags'].append({"type": "ORTHOGRAPHY_REHABILITATED"})
        if profile['deconstructed']:
            entry['metadata']['flags'].append({"type": "MORPHOLOGICAL_DECONSTRUCTION"})
        if profile['shift_detected']:
            entry['metadata']['flags'].append({"type": "CONSONANT_SHIFT_DETECTED"})
            
        processed_data.append(entry)
        
    return processed_data

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 puo-analyst-tagger.py <lexicon_json> <joined_json> [output_json]")
        sys.exit(1)
        
    lexicon_file = sys.argv[1]
    joined_file = sys.argv[2]
    output_file = sys.argv[3] if len(sys.argv) > 3 else "tagged_output.json"
    
    try:
        with open(lexicon_file, 'r') as f:
            lexicon_data = json.load(f)
        with open(joined_file, 'r') as f:
            joined_data = json.load(f)
            
        enriched_data = process_batch(lexicon_data, joined_data)
            
        with open(output_file, 'w') as f:
            json.dump(enriched_data, f, indent=2, ensure_ascii=False)
        
        print(f"Processed {len(enriched_data)} entries. Saved to {output_file}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

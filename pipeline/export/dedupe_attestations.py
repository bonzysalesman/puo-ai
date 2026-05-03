import argparse
import json
from typing import List, Dict

def dedupe_attestations(lexicon_path: str, attestations_path: str):
    with open(lexicon_path, "r", encoding="utf-8") as f:
        lexicon = json.load(f)
    with open(attestations_path, "r", encoding="utf-8") as f:
        attestations = json.load(f)

    # Get all active sense IDs from the lexicon
    active_sense_ids = set()
    for entry in lexicon:
        for sense in entry.get("senses", []):
            active_sense_ids.add(sense["sense_id"])

    # Group attestations by sense_id
    grouped = {}
    for att in attestations:
        sid = att["sense_id"]
        grouped.setdefault(sid, []).append(att)

    new_attestations = []
    pruned_count = 0

    for sid, group in grouped.items():
        if sid not in active_sense_ids:
            pruned_count += len(group)
            continue
            
        if len(group) == 1:
            new_attestations.append(group[0])
            continue
            
        # Priority logic for choosing the best attestation
        # 1. Prefer ones with a non-null score
        # 2. Prefer ones with 'manual_injection_v1' or 'enricher_split_v1' methods
        # 3. Prefer most recent (assuming they were appended)
        
        def score_att(a):
            method_score = 0
            m = a.get("method", "")
            if m == "manual_injection_v1": method_score = 100
            elif m == "enricher_split_v1": method_score = 50
            elif m == "normalization_migration_v1": method_score = 10
            
            val_score = a.get("score") if a.get("score") is not None else 0
            return (method_score, val_score)

        group.sort(key=score_att, reverse=True)
        best = group[0]
        new_attestations.append(best)
        pruned_count += (len(group) - 1)

    with open(attestations_path, "w", encoding="utf-8") as f:
        json.dump(new_attestations, f, ensure_ascii=False, indent=2)

    print(f"Deduplication complete. Pruned {pruned_count} redundant or orphan attestations.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Deduplicate attestations by sense_id.')
    parser.add_argument('--lexicon', default='data/lexicon.json')
    parser.add_argument('--attestations', default='data/attestations.json')
    args = parser.parse_args()
    dedupe_attestations(args.lexicon, args.attestations)

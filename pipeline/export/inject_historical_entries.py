import argparse
import json

from split_datasets import split_datasets


def load_json_array(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, list) else []


def _headword_key(entry):
    en = str(entry.get("headword_english", "")).strip().lower()
    st_list = entry.get("headword_sesotho", [])
    st = ""
    if isinstance(st_list, list) and st_list:
        first = st_list[0]
        if isinstance(first, dict):
            st = str(first.get("orthographic", "")).strip().lower()
    return en, st


def inject_staged_entries_split(
    lexicon_file,
    corpus_file,
    attestations_file,
    staged_files,
):
    lexicon = load_json_array(lexicon_file)
    corpus = load_json_array(corpus_file)
    attestations = load_json_array(attestations_file)

    existing_headword_keys = {
        _headword_key(entry) for entry in lexicon if isinstance(entry, dict)
    }
    existing_entry_by_en = {}
    for entry in lexicon:
        if not isinstance(entry, dict):
            continue
        en = str(entry.get("headword_english", "")).strip().lower()
        if en and en not in existing_entry_by_en:
            existing_entry_by_en[en] = entry
    existing_corpus_ids = {
        row.get("corpus_id")
        for row in corpus
        if isinstance(row, dict) and isinstance(row.get("corpus_id"), str)
    }
    existing_attestation_ids = {
        row.get("attestation_id")
        for row in attestations
        if isinstance(row, dict) and isinstance(row.get("attestation_id"), str)
    }

    injected_entries = 0
    injected_corpus = 0
    injected_attestations = 0
    merged_senses = 0
    total_processed = 0

    for staged_path in staged_files:
        staged = load_json_array(staged_path)
        staged_lexicon, staged_corpus, staged_attestations = split_datasets(staged)

        accepted_entry_ids = set()
        for entry in staged_lexicon:
            total_processed += 1
            key = _headword_key(entry)
            en_key = str(entry.get("headword_english", "")).strip().lower()
            if key in existing_headword_keys:
                if en_key and en_key in existing_entry_by_en:
                    # Merge senses for same headword instead of dropping alternate POS/definitions.
                    target = existing_entry_by_en[en_key]
                    target_senses = target.setdefault("senses", [])
                    existing_defs = {
                        str(s.get("definition_en", "")).strip().lower()
                        for s in target_senses
                        if isinstance(s, dict)
                    }
                    incoming_senses = entry.get("senses", [])
                    for sense in incoming_senses:
                        if not isinstance(sense, dict):
                            continue
                        d = str(sense.get("definition_en", "")).strip().lower()
                        if d and d not in existing_defs:
                            target_senses.append(sense)
                            existing_defs.add(d)
                            merged_senses += 1
                    # Merge POS tags where useful.
                    target_pos = target.setdefault("pos", [])
                    incoming_pos = entry.get("pos", [])
                    for p in incoming_pos:
                        if p not in target_pos:
                            target_pos.append(p)
                continue
            lexicon.append(entry)
            accepted_entry_ids.add(entry["entry_id"])
            existing_headword_keys.add(key)
            if en_key:
                existing_entry_by_en.setdefault(en_key, entry)
            injected_entries += 1

        accepted_sense_ids = {
            sense.get("sense_id")
            for entry in staged_lexicon
            if entry.get("entry_id") in accepted_entry_ids
            for sense in entry.get("senses", [])
            if isinstance(sense, dict) and isinstance(sense.get("sense_id"), str)
        }

        for row in staged_corpus:
            cid = row.get("corpus_id")
            if not isinstance(cid, str) or cid in existing_corpus_ids:
                continue
            corpus.append(row)
            existing_corpus_ids.add(cid)
            injected_corpus += 1

        for row in staged_attestations:
            aid = row.get("attestation_id")
            sid = row.get("sense_id")
            if not isinstance(aid, str) or aid in existing_attestation_ids:
                continue
            if sid not in accepted_sense_ids:
                continue
            attestations.append(row)
            existing_attestation_ids.add(aid)
            injected_attestations += 1

    with open(lexicon_file, "w", encoding="utf-8") as f:
        json.dump(lexicon, f, indent=2, ensure_ascii=False)
    with open(corpus_file, "w", encoding="utf-8") as f:
        json.dump(corpus, f, indent=2, ensure_ascii=False)
    with open(attestations_file, "w", encoding="utf-8") as f:
        json.dump(attestations, f, indent=2, ensure_ascii=False)

    print(f"Processed {total_processed} staged entries across files.")
    print(f"Injected entries: {injected_entries}")
    print(f"Merged senses into existing headwords: {merged_senses}")
    print(f"Injected corpus rows: {injected_corpus}")
    print(f"Injected attestations: {injected_attestations}")
    print(
        f"Updated '{lexicon_file}', '{corpus_file}', and '{attestations_file}'."
    )


def parse_args():
    parser = argparse.ArgumentParser(
        description="Inject staged historical entries into split datasets."
    )
    parser.add_argument("--lexicon", default="data/lexicon.json")
    parser.add_argument("--corpus", default="data/corpus.json")
    parser.add_argument("--attestations", default="data/attestations.json")
    parser.add_argument(
        "--staged-files",
        default="historical/staged/staged_casalis_a.json,historical/staged/staged_mabille_a.json",
        help="Comma-separated staged JSON files to inject.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    staged_files = [p.strip() for p in args.staged_files.split(",") if p.strip()]
    inject_staged_entries_split(
        lexicon_file=args.lexicon,
        corpus_file=args.corpus,
        attestations_file=args.attestations,
        staged_files=staged_files,
    )

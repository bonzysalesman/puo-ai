import argparse
import hashlib
import json
import re
from typing import Dict, Iterable, List, Tuple


def stable_hash(parts: Iterable[str], prefix: str, length: int = 16) -> str:
    joined = "|".join(parts)
    digest = hashlib.sha1(joined.encode("utf-8")).hexdigest()[:length]
    return f"{prefix}{digest}"


def parse_source(source: str) -> Tuple[str, str]:
    if not source:
        return "", ""
    text = source.strip()
    m = re.match(r"^(.*)\s+\(Verse\s+([^)]+)\)$", text)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    return text, ""


def normalize_lexicon(lexicon_path: str, corpus_path: str, attestations_path: str):
    with open(lexicon_path, "r", encoding="utf-8") as f:
        lexicon = json.load(f)
    with open(corpus_path, "r", encoding="utf-8") as f:
        corpus = json.load(f)
    with open(attestations_path, "r", encoding="utf-8") as f:
        attestations = json.load(f)

    corpus_index: Dict[Tuple[str, str, str, str], str] = {}
    for row in corpus:
        key = (
            str(row.get("source", "")).strip(),
            str(row.get("ref", "")).strip(),
            str(row.get("sesotho_text", "")).strip(),
            str(row.get("english_text", "")).strip(),
        )
        corpus_index[key] = row["corpus_id"]

    attestation_ids = {row["attestation_id"] for row in attestations}

    migrated_count = 0
    for entry in lexicon:
        for sense in entry.get("senses", []):
            example = sense.pop("usage_example", None)
            if not example:
                continue

            st_text = str(example.get("sesotho", "")).strip()
            en_text = str(example.get("english", "")).strip()
            source_raw = str(example.get("source", "")).strip()
            source_label, ref = parse_source(source_raw)

            if not (st_text and en_text):
                continue

            corpus_key = (source_label, ref, st_text, en_text)
            corpus_id = corpus_index.get(corpus_key)
            if corpus_id is None:
                corpus_id = stable_hash(
                    [source_label, ref, st_text, en_text], prefix="corpus_"
                )
                corpus_index[corpus_key] = corpus_id
                corpus.append(
                    {
                        "corpus_id": corpus_id,
                        "source": source_label,
                        "ref": ref,
                        "sesotho_text": st_text,
                        "english_text": en_text,
                    }
                )

            sense_id = sense["sense_id"]
            attestation_id = stable_hash([sense_id, corpus_id], prefix="att_")
            if attestation_id not in attestation_ids:
                attestations.append(
                    {
                        "attestation_id": attestation_id,
                        "sense_id": sense_id,
                        "corpus_id": corpus_id,
                        "source_raw": source_raw,
                        "match_terms": sense.get("sesotho_term", []),
                        "score": None,
                        "method": "normalization_migration_v1",
                    }
                )
                attestation_ids.add(attestation_id)
            migrated_count += 1

    if migrated_count > 0:
        with open(lexicon_path, "w", encoding="utf-8") as f:
            json.dump(lexicon, f, ensure_ascii=False, indent=2)
        with open(corpus_path, "w", encoding="utf-8") as f:
            json.dump(corpus, f, ensure_ascii=False, indent=2)
        with open(attestations_path, "w", encoding="utf-8") as f:
            json.dump(attestations, f, ensure_ascii=False, indent=2)

    print(f"Migrated {migrated_count} usage examples from lexicon to corpus/attestations.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Normalize lexicon by moving usage_example to split datasets.")
    parser.add_argument("--lexicon", default="data/lexicon.json")
    parser.add_argument("--corpus", default="data/corpus.json")
    parser.add_argument("--attestations", default="data/attestations.json")
    args = parser.parse_args()
    normalize_lexicon(args.lexicon, args.corpus, args.attestations)

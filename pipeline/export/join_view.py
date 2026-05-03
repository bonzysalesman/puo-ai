import argparse
import json
from copy import deepcopy
from typing import Dict, List


def load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_score(value):
    if isinstance(value, (int, float)):
        return float(value)
    return None


def choose_best_attestation(rows: List[Dict]) -> Dict:
    # Prefer highest explicit score; otherwise stable fallback by attestation_id.
    def key(row: Dict):
        score = parse_score(row.get("score"))
        return (score is not None, score if score is not None else -1.0, row.get("attestation_id", ""))

    return sorted(rows, key=key, reverse=True)[0]


def build_usage_example(corpus_row: Dict, source_raw: str) -> Dict:
    source = source_raw.strip() if isinstance(source_raw, str) and source_raw.strip() else ""
    if not source:
        source_label = str(corpus_row.get("source", "")).strip()
        ref = str(corpus_row.get("ref", "")).strip()
        if source_label and ref:
            source = f"{source_label} (Verse {ref})"
        else:
            source = source_label or ref
    return {
        "sesotho": str(corpus_row.get("sesotho_text", "")).strip(),
        "english": str(corpus_row.get("english_text", "")).strip(),
        "source": source,
    }


def join_view(lexicon: List[Dict], corpus: List[Dict], attestations: List[Dict]) -> List[Dict]:
    corpus_by_id = {}
    for row in corpus:
        cid = row.get("corpus_id")
        if isinstance(cid, str) and cid:
            corpus_by_id[cid] = row

    att_by_sense = {}
    for row in attestations:
        sid = row.get("sense_id")
        cid = row.get("corpus_id")
        if not (isinstance(sid, str) and sid and isinstance(cid, str) and cid):
            continue
        if cid not in corpus_by_id:
            continue
        att_by_sense.setdefault(sid, []).append(row)

    out = deepcopy(lexicon)
    for entry in out:
        senses = entry.get("senses", [])
        if not isinstance(senses, list):
            continue
        for sense in senses:
            sid = sense.get("sense_id")
            if not isinstance(sid, str) or sid not in att_by_sense:
                continue
            best = choose_best_attestation(att_by_sense[sid])
            corpus_row = corpus_by_id[best["corpus_id"]]
            sense["usage_example"] = build_usage_example(
                corpus_row, str(best.get("source_raw", ""))
            )
    return out


def parse_args():
    parser = argparse.ArgumentParser(
        description="Join lexicon+corpus+attestations into a backward-compatible dictionary view."
    )
    parser.add_argument("--lexicon", default="data/lexicon.json")
    parser.add_argument("--corpus", default="data/corpus.json")
    parser.add_argument("--attestations", default="data/attestations.json")
    parser.add_argument("--output", default="data/dictionary.joined.json")
    return parser.parse_args()


def main():
    args = parse_args()
    lexicon = load_json(args.lexicon)
    corpus = load_json(args.corpus)
    attestations = load_json(args.attestations)
    joined = join_view(lexicon, corpus, attestations)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(joined, f, ensure_ascii=False, indent=2)
    print(f"Joined entries: {len(joined)} -> {args.output}")


if __name__ == "__main__":
    main()

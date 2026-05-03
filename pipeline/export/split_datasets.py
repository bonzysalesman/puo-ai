import argparse
import hashlib
import json
import re
from typing import Dict, Iterable, List, Tuple


def stable_hash(parts: Iterable[str], prefix: str, length: int = 16) -> str:
    joined = "|".join(parts)
    digest = hashlib.sha1(joined.encode("utf-8")).hexdigest()[:length]
    return f"{prefix}{digest}"


def to_string_list(value) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        text = value.strip()
        return [text] if text else []
    if isinstance(value, list):
        out = []
        for item in value:
            if isinstance(item, str):
                text = item.strip()
                if text:
                    out.append(text)
        return out
    return []


def normalize_headword_english(value) -> str:
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, list):
        for item in value:
            if isinstance(item, str) and item.strip():
                return item.strip()
    return ""


def normalize_headword_sesotho(value) -> List[Dict[str, str]]:
    normalized = []
    if isinstance(value, dict):
        value = [value]
    if not isinstance(value, list):
        return normalized

    for item in value:
        if isinstance(item, str):
            orth = item.strip()
            if not orth:
                continue
            normalized.append(
                {
                    "orthographic": orth,
                    "tone_marked": "",
                    "ipa": "",
                    "tone_pattern": "",
                }
            )
            continue

        if not isinstance(item, dict):
            continue

        orth = str(item.get("orthographic", "")).strip()
        if not orth:
            continue
        normalized.append(
            {
                "orthographic": orth,
                "tone_marked": str(item.get("tone_marked", "")).strip(),
                "ipa": str(item.get("ipa", "")).strip(),
                "tone_pattern": str(item.get("tone_pattern", "")).strip(),
            }
        )
    return normalized


def ensure_entry_id(entry: Dict, index: int) -> str:
    existing = entry.get("entry_id")
    if isinstance(existing, str) and existing.strip():
        return existing.strip()
    en = normalize_headword_english(entry.get("headword_english"))
    st_items = normalize_headword_sesotho(entry.get("headword_sesotho"))
    st = st_items[0]["orthographic"] if st_items else ""
    return stable_hash([str(index), en, st], prefix="entry_")


def ensure_sense_id(entry_id: str, sense: Dict, sense_index: int) -> str:
    for key in ("sense_id", "id"):
        value = sense.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return f"{entry_id}.sense_{sense_index + 1}"


def parse_source(source: str) -> Tuple[str, str]:
    if not source:
        return "", ""
    text = source.strip()
    m = re.match(r"^(.*)\s+\(Verse\s+([^)]+)\)$", text)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    return text, ""


def extract_usage_examples(sense: Dict) -> List[Dict[str, str]]:
    examples = []
    one = sense.get("usage_example")
    if isinstance(one, dict):
        examples.append(one)

    many = sense.get("usage_examples")
    if isinstance(many, list):
        for item in many:
            if isinstance(item, dict):
                examples.append(item)
    return examples


def normalize_sense(entry_id: str, sense: Dict, sense_index: int, hw_sesotho: List[Dict[str, str]]) -> Dict:
    sense_id = ensure_sense_id(entry_id, sense, sense_index)
    definition = sense.get("definition_en")
    if not isinstance(definition, str):
        definition = sense.get("definition")
    if not isinstance(definition, str):
        definition = ""

    terms = to_string_list(sense.get("sesotho_term"))
    if not terms and hw_sesotho:
        terms = [hw_sesotho[0]["orthographic"]]

    out = {
        "sense_id": sense_id,
        "definition_en": definition.strip(),
        "sesotho_term": terms,
    }
    return out


def split_datasets(dictionary: List[Dict]) -> Tuple[List[Dict], List[Dict], List[Dict]]:
    lexicon = []
    corpus = []
    attestations = []
    corpus_index: Dict[Tuple[str, str, str, str], str] = {}

    for i, raw_entry in enumerate(dictionary):
        if not isinstance(raw_entry, dict):
            continue

        entry_id = ensure_entry_id(raw_entry, i)
        headword_en = normalize_headword_english(raw_entry.get("headword_english"))
        headword_st = normalize_headword_sesotho(raw_entry.get("headword_sesotho"))
        pos = to_string_list(raw_entry.get("pos"))
        syllables = to_string_list(raw_entry.get("syllables"))
        if not syllables and headword_st:
            syllables = [headword_st[0]["orthographic"]]

        morphology = raw_entry.get("morphology")
        if not isinstance(morphology, dict):
            morphology = {}
        morphology = {
            "root": str(morphology.get("root", "")).strip(),
            "derivation": str(morphology.get("derivation", "Historical Entry")).strip(),
            "noun_class": str(morphology.get("noun_class", "unknown")).strip(),
        }

        thes = raw_entry.get("thesaurus")
        if not isinstance(thes, dict):
            thes = {}
        thesaurus = {
            "synonyms_en": to_string_list(thes.get("synonyms_en")),
            "antonyms_en": to_string_list(thes.get("antonyms_en")),
            "synonyms_st": to_string_list(thes.get("synonyms_st")),
            "antonyms_st": to_string_list(thes.get("antonyms_st")),
        }

        raw_senses = raw_entry.get("senses", [])
        if not isinstance(raw_senses, list):
            raw_senses = []

        senses = []
        for j, raw_sense in enumerate(raw_senses):
            if not isinstance(raw_sense, dict):
                continue
            sense = normalize_sense(entry_id, raw_sense, j, headword_st)
            senses.append(sense)

            examples = extract_usage_examples(raw_sense)
            for ex in examples:
                st_text = str(ex.get("sesotho", "")).strip()
                en_text = str(ex.get("english", "")).strip()
                source_raw = str(ex.get("source", "")).strip()
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

                attestation_id = stable_hash(
                    [sense["sense_id"], corpus_id], prefix="att_"
                )
                attestations.append(
                    {
                        "attestation_id": attestation_id,
                        "sense_id": sense["sense_id"],
                        "corpus_id": corpus_id,
                        "source_raw": source_raw,
                        "match_terms": sense["sesotho_term"],
                        "score": None,
                        "method": "historical_split_v1",
                    }
                )

        lex_entry = {
            "entry_id": entry_id,
            "headword_english": headword_en,
            "pos": pos,
            "headword_sesotho": headword_st,
            "syllables": syllables,
            "morphology": morphology,
            "senses": senses,
            "thesaurus": thesaurus,
        }
        if "related_words" in raw_entry:
            lex_entry["related_words"] = to_string_list(raw_entry.get("related_words"))
        lexicon.append(lex_entry)

    return lexicon, corpus, attestations


def load_dictionary(path: str) -> List[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    entries = data.get("entries", [])
    return entries if isinstance(entries, list) else []


def write_json(path: str, payload: List[Dict]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Split mixed dictionary data into lexicon, corpus, and attestation datasets."
    )
    parser.add_argument("--dictionary", default="data/dictionary.json")
    parser.add_argument("--lexicon-out", default="data/lexicon.json")
    parser.add_argument("--corpus-out", default="data/corpus.json")
    parser.add_argument("--attestations-out", default="data/attestations.json")
    return parser.parse_args()


def main():
    args = parse_args()
    dictionary = load_dictionary(args.dictionary)
    lexicon, corpus, attestations = split_datasets(dictionary)
    write_json(args.lexicon_out, lexicon)
    write_json(args.corpus_out, corpus)
    write_json(args.attestations_out, attestations)
    print(f"Lexicon entries: {len(lexicon)} -> {args.lexicon_out}")
    print(f"Corpus verses: {len(corpus)} -> {args.corpus_out}")
    print(f"Attestations: {len(attestations)} -> {args.attestations_out}")


if __name__ == "__main__":
    main()

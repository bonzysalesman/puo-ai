#!/usr/bin/env python3
"""
stage_mabille_a.py
------------------
Converts the flat-format entries extracted from the Mabille Batch A OCR
(mabille_a_cleaned.json) into the full schema format expected by
inject_historical_entries.py.

Input format:
  {
    "headword_sesotho": "Abula",
    "pos": "v. n.",
    "definition_en": "to crawl on hands and feet, to cringe. ..."
  }

Output format (full schema, inject-ready):
  {
    "entry_id": "st_MAB_A_<hash>",
    "headword_english": "",
    "pos": [{"tag": "v. n.", "full": "verb neuter"}],
    "headword_sesotho": [{"orthographic": "Abula", "tone_marked": "", "ipa": "", "tone_pattern": ""}],
    "syllables": [],
    "morphology": {"root": "Abula", "noun_class": null, "derivation": "Historical Entry (Mabille)"},
    "senses": [{
      "sense_id": "st_MAB_A_<hash>_s1",
      "definition_en": "to crawl on hands and feet, to cringe. ...",
      "sesotho_term": ["Abula"]
    }],
    "thesaurus": {}
  }
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# POS mapping
# ---------------------------------------------------------------------------

POS_MAP = {
    "n.": ("n.", "noun"),
    "v.": ("v.", "verb"),
    "v. n.": ("v. n.", "verb neuter"),
    "v. t.": ("v. t.", "verb transitive"),
    "adj.": ("adj.", "adjective"),
    "adv.": ("adv.", "adverb"),
    "prep.": ("prep.", "preposition"),
    "conj.": ("conj.", "conjunction"),
    "interj.": ("interj.", "interjection"),
    "pron.": ("pron.", "pronoun"),
    "v. i.": ("v. n.", "verb neuter"),  # mapping intransitive to neuter for consistency
}


def map_pos(raw: str) -> list:
    raw = raw.strip()
    tag, full = POS_MAP.get(raw, (raw, "unknown"))
    return [{"tag": tag, "full": full}]


def stable_hash(text: str, length: int = 8) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:length]


# ---------------------------------------------------------------------------
# Entry construction
# ---------------------------------------------------------------------------

def build_entry(flat: dict) -> dict:
    hw_st = flat["headword_sesotho"].strip()
    pos_raw = flat.get("pos", "").strip()
    def_en = flat.get("definition_en", "").strip()

    uid = stable_hash(f"{hw_st}|{def_en}")
    entry_id = f"st_MAB_A_{uid}"
    sense_id = f"{entry_id}_s1"

    # Build headword_sesotho list
    hw_sesotho = [
        {
            "orthographic": hw_st,
            "tone_marked": "",
            "ipa": "",
            "tone_pattern": "",
        }
    ]

    sense = {
        "sense_id": sense_id,
        "definition_en": def_en,
        "sesotho_term": [hw_st],
        "usage_example": None
    }

    return {
        "entry_id": entry_id,
        "headword_english": "",  # To be enriched later
        "pos": map_pos(pos_raw),
        "headword_sesotho": hw_sesotho,
        "syllables": [],
        "morphology": {
            "root": hw_st,
            "noun_class": None,
            "derivation": "Historical Entry (Mabille)",
        },
        "senses": [sense],
        "thesaurus": {},
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        default="historical/mabille/mabille_a_cleaned.json",
        help="Path to the cleaned Mabille entries JSON",
    )
    parser.add_argument(
        "--output",
        default="historical/staged/staged_mabille_a_final.json",
        help="Where to write the staged full-schema entries",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        print(f"ERROR: {input_path} not found", file=sys.stderr)
        sys.exit(1)

    with open(input_path, encoding="utf-8") as f:
        all_entries = json.load(f)

    print(f"Found {len(all_entries)} entries to stage")

    staged = []
    for entry in all_entries:
        if not entry.get("headword_sesotho", "").strip():
            continue
        staged.append(build_entry(entry))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(staged, f, indent=2, ensure_ascii=False)

    print(f"Staged:  {len(staged)} entries → {output_path}")

    # Preview
    print("\nFirst 5 staged entries:")
    for e in staged[:5]:
        st = e["headword_sesotho"][0]["orthographic"]
        pos = e["pos"][0]["tag"]
        print(f"  {e['entry_id']}  {st:20} ({pos})")


if __name__ == "__main__":
    main()

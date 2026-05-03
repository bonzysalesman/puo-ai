#!/usr/bin/env python3
"""
stage_conversation_flat.py
--------------------------
Converts the 80 flat-format entries extracted from the Gemini conversation
(data-ss-ls.md) into the full schema format expected by inject_historical_entries.py.

Input format (flat Casalis/modern):
  {
    "headword_english": "Cage",
    "pos": "n.",
    "sesotho": "sehlahla, ntlo ea linonyana.",
    "source": { "page_index": 30, ... }   ← optional
  }

Output format (full schema, inject-ready):
  {
    "entry_id": "conv_flat_<hash>",
    "headword_english": "Cage",
    "pos": [{"tag": "n.", "full": "noun"}],
    "headword_sesotho": [{"orthographic": "sehlahla", "tone_marked": "sehlahla", "ipa": "", "tone_pattern": ""}],
    "syllables": [],
    "morphology": {"root": "sehlahla", "noun_class": null, "derivation": ""},
    "senses": [{
      "sense_id": "conv_flat_<hash>_s1",
      "definition_en": "Sesotho: sehlahla, ntlo ea linonyana.",
      "sesotho_term": ["sehlahla", "ntlo ea linonyana"],
      "usage_example": null           ← omitted; no corpus match possible without Bible HTML
    }],
    "thesaurus": {}
  }

Usage:
    python3 pipeline/staging/stage_conversation_flat.py \
        --input reports/new_entries_from_conversation.json \
        --output historical/staged/staged_conversation_flat.json
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
    "adj.": ("adj.", "adjective"),
    "adv.": ("adv.", "adverb"),
    "prep.": ("prep.", "preposition"),
    "conj.": ("conj.", "conjunction"),
    "interj.": ("interj.", "interjection"),
    "pron.": ("pron.", "pronoun"),
    "n./v.": ("n./v.", "noun or verb"),
    "v./n.": ("v./n.", "verb or noun"),
    "n. (digital)": ("n.", "noun"),
}


def map_pos(raw: str) -> list:
    raw = raw.strip()
    tag, full = POS_MAP.get(raw, (raw, "unknown"))
    return [{"tag": tag, "full": full}]


# ---------------------------------------------------------------------------
# Sesotho term extraction
# ---------------------------------------------------------------------------

def extract_sesotho_terms(sesotho_def: str) -> list[str]:
    """
    Pull primary Sesotho terms from a raw definition string.
    Splits on ';' first (separates alternatives/examples), then ',' within
    the first part (synonyms). Strips parenthetical annotations.
    """
    if not sesotho_def:
        return []
    # Take only the part before the first semicolon
    primary = sesotho_def.split(";")[0]
    # Remove parenthetical glosses like "(of fire)"
    primary = re.sub(r"\(.*?\)", "", primary)
    # Split synonyms by comma
    terms = [t.strip() for t in primary.split(",")]
    # Filter: remove empty, remove tokens that start with "ho " only if they
    # look like full verb phrases (common artefact in Casalis data)
    cleaned = []
    for t in terms:
        t = re.sub(r"\s+", " ", t).strip()
        # Strip trailing periods/commas left by OCR
        t = t.rstrip(".,;:")
        # Skip tokens that are just particles or very short noise
        if len(t) < 2:
            continue
        # Remove leading "v." / "n." leakage that sometimes appears
        t = re.sub(r"^(v\.|n\.|adj\.)\s+", "", t)
        t = t.strip()
        if t:
            cleaned.append(t)
    return cleaned


def stable_hash(text: str, length: int = 8) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:length]


# ---------------------------------------------------------------------------
# Entry construction
# ---------------------------------------------------------------------------

def build_entry(flat: dict) -> dict:
    hw_en = flat["headword_english"].strip()
    pos_raw = flat.get("pos", "n.").strip()
    sesotho_raw = flat.get("sesotho", "").strip()
    source = flat.get("source")

    uid = stable_hash(f"{hw_en}|{sesotho_raw}")
    entry_id = f"conv_flat_{uid}"
    sense_id = f"{entry_id}_s1"

    terms = extract_sesotho_terms(sesotho_raw)
    primary_term = terms[0] if terms else hw_en.lower()

    # Build headword_sesotho list
    hw_sesotho = [
        {
            "orthographic": t,
            "tone_marked": t,
            "ipa": "",
            "tone_pattern": "",
        }
        for t in terms
    ] or [
        {
            "orthographic": primary_term,
            "tone_marked": primary_term,
            "ipa": "",
            "tone_pattern": "",
        }
    ]

    # Definition — use raw Sesotho definition as the English gloss
    definition_en = f"{sesotho_raw}" if sesotho_raw else hw_en

    # Build source note for sense
    source_note = ""
    if source and isinstance(source, dict):
        pg = source.get("page_number", source.get("page_index", ""))
        col = source.get("column", "")
        source_note = f"Casalis p.{pg} ({col})" if pg else "Casalis OCR"

    sense = {
        "sense_id": sense_id,
        "definition_en": definition_en,
        "sesotho_term": terms,
        "usage_example": {
            "sesotho": sesotho_raw,
            "english": hw_en,
            "source": source_note or "Gemini conversation extract",
        },
    }

    return {
        "entry_id": entry_id,
        "headword_english": hw_en,
        "pos": map_pos(pos_raw),
        "headword_sesotho": hw_sesotho,
        "syllables": [],
        "morphology": {
            "root": primary_term,
            "noun_class": None,
            "derivation": "",
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
        default="reports/new_entries_from_conversation.json",
        help="Path to the extracted entries JSON from extract_from_conversation.py",
    )
    parser.add_argument(
        "--output",
        default="historical/staged/staged_conversation_flat.json",
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

    # Filter to flat-only entries
    flat_entries = [
        e for e in all_entries
        if "senses" not in e and "entry_id" not in e and "headword_sesotho" not in e
    ]

    print(f"Found {len(flat_entries)} flat entries to stage")

    staged = []
    skipped = []
    for entry in flat_entries:
        if not entry.get("headword_english", "").strip():
            skipped.append(entry)
            continue
        staged.append(build_entry(entry))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(staged, f, indent=2, ensure_ascii=False)

    print(f"Staged:  {len(staged)} entries → {output_path}")
    if skipped:
        print(f"Skipped: {len(skipped)} (missing headword_english)")

    # Preview
    print("\nFirst 5 staged entries:")
    for e in staged[:5]:
        st = e["headword_sesotho"][0]["orthographic"] if e["headword_sesotho"] else "?"
        print(f"  {e['entry_id']}  {e['headword_english']:30} → {st}")


if __name__ == "__main__":
    main()

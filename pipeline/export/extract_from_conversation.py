#!/usr/bin/env python3
"""
extract_from_conversation.py
----------------------------
Extracts structured lexicon entry blocks from a Gemini conversation markdown
file (data-ss-ls.md) and compares them against the current lexicon.json to
identify net-new entries not yet injected.

Usage:
    python3 pipeline/export/extract_from_conversation.py \
        --input ~/Downloads/data-ss-ls.md \
        --lexicon data/lexicon.json \
        --output-new reports/new_entries_from_conversation.json \
        --output-report reports/conversation_extraction_report.md

Two entry formats are handled:
  FORMAT A — Full schema (has entry_id, headword_sesotho, senses):
    { "entry_id": "st_G1_01", "headword_english": "Beginning", "senses": [...] }

  FORMAT B — Flat Casalis/OCR (has sesotho + source.page_index):
    { "headword_english": "Branch", "pos": "n.", "sesotho": "lekala.", "source": {...} }
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# JSON block extraction
# ---------------------------------------------------------------------------

def extract_json_blocks(text: str) -> list[str]:
    """
    Walk the text and collect every top-level JSON array or object block
    that immediately follows a bare 'JSON' line (the pattern Gemini uses).
    Also captures fenced ```json ... ``` blocks.

    Returns a list of raw JSON strings.
    """
    blocks = []

    # Pattern 1: bare 'JSON\n' followed by '[' or '{'
    # We find the marker, then grab balanced brackets.
    lines = text.splitlines(keepends=True)
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()

        # Gemini bare marker
        trigger = stripped in ("JSON", "json")

        # Fenced block  ```json or ```JSON
        fenced = re.match(r"^```\s*[Jj][Ss][Oo][Nn]\s*$", stripped)

        if trigger or fenced:
            # Find the start of the JSON value on the next non-blank line
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1

            if j >= len(lines):
                i += 1
                continue

            first_char = lines[j].strip()[0] if lines[j].strip() else ""
            if first_char not in ("[", "{"):
                i += 1
                continue

            # Collect until brackets balance (or fenced block ends)
            opener = "[" if first_char == "[" else "{"
            closer = "]" if opener == "[" else "}"
            depth = 0
            buf = []
            k = j

            if fenced:
                # Read until closing ```
                k = j
                while k < len(lines):
                    line = lines[k]
                    if re.match(r"^```\s*$", line.strip()) and k > j:
                        break
                    buf.append(line)
                    k += 1
            else:
                while k < len(lines):
                    line = lines[k]
                    depth += line.count(opener) - line.count(closer)
                    buf.append(line)
                    if depth <= 0:
                        break
                    k += 1

            raw = "".join(buf).strip()
            if raw:
                blocks.append(raw)

            i = k + 1
            continue

        i += 1

    return blocks


# ---------------------------------------------------------------------------
# Entry normalisation
# ---------------------------------------------------------------------------

def normalise_entry(obj: dict) -> Optional[dict]:
    """
    Normalise a raw parsed object into a minimal comparable dict with:
      - headword_english  (str)
      - format            ('full' | 'flat')
      - entry_id          (str | None)
      - pos               (str)
      - headword_sesotho  (list of orthographic strings)
      - senses            (list)
      - raw               (original dict)
    """
    hw_en = obj.get("headword_english", "").strip()
    if not hw_en:
        return None

    fmt = "full" if ("entry_id" in obj or "senses" in obj or "headword_sesotho" in obj) else "flat"

    # Headword sesotho
    if fmt == "full":
        hw_st_raw = obj.get("headword_sesotho", [])
        if isinstance(hw_st_raw, list):
            hw_st = [h.get("orthographic", "") for h in hw_st_raw if isinstance(h, dict)]
        else:
            hw_st = []
    else:
        raw_sesotho = obj.get("sesotho", "")
        # First token before ; or , is the primary form
        primary = re.split(r"[;,]", raw_sesotho)[0].strip()
        # Strip leading "ho " for verbs
        hw_st = [primary] if primary else []

    # POS
    pos_raw = obj.get("pos", "")
    if isinstance(pos_raw, list):
        pos = ", ".join(p.get("tag", "") if isinstance(p, dict) else str(p) for p in pos_raw)
    else:
        pos = str(pos_raw)

    return {
        "headword_english": hw_en,
        "format": fmt,
        "entry_id": obj.get("entry_id"),
        "pos": pos,
        "headword_sesotho": hw_st,
        "senses": obj.get("senses", []),
        "raw": obj,
    }


def parse_blocks(blocks: list) -> tuple:
    """
    Parse raw JSON strings into normalised entry dicts.
    Returns (entries, errors).
    """
    entries = []
    errors = []

    for raw in blocks:
        # Strip trailing commas at the end of the block
        raw = re.sub(r",\s*$", "", raw)
        
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as e:
            # Try to recover by stripping trailing commas (common in chat-generated JSON)
            cleaned = re.sub(r",\s*([}\]])", r"\1", raw)
            
            # Try to recover from concatenated JSON objects (e.g. {...} {...})
            cleaned = re.sub(r"}\s*\{", "}, {", cleaned)
            if cleaned.strip().startswith("{") and "}, {" in cleaned:
                cleaned = "[" + cleaned + "]"
                
            try:
                parsed = json.loads(cleaned)
            except json.JSONDecodeError as e2:
                errors.append(f"JSON parse error: {e2} (original: {e}) | snippet: {raw[:80]!r}")
                continue

        if isinstance(parsed, list):
            items = parsed
        elif isinstance(parsed, dict):
            items = [parsed]
        else:
            continue

        for item in items:
            if not isinstance(item, dict):
                continue
            norm = normalise_entry(item)
            if norm:
                entries.append(norm)

    return entries, errors


# ---------------------------------------------------------------------------
# Lexicon loading
# ---------------------------------------------------------------------------

def load_lexicon_headwords(lexicon_path: Path) -> set[str]:
    """Return a set of normalised English headwords already in lexicon.json."""
    with open(lexicon_path) as f:
        lex = json.load(f)

    if isinstance(lex, list):
        items = lex
    elif isinstance(lex, dict):
        items = lex.get("entries", list(lex.values()))
    else:
        return set()

    headwords = set()
    for entry in items:
        hw = entry.get("headword_english", "").strip().lower()
        if hw:
            headwords.add(hw)
    return headwords


# ---------------------------------------------------------------------------
# Diff & reporting
# ---------------------------------------------------------------------------

def diff_against_lexicon(
    entries: list[dict],
    lexicon_headwords: set[str],
) -> tuple[list[dict], list[dict]]:
    """
    Split entries into (new_entries, already_in_lexicon).
    Matching is case-insensitive on headword_english.
    """
    new_entries = []
    existing = []
    seen = set()

    for entry in entries:
        key = entry["headword_english"].lower()
        if key in lexicon_headwords:
            existing.append(entry)
        elif key not in seen:
            new_entries.append(entry)
            seen.add(key)
        # duplicates within conversation file are silently deduplicated

    return new_entries, existing


def build_report(
    total_blocks: int,
    total_entries: int,
    parse_errors: list[str],
    new_entries: list[dict],
    existing: list[dict],
    output_new: Path,
    output_report: Path,
) -> str:
    fmt_counts = defaultdict(int)
    for e in new_entries:
        fmt_counts[e["format"]] += 1

    lines = [
        "# Conversation Extraction Report",
        "",
        "## Summary",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| JSON blocks found | {total_blocks} |",
        f"| Entries parsed | {total_entries} |",
        f"| Parse errors | {len(parse_errors)} |",
        f"| Already in lexicon | {len(existing)} |",
        f"| **Net-new entries** | **{len(new_entries)}** |",
        f"| · Full-schema format | {fmt_counts['full']} |",
        f"| · Flat Casalis format | {fmt_counts['flat']} |",
        "",
    ]

    if parse_errors:
        lines += ["## Parse Errors", ""]
        for err in parse_errors[:20]:
            lines.append(f"- `{err}`")
        if len(parse_errors) > 20:
            lines.append(f"- … and {len(parse_errors) - 20} more")
        lines.append("")

    lines += [
        "## Net-New Entries (not in lexicon.json)",
        "",
        f"Saved to: `{output_new}`",
        "",
        "| # | Headword (EN) | Format | POS | Sesotho |",
        "|---|---------------|--------|-----|---------|",
    ]
    for i, e in enumerate(new_entries, 1):
        st = ", ".join(e["headword_sesotho"]) or "—"
        lines.append(f"| {i} | {e['headword_english']} | {e['format']} | {e['pos']} | {st} |")

    lines += [
        "",
        "## Already in Lexicon (skipped)",
        "",
        ", ".join(sorted(e["headword_english"] for e in existing)) or "None",
        "",
    ]

    report = "\n".join(lines)
    output_report.parent.mkdir(parents=True, exist_ok=True)
    output_report.write_text(report, encoding="utf-8")
    return report


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        default=str(Path.home() / "Downloads/data-ss-ls.md"),
        help="Path to the Gemini conversation markdown file",
    )
    parser.add_argument(
        "--lexicon",
        default="data/lexicon.json",
        help="Path to current lexicon.json",
    )
    parser.add_argument(
        "--output-new",
        default="reports/new_entries_from_conversation.json",
        help="Where to write net-new entries as JSON",
    )
    parser.add_argument(
        "--output-report",
        default="reports/conversation_extraction_report.md",
        help="Where to write the summary report",
    )
    parser.add_argument(
        "--format-filter",
        choices=["full", "flat", "all"],
        default="all",
        help="Only output entries of this format type",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
    )
    args = parser.parse_args()

    input_path = Path(args.input).expanduser()
    lexicon_path = Path(args.lexicon)
    output_new = Path(args.output_new)
    output_report = Path(args.output_report)

    if not input_path.exists():
        print(f"ERROR: input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    if not lexicon_path.exists():
        print(f"ERROR: lexicon not found: {lexicon_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Reading conversation file ({input_path.stat().st_size // 1024} KB)…")
    text = input_path.read_text(encoding="utf-8", errors="replace")

    print("Extracting JSON blocks…")
    blocks = extract_json_blocks(text)
    print(f"  Found {len(blocks)} blocks")

    print("Parsing entries…")
    entries, errors = parse_blocks(blocks)
    print(f"  Parsed {len(entries)} entries, {len(errors)} errors")

    print("Loading lexicon…")
    lexicon_headwords = load_lexicon_headwords(lexicon_path)
    print(f"  Lexicon has {len(lexicon_headwords)} headwords")

    print("Diffing…")
    new_entries, existing = diff_against_lexicon(entries, lexicon_headwords)

    # Apply format filter
    if args.format_filter != "all":
        new_entries = [e for e in new_entries if e["format"] == args.format_filter]

    print(f"  Net-new: {len(new_entries)}, already in lexicon: {len(existing)}")

    # Write new entries JSON (raw originals, not normalised wrappers)
    output_new.parent.mkdir(parents=True, exist_ok=True)
    raw_new = [e["raw"] for e in new_entries]
    with open(output_new, "w", encoding="utf-8") as f:
        json.dump(raw_new, f, ensure_ascii=False, indent=2)
    print(f"  Wrote {len(raw_new)} new entries → {output_new}")

    # Build report
    report = build_report(
        total_blocks=len(blocks),
        total_entries=len(entries),
        parse_errors=errors,
        new_entries=new_entries,
        existing=existing,
        output_new=output_new,
        output_report=output_report,
    )
    print(f"  Report → {output_report}")

    if args.verbose and errors:
        print("\nParse errors:")
        for err in errors:
            print(f"  {err}")

    print("\nDone.")


if __name__ == "__main__":
    main()

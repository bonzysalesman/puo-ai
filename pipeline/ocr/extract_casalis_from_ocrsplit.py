import argparse
import json
import re
from pathlib import Path


ENTRY_RE = re.compile(
    r"^\s*[-+.\|'`‘’\[\](){}]*\s*([A-Za-z][A-Za-z'’-]{1,40})\s*[,;:.]\s*(.*)$"
)

POS_MAP = {
    "n": "n.",
    "v": "v.",
    "adj": "adj.",
    "adv": "adv.",
    "prep": "prep.",
    "conj": "conj.",
    "interj": "interj.",
}


def normalize_headword(raw):
    hw = re.sub(r"^[^A-Za-z]+", "", raw).strip()
    if not hw:
        return ""
    # Common OCR artifact: stray leading lowercase before uppercase headword.
    if len(hw) > 1 and hw[0].islower() and hw[1].isupper():
        hw = hw[1:]
    # OCR on these scans often mistakes initial A as l/I.
    if hw[0] in {"l", "I"} and len(hw) > 2 and hw[1].islower():
        hw = "A" + hw[1:]
    if hw and hw[0].islower():
        hw = hw[0].upper() + hw[1:]
    return hw


def normalize_pos(raw):
    pos = raw.lower().replace(" ", "").replace(",", "").replace(";", "").replace(":", "")
    pos = pos.replace("u.", "n.").replace("vu.", "v.").replace("ady.", "adv.")
    pos = pos.replace("nv.", "n.")
    pos = pos.replace("nn.", "n.")
    pos = pos.replace("m.", "n.")
    pos = pos.rstrip(".")
    return POS_MAP.get(pos, f"{pos}.") if pos else "unknown"


def clean_definition(text):
    text = text.replace("\u2019", "'")
    text = re.sub(r"\s+", " ", text).strip()
    # Join simple OCR line-break hyphenation artifacts.
    text = text.replace("- ", "")
    text = re.sub(r"\s+([,;:.])", r"\1", text)
    return text


def split_pos_and_definition(rest):
    m = re.match(r"^([A-Za-z]{1,6}\.?)\s*(.*)$", rest.strip())
    if not m:
        return None, rest
    token = m.group(1)
    norm = normalize_pos(token)
    if norm.startswith("unknown") or norm in {"k.", "of.", "to.", "be."}:
        return None, rest
    return norm, m.group(2).strip()


def parse_txt_file(txt_path):
    lines = txt_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    entries = []
    current = None
    for line in lines:
        raw = line.strip()
        if not raw:
            continue
        m = ENTRY_RE.match(raw)
        if m:
            hw = normalize_headword(m.group(1))
            pos, remainder = split_pos_and_definition(m.group(2))
            if not (hw and pos):
                if current is not None:
                    sep = "" if current["definition_raw"].endswith("-") else " "
                    current["definition_raw"] = (current["definition_raw"] + sep + raw).strip()
                continue
            if current is not None:
                current["definition_raw"] = clean_definition(current["definition_raw"])
                entries.append(current)
            current = {
                "headword_english": hw,
                "pos_raw": pos,
                "definition_raw": remainder,
            }
        elif current is not None:
            sep = "" if current["definition_raw"].endswith("-") else " "
            current["definition_raw"] = (current["definition_raw"] + sep + raw).strip()
    if current is not None:
        current["definition_raw"] = clean_definition(current["definition_raw"])
        entries.append(current)
    return entries


def manifest_index(manifest_rows):
    out = {}
    for row in manifest_rows:
        image = row.get("image")
        if not image:
            continue
        txt_name = Path(image).with_suffix(".txt").name
        out[txt_name] = row
    return out


def is_target_letter_entry(headword, letter):
    return bool(headword) and headword[0].upper() == letter.upper()


def parse_all(input_dir, letter):
    input_dir = Path(input_dir)
    manifest_path = input_dir / "manifest.json"
    manifest = []
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    by_txt = manifest_index(manifest)

    raw_entries = []
    for txt_path in sorted(input_dir.glob("*.txt")):
        if txt_path.name == "manifest.txt":
            continue
        source = by_txt.get(txt_path.name, {})
        for e in parse_txt_file(txt_path):
            if not is_target_letter_entry(e["headword_english"], letter):
                continue
            e["source"] = {
                "page_index": source.get("page_index"),
                "page_number": source.get("page_number"),
                "column": source.get("column"),
                "image": source.get("image"),
                "text_file": txt_path.name,
                "method": "split-image-tesseract-ocr",
            }
            raw_entries.append(e)
    return raw_entries


def write_outputs(raw_entries, raw_out, cleaned_out):
    with open(raw_out, "w", encoding="utf-8") as f:
        json.dump(raw_entries, f, ensure_ascii=False, indent=2)

    cleaned = []
    for e in raw_entries:
        cleaned.append(
            {
                "headword_english": e["headword_english"],
                "pos": e["pos_raw"],
                "sesotho": e["definition_raw"],
                "source": e["source"],
            }
        )
    with open(cleaned_out, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Extract Casalis A entries from split-image OCR text files."
    )
    parser.add_argument("--input-dir", default="ocr_splits/casalis_a")
    parser.add_argument("--letter", default="A", help="Target starting letter to extract.")
    parser.add_argument("--raw-out", default=None)
    parser.add_argument("--cleaned-out", default=None)
    return parser.parse_args()


def main():
    args = parse_args()
    letter = (args.letter or "A").strip().upper()
    raw_out = args.raw_out or f"casalis_{letter.lower()}_raw_ocrsplit.json"
    cleaned_out = args.cleaned_out or f"casalis_{letter.lower()}_cleaned_ocrsplit.json"
    raw_entries = parse_all(args.input_dir, letter=letter)
    write_outputs(raw_entries, raw_out, cleaned_out)
    print(f"Extracted {len(raw_entries)} {letter}-entries -> {raw_out}")
    print(f"Wrote cleaned view -> {cleaned_out}")


if __name__ == "__main__":
    main()

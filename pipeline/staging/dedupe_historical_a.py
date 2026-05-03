import argparse
import json
import re
from collections import defaultdict


def entry_definition(entry):
    senses = entry.get("senses", [])
    if not isinstance(senses, list) or not senses:
        return ""
    first = senses[0]
    if not isinstance(first, dict):
        return ""
    return str(first.get("definition_en", "")).strip()


def quality_score(entry):
    score = 0
    deriv = str(entry.get("morphology", {}).get("derivation", ""))
    if "(Casalis)" in deriv:
        score += 5
    elif "Historical Entry" in deriv:
        score += 2

    pos = entry.get("pos", [])
    if isinstance(pos, list) and pos:
        score += 2
        if any(str(p).lower() == "unknown" for p in pos):
            score -= 1

    d = entry_definition(entry)
    score += min(4, len(d) / 60.0)

    if re.search(r"[{}<>]|\\b\\w*[A-Z]\\w*[A-Z]\\w*\\b", d):
        score -= 2
    if re.search(r"[0-9]", d):
        score -= 1
    if re.search(r"[.]{3,}|[,;:]{2,}", d):
        score -= 1
    if re.search(r"\\b[A-Z][a-z]{3,},\\s*(?:n|v|adj|adv|prep|conj)\\.", d):
        score -= 2
    if re.search(r"(\\bto\\b\\s+\\bto\\b|\\bte\\b\\s+\\breceive\\b)", d.lower()):
        score -= 1
    return score


def normalized_definition_signature(entry):
    d = entry_definition(entry).lower()
    d = re.sub(r"\s+", " ", d).strip()
    d = re.sub(r"[^a-z0-9\s]", "", d)
    return d


def normalize_headword(hw):
    hw = str(hw or "").strip()
    if not hw:
        return ""
    return hw[0].upper() + hw[1:]


def is_historical_letter(entry, letter):
    hw = normalize_headword(entry.get("headword_english", ""))
    if not hw.startswith(letter.upper()):
        return False
    deriv = str(entry.get("morphology", {}).get("derivation", ""))
    return "Historical Entry" in deriv


def dedupe(entries, letter):
    grouped = defaultdict(list)
    keep_indices = set()

    for i, entry in enumerate(entries):
        if not isinstance(entry, dict):
            keep_indices.add(i)
            continue
        if not is_historical_letter(entry, letter):
            keep_indices.add(i)
            continue
        hw = normalize_headword(entry.get("headword_english", ""))
        sig = normalized_definition_signature(entry)
        grouped[(hw, sig)].append((i, entry))

    removed = []
    for (hw, _sig), items in grouped.items():
        if len(items) == 1:
            keep_indices.add(items[0][0])
            continue
        ranked = sorted(
            items,
            key=lambda item: (
                quality_score(item[1]),
                len(entry_definition(item[1])),
                item[0],
            ),
            reverse=True,
        )
        winner_idx = ranked[0][0]
        keep_indices.add(winner_idx)
        for idx, entry in ranked[1:]:
            removed.append(
                {
                    "headword_english": hw,
                    "entry_id": entry.get("entry_id"),
                    "definition_en": entry_definition(entry),
                    "score": quality_score(entry),
                }
            )

    deduped = [entry for i, entry in enumerate(entries) if i in keep_indices]
    return deduped, removed


def parse_args():
    parser = argparse.ArgumentParser(
        description="Deduplicate historical Casalis letter entries in lexicon.json."
    )
    parser.add_argument("--lexicon", default="data/lexicon.json")
    parser.add_argument("--letter", default="A")
    parser.add_argument("--report", default=None)
    return parser.parse_args()


def main():
    args = parse_args()
    letter = (args.letter or "A").upper()
    report = args.report or f"lexicon_{letter.lower()}_dedupe_report.md"
    with open(args.lexicon, encoding="utf-8") as f:
        entries = json.load(f)

    deduped, removed = dedupe(entries, letter=letter)
    with open(args.lexicon, "w", encoding="utf-8") as f:
        json.dump(deduped, f, ensure_ascii=False, indent=2)

    lines = []
    lines.append(f"# Lexicon {letter} Dedupe Report")
    lines.append("")
    lines.append(f"- Input entries: {len(entries)}")
    lines.append(f"- Output entries: {len(deduped)}")
    lines.append(f"- Removed duplicates: {len(removed)}")
    lines.append("")
    if removed:
        lines.append("## Removed Entries (first 80)")
        lines.append("")
        for row in removed[:80]:
            lines.append(
                f"- {row['headword_english']} | entry_id={row['entry_id']} | score={row['score']:.2f}"
            )
        lines.append("")
    with open(report, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Deduped lexicon: {len(entries)} -> {len(deduped)}")
    print(f"Removed duplicates: {len(removed)}")
    print(f"Report: {report}")


if __name__ == "__main__":
    main()

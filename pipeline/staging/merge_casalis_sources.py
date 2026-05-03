import argparse
import json
import re
from copy import deepcopy
from difflib import SequenceMatcher


ALLOWED_POS = {"n.", "v.", "adj.", "adv.", "prep.", "conj.", "interj."}


def normalize_headword(hw):
    hw = (hw or "").strip()
    if not hw:
        return ""
    hw = hw[0].upper() + hw[1:]
    hw = re.sub(r"[^A-Za-z'\\-]", "", hw)
    return hw


def is_near_existing_headword(hw, existing_headwords, threshold=0.80):
    for ex in existing_headwords:
        if ex == hw:
            continue
        ratio = SequenceMatcher(None, hw, ex).ratio()
        if ratio >= threshold:
            return True, ex, ratio
    return False, None, 0.0


def ocr_entry_score(entry):
    hw = normalize_headword(entry.get("headword_english", ""))
    pos = (entry.get("pos") or entry.get("pos_raw") or "").strip().lower()
    if pos and not pos.endswith("."):
        pos += "."
    definition = (entry.get("sesotho") or entry.get("definition_raw") or "").strip()

    score = 0
    reasons = []

    if hw.startswith("A") and len(hw) >= 3:
        score += 2
    else:
        reasons.append("headword_not_a_or_too_short")

    if pos in ALLOWED_POS:
        score += 2
    else:
        reasons.append("pos_not_allowed")

    if len(definition) >= 20:
        score += 2
    elif len(definition) >= 12:
        score += 1
    elif len(definition) >= 6:
        score += 1
    else:
        reasons.append("definition_too_short")

    if len(definition.split()) >= 3:
        score += 1
    else:
        reasons.append("definition_too_few_tokens")

    if definition.endswith("-"):
        score -= 1
        reasons.append("definition_truncated_hyphen")
    else:
        score += 1

    # Likely bleed from next entry line inside definition.
    if re.search(r"[.;]\s+[A-Z][A-Za-z'\\-]{2,}\s*,\s*(?:n|v|adj|adv|prep|conj)\\.", definition):
        score -= 2
        reasons.append("definition_contains_next_entry_bleed")

    if re.search(r"\d", definition):
        score -= 2
        reasons.append("definition_has_digits")

    if definition.count("?") > 0:
        score -= 1
        reasons.append("definition_has_question_mark")

    # Penalize likely OCR garbage clusters.
    if re.search(r"(?:\\b[a-z]{1,2}\\.[a-z]{1,2}\\b|[|_])", definition.lower()):
        score -= 1
        reasons.append("definition_noise_pattern")

    return score, hw, pos, definition, reasons


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def save_report(path, lines):
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def merge(curated, ocr, min_score):
    merged = deepcopy(curated)
    existing = {normalize_headword(e.get("headword_english", "")) for e in curated}

    candidates_by_hw = {}
    rejected = []

    for entry in ocr:
        score, hw, pos, definition, reasons = ocr_entry_score(entry)
        if not hw or hw in existing:
            continue
        near, near_hw, near_ratio = is_near_existing_headword(hw, existing)
        if near:
            rejected.append(
                {
                    "headword_english": hw,
                    "pos": pos,
                    "sesotho": definition,
                    "source": entry.get("source", {}),
                    "score": score,
                    "reasons": [f"headword_near_existing:{near_hw}:{near_ratio:.2f}"],
                }
            )
            continue
        row = {
            "headword_english": hw,
            "pos": pos,
            "sesotho": definition,
            "source": entry.get("source", {}),
            "score": score,
            "reasons": reasons,
        }
        if score < min_score:
            rejected.append(row)
            continue
        current = candidates_by_hw.get(hw)
        if current is None or row["score"] > current["score"] or (
            row["score"] == current["score"] and len(row["sesotho"]) > len(current["sesotho"])
        ):
            candidates_by_hw[hw] = row

    accepted = sorted(candidates_by_hw.values(), key=lambda x: x["headword_english"])
    for row in accepted:
        merged.append(
            {
                "headword_english": row["headword_english"],
                "pos": row["pos"],
                "sesotho": row["sesotho"],
                "source": row["source"],
            }
        )
    return merged, accepted, rejected


def build_report(curated_path, ocr_path, out_path, merged, accepted, rejected, min_score):
    lines = []
    lines.append("# Casalis Auto-Merge Report")
    lines.append("")
    lines.append(f"- Curated input: `{curated_path}`")
    lines.append(f"- OCR input: `{ocr_path}`")
    lines.append(f"- Minimum acceptance score: `{min_score}`")
    lines.append(f"- Accepted OCR additions: `{len(accepted)}`")
    lines.append(f"- Rejected OCR candidates: `{len(rejected)}`")
    lines.append(f"- Merged output entries: `{len(merged)}`")
    lines.append("")
    if accepted:
        lines.append("## Accepted Additions")
        lines.append("")
        for row in accepted:
            src = row.get("source", {})
            lines.append(
                f"- {row['headword_english']} ({row['pos']}) score={row['score']} "
                f"source={src.get('text_file','?')}"
            )
        lines.append("")
    if rejected:
        lines.append("## Rejected Candidates (first 40)")
        lines.append("")
        for row in sorted(rejected, key=lambda x: x["score"])[:40]:
            src = row.get("source", {})
            why = ",".join(row["reasons"]) if row["reasons"] else "low_score"
            lines.append(
                f"- {row['headword_english']} ({row['pos']}) score={row['score']} "
                f"source={src.get('text_file','?')} reasons={why}"
            )
        lines.append("")
    save_report(out_path, lines)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Auto-merge curated Casalis entries with high-confidence missing OCR entries."
    )
    parser.add_argument("--curated", default="casalis_a_cleaned.json")
    parser.add_argument("--ocr", default="casalis_a_cleaned_ocrsplit.json")
    parser.add_argument(
        "--output", default="casalis_a_cleaned_merged.json", help="Merged output JSON path."
    )
    parser.add_argument(
        "--report", default="casalis_a_merge_report.md", help="Merge report markdown path."
    )
    parser.add_argument("--min-score", type=int, default=8)
    return parser.parse_args()


def main():
    args = parse_args()
    curated = load_json(args.curated)
    ocr = load_json(args.ocr)
    merged, accepted, rejected = merge(curated, ocr, args.min_score)
    save_json(args.output, merged)
    build_report(
        curated_path=args.curated,
        ocr_path=args.ocr,
        out_path=args.report,
        merged=merged,
        accepted=accepted,
        rejected=rejected,
        min_score=args.min_score,
    )
    print(f"Accepted OCR additions: {len(accepted)}")
    print(f"Rejected OCR candidates: {len(rejected)}")
    print(f"Merged output: {args.output} ({len(merged)} entries)")
    print(f"Report: {args.report}")


if __name__ == "__main__":
    main()

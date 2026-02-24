import argparse
import json


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def index_senses(dictionary):
    by_id = {}
    for entry in dictionary:
        entry_id = entry.get("entry_id", "")
        for sense in entry.get("senses", []):
            sense_id = sense.get("sense_id", "")
            by_id[(entry_id, sense_id)] = {
                "headword_english": entry.get("headword_english", ""),
                "definition_en": sense.get("definition_en", ""),
                "usage_example": sense.get("usage_example"),
            }
    return by_id


def summarize_changes(base_dict, candidate_dict):
    base_index = index_senses(base_dict)
    candidate_index = index_senses(candidate_dict)

    all_keys = sorted(set(base_index.keys()) | set(candidate_index.keys()))
    added, removed, changed = [], [], []

    for key in all_keys:
        base_item = base_index.get(key)
        cand_item = candidate_index.get(key)
        if base_item is None and cand_item is not None:
            added.append((key, cand_item))
            continue
        if base_item is not None and cand_item is None:
            removed.append((key, base_item))
            continue
        if base_item["usage_example"] != cand_item["usage_example"]:
            changed.append((key, base_item, cand_item))

    return {"added": added, "removed": removed, "changed": changed}


def render_report(summary, base_path, candidate_path):
    changed = sorted(summary["changed"], key=lambda item: item[0])
    added = sorted(summary["added"], key=lambda item: item[0])
    removed = sorted(summary["removed"], key=lambda item: item[0])

    lines = [
        "# Enrichment Diff Report",
        "",
        f"- Base: `{base_path}`",
        f"- Candidate: `{candidate_path}`",
        "",
        f"- Changed usage examples: {len(changed)}",
        f"- Added senses: {len(added)}",
        f"- Removed senses: {len(removed)}",
        "",
    ]

    if changed:
        lines.append("## Changed Usage Examples")
        lines.append("")
        for (entry_id, sense_id), base_item, cand_item in changed:
            before = base_item.get("usage_example") or {}
            after = cand_item.get("usage_example") or {}
            lines.append(
                f"- `{entry_id}` / `{sense_id}` ({cand_item.get('headword_english', '')})"
            )
            lines.append(f"  - before: `{before.get('source', 'None')}`")
            lines.append(f"  - after: `{after.get('source', 'None')}`")
        lines.append("")

    if added:
        lines.append("## Added Senses")
        lines.append("")
        for (entry_id, sense_id), item in added:
            lines.append(f"- `{entry_id}` / `{sense_id}` ({item.get('headword_english', '')})")
        lines.append("")

    if removed:
        lines.append("## Removed Senses")
        lines.append("")
        for (entry_id, sense_id), item in removed:
            lines.append(f"- `{entry_id}` / `{sense_id}` ({item.get('headword_english', '')})")
        lines.append("")

    return "\n".join(lines)


def parse_args():
    parser = argparse.ArgumentParser(description="Generate deterministic diff report for enriched dictionary output.")
    parser.add_argument("--base", default="dictionary.json")
    parser.add_argument("--candidate", default="dictionary.enriched.json")
    parser.add_argument("--output", default="enrichment_diff.md")
    return parser.parse_args()


def main():
    args = parse_args()
    base_dict = load_json(args.base)
    candidate_dict = load_json(args.candidate)
    summary = summarize_changes(base_dict, candidate_dict)
    report = render_report(summary, args.base, args.candidate)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(report)
    print(
        "Generated diff report: "
        f"{len(summary['changed'])} changed, {len(summary['added'])} added, {len(summary['removed'])} removed."
    )
    print(f"Saved to '{args.output}'.")


if __name__ == "__main__":
    main()

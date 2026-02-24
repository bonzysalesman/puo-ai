import argparse
import json
import re
from pathlib import Path

from bs4 import BeautifulSoup


def clean_text(text):
    # Remove typical JW inline markers and normalize whitespace.
    text = re.sub(r"[+*]", " ", text)
    text = re.sub(r"^\d+\s*", "", text)
    # Normalize special apostrophes and handle specific Sesotho spacing issues (e.g., "holim 'a")
    text = text.replace("\u2019", "'")
    text = text.replace(" 'a", "'a")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def contains_term(text, term):
    term = term.strip()
    if not term:
        return False
    # Match whole term only to avoid partial matches (e.g. "cat" in "concatenate").
    pattern = re.compile(rf"(?<!\w){re.escape(term)}(?!\w)", re.IGNORECASE)
    return bool(pattern.search(text))


def normalize_terms(terms, stop_terms=None):
    stop_lookup = {t.strip().lower() for t in (stop_terms or []) if t.strip()}
    seen = set()
    normalized = []
    for term in terms:
        term = term.strip()
        if not term:
            continue
        key = term.lower()
        if key in stop_lookup or key in seen:
            continue
        seen.add(key)
        normalized.append(term)
    return normalized


def score_verse_match(st_text, terms):
    matched_terms = [term for term in terms if contains_term(st_text, term)]
    if not matched_terms:
        return None

    term_count = len(matched_terms)
    term_length_sum = sum(len(term) for term in matched_terms)
    return matched_terms, term_count, term_length_sum, len(st_text)


def find_best_match(
    st_verses,
    en_verses,
    terms,
    weight_term_count=1000.0,
    weight_term_length=1.0,
    weight_verse_length_penalty=0.01,
):
    best = None
    for verse_id, st_text in st_verses.items():
        en_text = en_verses.get(verse_id)
        if not en_text:
            continue
        scored = score_verse_match(st_text, terms)
        if not scored:
            continue
        matched_terms, term_count, term_length_sum, verse_length = scored
        weighted_score = (
            (term_count * weight_term_count)
            + (term_length_sum * weight_term_length)
            - (verse_length * weight_verse_length_penalty)
        )
        candidate = (
            weighted_score,
            term_count,
            term_length_sum,
            -verse_length,
            verse_id,
            st_text,
            en_text,
            matched_terms,
        )
        if best is None:
            best = candidate
            continue
        # Higher weighted score wins; lexical verse id ascending breaks ties.
        if candidate[:4] > best[:4] or (candidate[:4] == best[:4] and verse_id < best[4]):
            best = candidate
    return best


def fetch_verses_local(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return {}

    soup = BeautifulSoup(content, "html.parser")
    verses = {}

    verse_spans = soup.find_all("span", class_="verse")

    for span in verse_spans:
        verse_id = span.get("id")
        if not verse_id:
            continue

        for tag in span.find_all(["sup", "a"]):
            tag.decompose()

        text = clean_text(span.get_text())
        if text:
            verses[verse_id] = text

    return verses


def enrich_dictionary(
    dict_path,
    st_file,
    en_file,
    source_label=None,
    output_path=None,
    dry_run=False,
    verbose=False,
    overwrite=False,
    stop_terms=None,
    weight_term_count=1000.0,
    weight_term_length=1.0,
    weight_verse_length_penalty=0.01,
):
    try:
        with open(dict_path, "r", encoding="utf-8") as f:
            dictionary = json.load(f)
    except Exception as e:
        print(f"Error reading dictionary: {e}")
        return 0

    st_verses = fetch_verses_local(st_file)
    en_verses = fetch_verses_local(en_file)

    if verbose:
        print(f"St Verses retrieved: {len(st_verses)}")
        print(f"En Verses retrieved: {len(en_verses)}")

    source_base = source_label or f"JW Bible - {Path(st_file).stem}"
    enriched_count = 0
    unmatched_senses = 0

    for entry in dictionary:
        for sense in entry.get("senses", []):
            if sense.get("usage_example") and not overwrite:
                if verbose:
                    print(f"Skipping already enriched sense '{sense.get('sense_id')}'")
                continue

            st_terms = normalize_terms(sense.get("sesotho_term", []), stop_terms=stop_terms)
            best_match = find_best_match(
                st_verses,
                en_verses,
                st_terms,
                weight_term_count=weight_term_count,
                weight_term_length=weight_term_length,
                weight_verse_length_penalty=weight_verse_length_penalty,
            )
            if not best_match:
                unmatched_senses += 1
                continue
            (
                weighted_score,
                term_count,
                term_length_sum,
                _neg_verse_len,
                verse_id,
                st_text,
                en_text,
                matched_terms,
            ) = best_match
            sense["usage_example"] = {
                "sesotho": st_text,
                "english": en_text,
                "source": f"{source_base} (Verse {verse_id})",
            }
            enriched_count += 1
            if verbose:
                print(
                    "Matched sense "
                    f"'{sense.get('sense_id')}' in {verse_id} using {matched_terms} "
                    f"weighted_score={weighted_score:.3f} "
                    f"(count={term_count}, length={term_length_sum})"
                )

    if dry_run:
        print(
            f"Dry run: {enriched_count} senses would be enriched; {unmatched_senses} unmatched."
        )
        return enriched_count

    destination = output_path or dict_path
    with open(destination, "w", encoding="utf-8") as f:
        json.dump(dictionary, f, ensure_ascii=False, indent=2)

    print(f"Successfully enriched {enriched_count} senses; {unmatched_senses} unmatched.")
    print(f"Saved to '{destination}'.")
    return enriched_count


def parse_args():
    parser = argparse.ArgumentParser(
        description="Enrich dictionary senses with parallel verse examples."
    )
    parser.add_argument("--dictionary", default="dictionary.json")
    parser.add_argument("--sesotho-file", default="st_gen1.html")
    parser.add_argument("--english-file", default="en_gen1.html")
    parser.add_argument("--source-label", default=None)
    parser.add_argument("--output", default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing usage examples.")
    parser.add_argument(
        "--stop-terms",
        default="",
        help="Comma-separated terms to ignore during matching.",
    )
    parser.add_argument(
        "--weight-term-count",
        type=float,
        default=1000.0,
        help="Weight applied to number of matched terms in a verse.",
    )
    parser.add_argument(
        "--weight-term-length",
        type=float,
        default=1.0,
        help="Weight applied to total character length of matched terms.",
    )
    parser.add_argument(
        "--weight-verse-length-penalty",
        type=float,
        default=0.01,
        help="Penalty applied per verse character (higher prefers shorter verses).",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    enrich_dictionary(
        dict_path=args.dictionary,
        st_file=args.sesotho_file,
        en_file=args.english_file,
        source_label=args.source_label,
        output_path=args.output,
        dry_run=args.dry_run,
        verbose=args.verbose,
        overwrite=args.overwrite,
        stop_terms=[t for t in args.stop_terms.split(",") if t.strip()],
        weight_term_count=args.weight_term_count,
        weight_term_length=args.weight_term_length,
        weight_verse_length_penalty=args.weight_verse_length_penalty,
    )

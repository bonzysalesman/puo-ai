import argparse
import hashlib
import json
import re
from pathlib import Path
import sqlite3

from bs4 import BeautifulSoup
from pipeline.warden.normalize_orthography import Warden
from pipeline.warden.protector import Protector
from pipeline.warden.agreement import AgreementEngine


def stable_hash(parts, prefix, length=16):
    joined = "|".join(parts)
    digest = hashlib.sha1(joined.encode("utf-8")).hexdigest()[:length]
    return f"{prefix}{digest}"


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


def fetch_verses_db(db_path, terms, limit=500):
    """Query the SQLite DB FTS index for candidate verses matching any of the terms.

    Returns two dicts: (st_verses, en_verses) keyed by verse_id (corpus.ref if present, else corpus_id).
    """
    st_verses = {}
    en_verses = {}
    if not db_path or not terms:
        return st_verses, en_verses

    # Build a simple FTS5 match string. Escape double-quotes in tokens.
    tokens = []
    for t in terms:
        tok = str(t).strip()
        if not tok:
            continue
        tok = tok.replace('"', '')
        if " " in tok:
            tokens.append(f'"{tok}"')
        else:
            tokens.append(tok)
    if not tokens:
        return st_verses, en_verses

    match_query = " OR ".join(tokens)

    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        sql = (
            "SELECT corpus.corpus_id, corpus.ref, corpus.sesotho_text, corpus.english_text "
            "FROM corpus JOIN corpus_fts ON corpus.rowid = corpus_fts.rowid "
            "WHERE corpus_fts MATCH ? LIMIT ?"
        )
        cur.execute(sql, (match_query, limit))
        rows = cur.fetchall()
        for corpus_id, ref, st, en in rows:
            verse_id = ref if ref else corpus_id
            if st and st.strip():
                st_verses[verse_id] = st
            if en and en.strip():
                en_verses[verse_id] = en
    except Exception as e:
        print(f"Error querying DB {db_path}: {e}")
    finally:
        try:
            conn.close()
        except Exception:
            pass

    return st_verses, en_verses


def enrich_dictionary(
    dict_path,
    st_file,
    en_file,
    db_path=None,
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

    use_db = False
    st_verses = {}
    en_verses = {}
    if db_path:
        use_db = True
        if verbose:
            print(f"Using SQLite DB for candidate verses: {db_path}")
    else:
        st_verses = fetch_verses_local(st_file)
        en_verses = fetch_verses_local(en_file)

        if verbose:
            print(f"St Verses retrieved: {len(st_verses)}")
            print(f"En Verses retrieved: {len(en_verses)}")

    # instantiate Warden/Protector/AgreementEngine once for the loop
    warden_inst = Warden(db_path=db_path) if db_path else Warden()
    protector = Protector(db_path=db_path) if db_path else Protector()
    agreement_engine = AgreementEngine(db_path=db_path) if db_path else AgreementEngine()

    source_base = source_label or f"JW Bible - {Path(st_file).stem}"
    enriched_count = 0
    unmatched_senses = 0

    for entry in dictionary:
        for sense in entry.get("senses", []):
            if sense.get("usage_example") and not overwrite:
                if verbose:
                    print(f"Skipping already enriched sense '{sense.get('sense_id')}'")
                continue

            st_terms_raw = sense.get("sesotho_term", [])
            if not st_terms_raw:
                hw_st = entry.get("headword_sesotho", [])
                if isinstance(hw_st, list) and len(hw_st) > 0:
                    st_terms_raw = [hw_st[0].get("orthographic", "")]
                elif isinstance(hw_st, dict):
                    st_terms_raw = [hw_st.get("orthographic", "")]
            st_terms = normalize_terms(st_terms_raw, stop_terms=stop_terms)
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

            # Pipeline: Protector(mask) -> Warden(normalize mappings) -> Agreement (apply_all) -> Protector(restore)
            try:
                masked, imm_map = protector.protect(st_text)
                mapped = warden_inst.apply_mappings(masked)
                agreed = agreement_engine.apply_all_agreement(mapped)
                st_text_processed = protector.restore(agreed, imm_map)
            except Exception as e:
                # fallback to original if anything fails
                if verbose:
                    print(f"Agreement pipeline error: {e}")
                st_text_processed = st_text

            sense["usage_example"] = {
                "sesotho": st_text_processed,
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


def load_json_array(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, list) else []


def normalize_headword_sesotho(headword_sesotho):
    if isinstance(headword_sesotho, dict):
        headword_sesotho = [headword_sesotho]
    if not isinstance(headword_sesotho, list):
        return []
    out = []
    for item in headword_sesotho:
        if not isinstance(item, dict):
            continue
        orth = str(item.get("orthographic", "")).strip()
        if not orth:
            continue
        out.append(orth)
    return out


def enrich_split_datasets(
    lexicon_path,
    corpus_path,
    attestations_path,
    st_file,
    en_file,
    db_path=None,
    source_label=None,
    dry_run=False,
    verbose=False,
    overwrite=False,
    stop_terms=None,
    weight_term_count=1000.0,
    weight_term_length=1.0,
    weight_verse_length_penalty=0.01,
):
    lexicon = load_json_array(lexicon_path)
    corpus = load_json_array(corpus_path)
    attestations = load_json_array(attestations_path)

    st_verses = fetch_verses_local(st_file)
    en_verses = fetch_verses_local(en_file)

    if verbose:
        print(f"St Verses retrieved: {len(st_verses)}")
        print(f"En Verses retrieved: {len(en_verses)}")

    source_base = source_label or f"JW Bible - {Path(st_file).stem}"

    corpus_by_id = {}
    corpus_key_to_id = {}
    for row in corpus:
        if not isinstance(row, dict):
            continue
        cid = row.get("corpus_id")
        if not isinstance(cid, str) or not cid:
            continue
        corpus_by_id[cid] = row
        key = (
            str(row.get("source", "")).strip(),
            str(row.get("ref", "")).strip(),
            str(row.get("sesotho_text", "")).strip(),
            str(row.get("english_text", "")).strip(),
        )
        corpus_key_to_id[key] = cid

    atts_by_sense = {}
    for row in attestations:
        if not isinstance(row, dict):
            continue
        sid = row.get("sense_id")
        if isinstance(sid, str) and sid:
            atts_by_sense.setdefault(sid, []).append(row)

    enriched_count = 0
    unmatched_senses = 0
    skipped_senses = 0

    for entry in lexicon:
        if not isinstance(entry, dict):
            continue
        entry_terms_fallback = normalize_headword_sesotho(entry.get("headword_sesotho"))
        for sense in entry.get("senses", []):
            if not isinstance(sense, dict):
                continue
            sense_id = sense.get("sense_id")
            if not isinstance(sense_id, str) or not sense_id:
                continue

            if atts_by_sense.get(sense_id) and not overwrite:
                skipped_senses += 1
                if verbose:
                    print(f"Skipping already enriched sense '{sense_id}'")
                continue

            st_terms_raw = sense.get("sesotho_term", [])
            if not st_terms_raw:
                st_terms_raw = entry_terms_fallback
            st_terms = normalize_terms(st_terms_raw, stop_terms=stop_terms)
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

            if overwrite and atts_by_sense.get(sense_id):
                attestations = [
                    row
                    for row in attestations
                    if not (isinstance(row, dict) and row.get("sense_id") == sense_id)
                ]
                atts_by_sense[sense_id] = []

            corpus_key = (source_base, verse_id, st_text, en_text)
            corpus_id = corpus_key_to_id.get(corpus_key)
            if corpus_id is None:
                corpus_id = stable_hash(corpus_key, prefix="corpus_")
                corpus_row = {
                    "corpus_id": corpus_id,
                    "source": source_base,
                    "ref": verse_id,
                    "sesotho_text": st_text_processed,
                    "english_text": en_text,
                }
                corpus.append(corpus_row)
                corpus_by_id[corpus_id] = corpus_row
                corpus_key_to_id[corpus_key] = corpus_id

            attestation_id = stable_hash([sense_id, corpus_id], prefix="att_")
            attestation_row = {
                "attestation_id": attestation_id,
                "sense_id": sense_id,
                "corpus_id": corpus_id,
                "source_raw": f"{source_base} (Verse {verse_id})",
                "match_terms": matched_terms,
                "score": weighted_score,
                "method": "enricher_split_v1",
            }
            if not any(
                isinstance(row, dict) and row.get("attestation_id") == attestation_id
                for row in attestations
            ):
                attestations.append(attestation_row)
                atts_by_sense.setdefault(sense_id, []).append(attestation_row)
                enriched_count += 1
                if verbose:
                    print(
                        "Matched sense "
                        f"'{sense_id}' in {verse_id} using {matched_terms} "
                        f"weighted_score={weighted_score:.3f} "
                        f"(count={term_count}, length={term_length_sum})"
                    )

    if dry_run:
        print(
            f"Dry run: {enriched_count} senses would be enriched; "
            f"{unmatched_senses} unmatched; {skipped_senses} skipped."
        )
        return enriched_count

    with open(corpus_path, "w", encoding="utf-8") as f:
        json.dump(corpus, f, ensure_ascii=False, indent=2)
    with open(attestations_path, "w", encoding="utf-8") as f:
        json.dump(attestations, f, ensure_ascii=False, indent=2)

    print(
        f"Successfully enriched {enriched_count} senses; "
        f"{unmatched_senses} unmatched; {skipped_senses} skipped."
    )
    print(f"Updated '{corpus_path}' and '{attestations_path}'.")
    return enriched_count


def parse_args():
    parser = argparse.ArgumentParser(
        description="Enrich dictionary senses with parallel verse examples."
    )
    parser.add_argument(
        "--mode",
        choices=["split", "legacy"],
        default="split",
        help="`split` writes to corpus/attestations via lexicon senses; `legacy` writes usage_example into dictionary JSON.",
    )
    parser.add_argument("--dictionary", default="data/dictionary.json")
    parser.add_argument("--lexicon", default="data/lexicon.json")
    parser.add_argument("--corpus", default="data/corpus.json")
    parser.add_argument("--attestations", default="data/attestations.json")
    parser.add_argument("--sesotho-file", default="sources/bible/st_gen1.html")
    parser.add_argument("--english-file", default="sources/bible/en_gen1.html")
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
    if args.mode == "legacy":
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
    else:
        enrich_split_datasets(
            lexicon_path=args.lexicon,
            corpus_path=args.corpus,
            attestations_path=args.attestations,
            st_file=args.sesotho_file,
            en_file=args.english_file,
            source_label=args.source_label,
            dry_run=args.dry_run,
            verbose=args.verbose,
            overwrite=args.overwrite,
            stop_terms=[t for t in args.stop_terms.split(",") if t.strip()],
            weight_term_count=args.weight_term_count,
            weight_term_length=args.weight_term_length,
            weight_verse_length_penalty=args.weight_verse_length_penalty,
        )

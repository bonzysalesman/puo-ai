import json
import re
import argparse
from pathlib import Path
from bs4 import BeautifulSoup
import hashlib

# Import necessary functions from enricher.py if possible, or redefine them for portability
def clean_text(text):
    text = re.sub(r"[+*]", " ", text)
    text = re.sub(r"^\d+\s*", "", text)
    text = text.replace("\u2019", "'")
    text = text.replace(" 'a", "'a")
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def contains_term(text, term):
    term = term.strip()
    if not term: return False
    pattern = re.compile(rf"(?<!\w){re.escape(term)}(?!\w)", re.IGNORECASE)
    return bool(pattern.search(text))

def stable_hash(data, prefix=""):
    if isinstance(data, (list, tuple)):
        data = "|".join(map(str, data))
    return prefix + hashlib.md5(str(data).encode("utf-8")).hexdigest()[:16]

def normalize_terms(terms):
    seen = set()
    normalized = []
    for term in terms:
        term = term.strip()
        if not term: continue
        key = term.lower()
        if key in seen: continue
        seen.add(key)
        normalized.append(term)
    return normalized

def score_verse_match(st_text, terms):
    matched_terms = [term for term in terms if contains_term(st_text, term)]
    if not matched_terms: return None
    return matched_terms, len(matched_terms), sum(len(term) for term in matched_terms), len(st_text)

def find_best_match(st_verses, en_verses, terms):
    best = None
    for verse_id, st_text in st_verses.items():
        en_text = en_verses.get(verse_id)
        if not en_text: continue
        scored = score_verse_match(st_text, terms)
        if not scored: continue
        
        matched_terms, term_count, term_length_sum, verse_length = scored
        # Basic scoring: favor more terms, then length, then penalize verse length
        weighted_score = (term_count * 1000.0) + (term_length_sum * 1.0) - (verse_length * 0.01)
        
        candidate = (weighted_score, term_count, term_length_sum, -verse_length, verse_id, st_text, en_text, matched_terms)
        if best is None or candidate[:4] > best[:4]:
            best = candidate
    return best

def fetch_verses_st(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    verses = {}
    for span in soup.find_all("span", class_="verse"):
        vid = span.get("id")
        if not vid: continue
        # Remove footnotes/xrefs
        for tag in span.find_all(["sup", "a"]): tag.decompose()
        verses[vid] = clean_text(span.get_text())
    return verses

def load_nkjv_verses(nkjv_path, book_name, book_id_num):
    with open(nkjv_path, "r", encoding="utf-8") as f:
        nkjv = json.load(f)
    
    verses = {}
    book_data = nkjv.get(book_name, {})
    for chapter_num, chapter_data in book_data.items():
        for verse_num, text in chapter_data.items():
            # Format: vBBCCCVVV
            vid = f"v{int(book_id_num):02}{int(chapter_num):03}{int(verse_num):03}"
            verses[vid] = text.strip()
    return verses

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lexicon", default="data/lexicon.json")
    parser.add_argument("--corpus", default="data/corpus.json")
    parser.add_argument("--attestations", default="data/attestations.json")
    parser.add_argument("--nkjv", default="sources/bible/NEW KING JAMES VERSION.json")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    lexicon = json.load(open(args.lexicon))
    corpus = json.load(open(args.corpus))
    attestations = json.load(open(args.attestations))

    # Map of books to process
    job_list = [
        ("Genesis", "01", "sources/bible/st_gen1.html"),
        ("Genesis", "01", "sources/bible/st_gen2.html"),  # gen1 and gen2 files might overlap in book id but we use HTML for st
        ("Psalms", "19", "sources/bible/st_ps103.html"),
        ("Romans", "45", "sources/bible/st_rom13.html"),
    ]

    source_label = "NKJV"
    
    # Pre-index existing attestations by (sense_id, source)
    existing_atts = {}
    for a in attestations:
        existing_atts[(a['sense_id'], a.get('source_raw', '').split(' ')[0])] = True

    new_enriched = 0
    
    for book_name, book_id, st_file in job_list:
        print(f"Processing {st_file} with NKJV {book_name}...")
        st_verses = fetch_verses_st(st_file)
        en_verses = load_nkjv_verses(args.nkjv, book_name, book_id)
        
        for entry in lexicon:
            hw_st_list = [h['orthographic'] for h in entry.get('headword_sesotho', [])]
            for sense in entry.get('senses', []):
                sid = sense['sense_id']
                
                # Check if we already have an NKJV attestation for this sense
                if (sid, "NKJV") in existing_atts:
                    continue
                
                terms = normalize_terms(sense.get('sesotho_term', []) or hw_st_list)
                if not terms: continue
                
                match = find_best_match(st_verses, en_verses, terms)
                if match:
                    score, _, _, _, vid, st_text, en_text, matched_terms = match
                    
                    corpus_key = (source_label, vid, st_text, en_text)
                    cid = stable_hash(corpus_key, prefix="corpus_")
                    
                    # Add to corpus if missing
                    if not any(c['corpus_id'] == cid for c in corpus):
                        corpus.append({
                            "corpus_id": cid,
                            "source": source_label,
                            "ref": vid,
                            "sesotho_text": st_text,
                            "english_text": en_text
                        })
                    
                    aid = stable_hash([sid, cid], prefix="att_")
                    if not any(a['attestation_id'] == aid for a in attestations):
                        attestations.append({
                            "attestation_id": aid,
                            "sense_id": sid,
                            "corpus_id": cid,
                            "source_raw": f"{source_label} ({book_name} {vid})",
                            "match_terms": matched_terms,
                            "score": score,
                            "method": "nkjv_enrich_v1"
                        })
                        new_enriched += 1

    print(f"Enriched {new_enriched} senses with NKJV examples.")
    
    if not args.dry_run:
        with open(args.corpus, "w") as f: json.dump(corpus, f, indent=2, ensure_ascii=False)
        with open(args.attestations, "w") as f: json.dump(attestations, f, indent=2, ensure_ascii=False)
        print("Updated corpus.json and attestations.json")

if __name__ == "__main__":
    main()

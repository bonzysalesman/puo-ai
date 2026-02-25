"""
Targeted enrichment for historical entries using split datasets as source of truth.
Writes only to corpus.json and attestations.json (lexicon is read-only for sense terms).
"""
from enricher import enrich_split_datasets


corpus_sources = [
    ("st_gen1.html", "en_gen1.html", "JW Bible - Gen1"),
    ("st_gen2.html", "en_gen2.html", "JW Bible - Gen2"),
    ("st_ps103.html", "en_ps103.html", "JW Bible - Ps103"),
]

total = 0
for st_path, en_path, label in corpus_sources:
    count = enrich_split_datasets(
        lexicon_path="lexicon.json",
        corpus_path="corpus.json",
        attestations_path="attestations.json",
        st_file=st_path,
        en_file=en_path,
        source_label=label,
        dry_run=False,
        overwrite=False,
        stop_terms=["le", "ke", "a", "ho", "o"],
    )
    total += count

print(f"Total new attestations added across corpora: {total}")

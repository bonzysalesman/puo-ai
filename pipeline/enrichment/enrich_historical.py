import argparse
from enricher import enrich_split_datasets


def main():
    parser = argparse.ArgumentParser(description="Targeted enrichment for historical entries.")
    parser.add_argument("--dry-run", action="store_true", help="Perform a dry run without writing changes.")
    parser.add_argument("--verbose", action="store_true", help="Print detailed matching information.")
    args = parser.parse_args()

    corpus_sources = [
        ("sources/bible/st_gen1.html", "sources/bible/en_gen1.html", "JW Bible - Gen1"),
        ("sources/bible/st_gen2.html", "sources/bible/en_gen2.html", "JW Bible - Gen2"),
        ("sources/bible/st_ps103.html", "sources/bible/en_ps103.html", "JW Bible - Ps103"),
        ("sources/bible/st_rom13.html", "sources/bible/en_rom13.html", "JW Bible - Rom13"),
    ]

    total = 0
    for st_path, en_path, label in corpus_sources:
        count = enrich_split_datasets(
            lexicon_path="data/lexicon.json",
            corpus_path="data/corpus.json",
            attestations_path="data/attestations.json",
            st_file=st_path,
            en_file=en_path,
            source_label=label,
            dry_run=args.dry_run,
            verbose=args.verbose,
            overwrite=False,
            stop_terms=["le", "ke", "a", "ho", "o"],
        )
        total += count

    if args.dry_run:
        print(f"Dry run: {total} new attestations would be added across corpora.")
    else:
        print(f"Total new attestations added across corpora: {total}")


if __name__ == "__main__":
    main()

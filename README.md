# PUO-AI

Sesotho-English dictionary enrichment utilities using local parallel Bible HTML.

## Requirements

- Python 3.9+
- `pip`

Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

## Core Commands

Run tests:

```bash
python3 -m unittest discover -s tests -v
```

Validate dictionary schema only:

```bash
python3 -m unittest tests.test_dictionary_schema -v
```

Dry-run enrichment:

```bash
python3 enricher.py --mode split --dry-run --source-label "JW Bible - Genesis 1"
```

Dry-run with generic terms ignored:

```bash
python3 enricher.py --mode split --dry-run --source-label "JW Bible - Genesis 1" --stop-terms "le,ea,ho"
```

Dry-run with custom scoring weights:

```bash
python3 enricher.py --mode split --dry-run --source-label "JW Bible - Genesis 1" --weight-term-count 1200 --weight-term-length 1 --weight-verse-length-penalty 0.02
```

Write enrichment output directly to `corpus.json` and `attestations.json`:

```bash
python3 enricher.py --mode split --source-label "JW Bible - Genesis 1"
```

Legacy mode (writes `usage_example` into dictionary-style JSON):

```bash
python3 enricher.py --mode legacy --dictionary dictionary.json --output dictionary.enriched.json --source-label "JW Bible - Genesis 1"
```

Generate deterministic diff report before promoting:

```bash
python3 review_enrichment_diff.py --base dictionary.json --candidate dictionary.enriched.json --output enrichment_diff.md
```

Staged workflow with `make`:

```bash
make enrich-stage
make review-stage
```

Generate word list:

```bash
python3 extract_wordlist.py --dictionary dictionary.json --output wordlist.md
```

Split mixed dictionary+corpus data into linked datasets:

```bash
python3 split_datasets.py --dictionary dictionary.json --lexicon-out lexicon.json --corpus-out corpus.json --attestations-out attestations.json
```

Or with `make`:

```bash
make split-datasets
```

Rebuild a backward-compatible dictionary view with `usage_example` fields:

```bash
python3 join_view.py --lexicon lexicon.json --corpus corpus.json --attestations attestations.json --output dictionary.joined.json
```

Or with `make`:

```bash
make join-view
```

## Local Data Files

- `dictionary.json`: dictionary data and usage examples
- `lexicon.json`: normalized dictionary-only dataset (generated)
- `corpus.json`: parallel verse corpus dataset (generated)
- `attestations.json`: linkage table from lexicon senses to corpus verses (generated)
- `dictionary.joined.json`: reconstructed legacy-compatible combined view (generated)
- `dictionary.json`: legacy mixed file (no longer source of truth)
- `st_gen1.html`: Sesotho Genesis 1
- `en_gen1.html`: English Genesis 1
- `st_ps103.html`: placeholder (currently empty)

## Notes

- `enricher.py` uses whole-term, case-insensitive matching to reduce false positives.
- Split datasets (`lexicon/corpus/attestations`) are now the source of truth.
- Use `--dry-run` before writing changes to validate expected match counts.
- Match scoring can be tuned using `--weight-term-count`, `--weight-term-length`, and `--weight-verse-length-penalty`.

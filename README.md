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
python3 enricher.py --dry-run --source-label "JW Bible - Genesis 1"
```

Dry-run with generic terms ignored:

```bash
python3 enricher.py --dry-run --source-label "JW Bible - Genesis 1" --stop-terms "le,ea,ho"
```

Dry-run with custom scoring weights:

```bash
python3 enricher.py --dry-run --source-label "JW Bible - Genesis 1" --weight-term-count 1200 --weight-term-length 1 --weight-verse-length-penalty 0.02
```

Write enriched output to a new file:

```bash
python3 enricher.py --output dictionary.enriched.json --source-label "JW Bible - Genesis 1"
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

## Local Data Files

- `dictionary.json`: dictionary data and usage examples
- `st_gen1.html`: Sesotho Genesis 1
- `en_gen1.html`: English Genesis 1
- `st_ps103.html`: placeholder (currently empty)

## Notes

- `enricher.py` uses whole-term, case-insensitive matching to reduce false positives.
- Use `--dry-run` before writing changes to validate expected match counts.
- Match scoring can be tuned using `--weight-term-count`, `--weight-term-length`, and `--weight-verse-length-penalty`.

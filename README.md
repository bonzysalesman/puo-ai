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

Dry-run enrichment:

```bash
python3 enricher.py --dry-run --source-label "JW Bible - Genesis 1"
```

Write enriched output to a new file:

```bash
python3 enricher.py --output dictionary.enriched.json --source-label "JW Bible - Genesis 1"
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

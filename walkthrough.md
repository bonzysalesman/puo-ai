# Walkthrough: Sesotho-English Dictionary Enrichment

This walkthrough documents the current enrichment flow and the repository state as of February 24, 2026.

## Overview

The project enriches dictionary senses in `dictionary.json` by matching Sesotho terms against local JW Bible chapter HTML and attaching aligned English verse text.

## Current Local Corpus

- Sesotho Genesis 1: `st_gen1.html`
- English Genesis 1: `en_gen1.html`
- Placeholder file (empty): `st_ps103.html`

## Enrichment Workflow

1. Parse local verse HTML (`span.verse`) for both Sesotho and English files.
2. Remove inline markers and normalize text.
3. Match each `sesotho_term` using whole-term, case-insensitive matching.
4. If a verse id exists in both languages, write a `usage_example` to the matched sense.
5. Save changes either in-place or to an output file.

## Commands

Dry run (no writes):

```bash
python3 enricher.py --dry-run --source-label "JW Bible - Genesis 1"
```

Write to a new file:

```bash
python3 enricher.py --output dictionary.enriched.json --source-label "JW Bible - Genesis 1"
```

Generate deduplicated word list:

```bash
python3 extract_wordlist.py --dictionary dictionary.json --output wordlist.md
```

Run tests:

```bash
python3 -m unittest discover -s tests -v
```

## Notes on Sources

- Most `usage_example.source` values are Genesis 1 verse references generated from local HTML.
- A small number of dictionary entries currently contain source strings for Psalm 103:12 and Romans 13:7.
- Those two references are present as data labels in `dictionary.json`; equivalent local chapter HTML is not currently committed in this repository.

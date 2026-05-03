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

### Validation & Testing
Run all tests:
```bash
make test
```

Validate lexicon schema only:
```bash
python3 -m unittest tests.test_dictionary_schema -v
```

### Enrichment Pipeline
Enrich the split datasets (lexicon, corpus, attestations) using local parallel Bible HTML.

**Dry-run enrichment:**
```bash
python3 pipeline/enrichment/enricher.py --mode split --dry-run --source-label "JW Bible - Genesis 1"
```

**Write enrichment output:**
```bash
python3 pipeline/enrichment/enricher.py --mode split --source-label "JW Bible - Genesis 1"
```

**Options:**
- `--stop-terms "le,ea,ho"`: Ignore generic terms during matching.
- `--weight-term-count 1200`: Adjust scoring weights.

### Data Management
**Split legacy dictionary into datasets:**
```bash
make split-datasets
```

**Rebuild backward-compatible joined view:**
```bash
make join-view
```

**Generate word list:**
```bash
make wordlist
```

## Data Architecture

The project uses a normalized "split" architecture:
- `data/lexicon.json`: Headwords and senses (Source of Truth).
- `data/corpus.json`: Parallel verse corpus.
- `data/attestations.json`: Linkage table between lexicon senses and corpus verses.
- `data/dictionary.joined.json`: Generated legacy-compatible view for external tools.

Legacy files are stored in `data/legacy/`.

## Local Source Files
- `sources/bible/`: Parallel HTML chapters (e.g., `st_gen1.html`, `en_gen1.html`).
- `sources/nkjv_wordlist.txt`: Exhaustive English word list.
- `schemas/`: JSON schemas for all datasets.

## Notes
- `enricher.py` uses whole-term, case-insensitive matching to reduce false positives.
- Always use `--dry-run` before writing changes to validate match quality.

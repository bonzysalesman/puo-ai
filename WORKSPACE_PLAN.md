# Workspace Reorganisation Plan

## Context

The root directory accumulated 99 files across 6 types during iterative development of the Sesotho-English lexicography pipeline. This plan reorganises them into a coherent structure without breaking the existing test suite or Makefile targets.

## Target Structure

```
PUO-AI/
├── data/                          # source-of-truth datasets
│   ├── lexicon.json
│   ├── corpus.json
│   ├── attestations.json
│   ├── dictionary.json            # legacy
│   └── dictionary.joined.json     # derived
│
├── schemas/                       # JSON schema files
│   ├── lexicon.schema.json
│   ├── corpus.schema.json
│   ├── dictionary.schema.json
│   └── attestations.schema.json
│
├── sources/                       # original unmodified inputs
│   ├── bible/                     # parallel Bible HTML + NKJV JSON
│   └── pdfs/                      # Casalis + Mabille source PDFs
│
├── historical/                    # all OCR pipeline artifacts
│   ├── casalis/
│   │   ├── a/                     # casalis_a_*.json/md/csv
│   │   ├── b/
│   │   ├── c/
│   │   ├── d/
│   │   ├── e/
│   │   └── f/
│   ├── mabille/                   # mabille_*.json
│   └── staged/                    # staged_casalis_*.json, staged_mabille_*.json
│
├── pipeline/                      # processing scripts
│   ├── ocr/                       # ocr_split_pages.py, extract_casalis_*.py,
│   │                              #   build_corrected_casalis.py, heuristic_cleanup.py,
│   │                              #   cleanup_to_headwords.py, fix_casalis_e_extraction.py
│   ├── staging/                   # stage_a_entries.py, stage_f_entries.py,
│   │                              #   merge_casalis_sources.py, dedupe_historical_a.py,
│   │                              #   locate_a.py, extract_a_entries.py
│   ├── enrichment/                # enricher.py, enrich_historical.py,
│   │                              #   enrich_with_nkjv.py, review_enrichment_diff.py
│   └── export/                    # split_datasets.py, join_view.py,
│                                  #   extract_wordlist.py, generate_wordlist.py,
│                                  #   extract_nkjv_words.py, inject_historical_entries.py
│
├── reports/                       # markdown reports, diffs, review sheets
│
├── ocr_splits/                    # keep as-is (already well-structured)
├── tests/                         # keep as-is + conftest.py added in Phase 2
├── _agents/                       # keep as-is
├── _bmad/                         # keep as-is
├── backups/                       # keep as-is
│
├── Makefile                       # updated paths in Phase 2+
├── README.md
├── requirements.txt
└── WORKSPACE_PLAN.md              # this file
```

**Root goes from 99 files → 7 files.**

---

## Files to Delete

These are confirmed safe to remove — content is either superseded, already in lexicon.json, or a stale temp artifact:

| File | Reason |
|---|---|
| `lexicon.json.broken_backup` | Breakage pre-dates last 3 commits; `backups/` handles this now |
| `lexicon.tmp` | Temp write artifact |
| `old_wordlist.md` | Superseded by `wordlist.md` |
| `test_casalis_cleaned.json` | Dev-time fixture, not referenced by test suite |
| `test_casalis_extraction.json` | Dev-time fixture, not referenced by test suite |
| `genesis_21_batch2.json` | Injection-complete batch; content is now in `lexicon.json` |
| `genesis_22_batch.json` | Injection-complete batch; content is now in `lexicon.json` |
| `cultural_insights_genesis.md` | One-off notes; content captured in `dev_log.md` |

---

## Phase 1 — No Code Changes ✅ Complete (2026-04-27)

**Goal:** Move files only. Zero risk of breaking tests or Makefile.

- [x] Create `historical/casalis/{a,b,c,d,e,f}/`
- [x] Move all `casalis_{letter}_*` files into letter subfolder
- [x] Create `historical/mabille/` and move `mabille_*` files
- [x] Create `historical/staged/` and move all `staged_*` files
- [x] Create `sources/bible/` and move all `st_*.html`, `en_*.html`, `NEW KING JAMES VERSION.json`
- [x] Create `sources/pdfs/` and move both PDF files
- [x] Move `nkjv_wordlist.txt` to `sources/`
- [x] Create `reports/` and move all reports, diffs, review sheets, provenance files
- [x] Delete confirmed-safe stale files

---

## Phase 2 — Schema + Data Dirs ✅ Complete (2026-04-27)

**Goal:** Move schemas and datasets into `schemas/` and `data/`. Update all hardcoded paths in scripts, tests, and Makefile.

- [x] Create `schemas/`, move 4 `*.schema.json` files
- [x] Create `data/`, move `lexicon.json`, `corpus.json`, `attestations.json`, `dictionary*.json`
- [x] Update `tests/test_dictionary_schema.py` — schema + lexicon paths
- [x] Update `tests/test_split_datasets.py` — dictionary + 3 schema paths
- [x] Update argparse defaults in: `enricher.py`, `enrich_with_nkjv.py`, `extract_wordlist.py`, `inject_historical_entries.py`, `join_view.py`, `review_enrichment_diff.py`, `split_datasets.py`, `dedupe_historical_a.py`
- [x] Update hardcoded paths in: `enrich_historical.py`, `fix_casalis_e_extraction.py`, `generate_wordlist.py`, `cleanup_to_headwords.py`
- [x] Update bible HTML paths (broken since Phase 1) in: `enrich_historical.py`, `enrich_with_nkjv.py`, `stage_a_entries.py`, `stage_f_entries.py`
- [x] Update historical input/output defaults in: `stage_a_entries.py`, `stage_f_entries.py`, `inject_historical_entries.py`
- [x] Update Makefile — all targets with explicit file paths
- [x] All 21 tests pass

---

## Phase 3 — Script Reorganisation ✅ Complete (2026-04-27)

**Goal:** Move all 22 pipeline scripts into `pipeline/{ocr,staging,enrichment,export}/`.

- [x] Resolved cross-directory imports before moving:
  - Inlined `stable_hash` into `enricher.py` (was imported from `split_datasets`)
  - Inlined `clean_text`, `contains_term`, `score_verse_match`, `find_best_match` into `stage_a_entries.py` (was imported from `enricher`)
- [x] Created `pipeline/{ocr,staging,enrichment,export}/`
- [x] Created `tests/__init__.py` — adds all four pipeline subdirs to `sys.path` (requires `python3 -m unittest discover -s tests -t . -v` with `-t .`)
- [x] Updated `Makefile` — `test` target uses `-t .`; all script paths updated
- [x] Moved scripts:
  - `pipeline/export/`: `split_datasets.py`, `join_view.py`, `inject_historical_entries.py`, `extract_wordlist.py`, `generate_wordlist.py`, `extract_nkjv_words.py`
  - `pipeline/enrichment/`: `enricher.py`, `enrich_historical.py`, `enrich_with_nkjv.py`, `review_enrichment_diff.py`
  - `pipeline/staging/`: `stage_a_entries.py`, `stage_f_entries.py`, `merge_casalis_sources.py`, `dedupe_historical_a.py`, `locate_a.py`, `extract_a_entries.py`
  - `pipeline/ocr/`: `ocr_split_pages.py`, `extract_casalis_from_ocrsplit.py`, `build_corrected_casalis.py`, `heuristic_cleanup.py`, `cleanup_to_headwords.py`, `fix_casalis_e_extraction.py`
- [x] All 21 tests pass after every move batch

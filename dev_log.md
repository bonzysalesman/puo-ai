# Developer Log: Sesotho-English Dictionary Enrichment

## 2026-02-19

### Initial Progress
- Set up project structure and initialized `dictionary.json`.
- Created `enricher.py` for automated enrichment from JW Bible.
- Overcame network restrictions by using local HTML processing for Genesis 1.
- Recorded additional reference sources for Psalm 103:12 and Romans 13:7 in `dictionary.json`.
- Successfully enriched headwords: **Away, Awe, Heaven, Earth, Deep, Light, Night, Expansion, Land, Sea, Seed, Kind, Sign, Year, Star, Source of light** (16 total entries).

### Challenges & Solutions
- **Network Issues:** Shifted to local HTML processing when direct web requests failed.
- **Matching Logic:** Upgraded to whole-term matching and added `--dry-run`/`--output` safety options.

### Next Steps
- Continue adding raw data entries (headwords and definitions).
- Scale the enrichment script to cover more Bible books as needed.
- Maintain local documentation (`walkthrough.md` and `dev_log.md`).

## 2026-02-24

### Maintenance Updates
- Refactored `enricher.py` for safer matching and configurable CLI:
  - `--dictionary`, `--sesotho-file`, `--english-file`, `--source-label`, `--output`, `--dry-run`, `--verbose`.
- Added `requirements.txt` to pin runtime dependency (`beautifulsoup4`).
- Added tests for:
  - `enricher.py` text cleanup, whole-term matching, and dry-run behavior.
  - `extract_wordlist.py` deduplication/casing/diacritic behavior.
- Clarified project status:
  - Local chapter corpora currently available: `st_gen1.html` and `en_gen1.html`.
  - `st_ps103.html` exists as a placeholder and is empty.

## 2026-03-18

### Skill Formalization
- Converted the ad-hoc dictionary injection process into a formal **Agent Skill** (`dictionary_injection`).
- Developed a professional `inject_entries.py` script with:
  - Automatic timestamped backups.
  - Multi-format JSON support.
  - Lexicographical sorting and **duplicate detection**.
- Injected high-fidelity entries for **Heaven**, **Earth**, **Deep**, **Light**, **Night**, **Expansion**, **Land**, **Sea**, **Seed**, **Kind**, **Source of light**, **Sign**, **Year**, **Star**, **Sea monster**, **Flying creature**, **Creeping thing**, **Wild beast**, **Man**, **Image**, **Male**, **Female**, **Good**, and **Genesis Chapters 1, 2, 3, 4, 5, 6, & 7** (136 entries from Batches 15-38).
    - *Note*: Batch 27 (Gen 2), Batch 32 (Gen 3), Batch 34 (Gen 4), Batch 37 (Gen 6), and Batch 40 (Gen 7) consolidated sequences into stable IDs.
    - *Note*: 185 unique high-fidelity entries added/refined in this session.

### Challenges & Solutions
- **JSON Format Drift:** Handled drift between simple user JSON and structured schema-aligned JSON by making the injection script more flexible.
- **Redundancy:** Improved the skill with duplicate detection logic to maintain lexicon purity.
- **ID Collisions:** Implemented stable-hash-based ID generation for corpus and attestations.

### Next Steps
- Continue Batch 11 injection using the new skill.
- Explore similar skill formalization for other repetitive tasks (e.g., historical OCR cleaning).

## 2026-03-20

### Lexicon Refinement
- Refined **Batch 42 (Genesis 8)** entries with high-fidelity raw data provided by the user.
- Updated headwords: **To subside / decrease**, **Dove**, **Harvest**, **Aroma / Scent**, and **Winter**.
    - Enhanced POS and Syllable metadata.
    - Added contextual **usage examples** directly linked to the lexicon via `corpus.json`.
- Verified integrity with `tests.test_dictionary_schema`.

### Lexicon Expansion
- Injected and refined **Batch 43 (Genesis 9)** entries with stable `st_G9_xxx` IDs.
- Added 5 high-fidelity entries: **Rainbow**, **Sign / Token**, **Farmer**, **Vineyard**, and **Servant / Slave**.
- Enriched each entry with **usage examples** from the Genesis 9 parallel corpus.
- Verified integrity with `tests.test_dictionary_schema`.

### Lexicon Expansion
- Injected and refined **Batch 44 (Genesis 10)** entries.
- Added 8 high-fidelity entries: **Hunter**, **Kingdom / Government**, **To divide**, **Boundary / Border**, **Island / Coastland**, **Language / Tongue**, **Mighty / Strong**, and **Lineage / Ancestry**.
- Integrated contextual **usage examples** for all terms from the Genesis 10 parallel corpus.
- Verified integrity with `tests.test_dictionary_schema`.

### Lexicon Expansion
- Injected and refined **Batch 45 (Genesis 11)** entries.
- Added 7 high-fidelity entries: **To confuse / Muddle**, **To scatter / Disperse**, **Barren**, **Daughter-in-law**, **Bricks**, **Tower**, and **Grandchild**.
- Integrated contextual **usage examples** for all terms from the Genesis 11 parallel corpus.
- Verified integrity with `tests.test_dictionary_schema`.

### Lexicon Expansion & Refinement
- Injected and refined the full **Batch 47 (Genesis 13)** set.
- Expanded to **19 high-fidelity entries**: **Strife / Quarrel**, **Herdsmen / Shepherds**, **Dust**, **Brethren / Kin**, **To be wealthy**, **Right (Direction)**, **Length**, **Silver**, **Well-watered / Irrigated**, **Width / Breadth**, **Sinners**, **Left (Direction)**, **District / Plain**, **Gold**, **Journey / Travels**, **Garden**, **North**, **South**, and **Large trees / Oaks**.
- Enriched all entries with **deep linguistic and cultural nuances** and contextual **usage examples** from the Genesis 13 parallel corpus.
- Verified integrity with `tests.test_dictionary_schema`.

### Lexicon Expansion & Refinement
- Completed a **Comprehensive JW/PEMS Audit (Genesis 9-17)**.
- Updated **108+ entries** across Batches 43-51.
- All entries now strictly conform to the **JW Bible (NWT)** Sesotho text and **Sesotho PEMS (ss-LS)** orthography (Lesotho standard).
- Integrated correct vowel markings (macrons) and consistent `oa`/`ea` spellings for all usage examples and headwords.
- Completed a **Comprehensive JW/PEMS Audit (Genesis 1-3)**.
- Re-audited and refined **Batch 53 (Genesis 19)** expansion with **11 entries** (st_G19_EX_01-11).
- Injected and refined **Batch 54 (Genesis 20)** expansion with **9 entries** (st_G20_EX_01-09).
- Integrated **user nuances**, **JW Bible (Sesotho)**, and **NKJV (English)** usage examples for all new entries.
- All entries strictly conform to **Sesotho PEMS (ss-LS)** orthography.

### Lexicon Expansion & Refinement
- Injected and refined the full **Genesis 21** expansion with **10 entries**: **Isaac (Laughter)**, **To be weaned**, **Scoffing / Mocking**, **Heir**, **Water-skin**, **Bowshot / Distance**, **Archer**, **Loyal Love**, **Beersheba**, and **Tamarisk Tree**.
- Integrated contextual **usage examples** for all terms from the Genesis 21 parallel corpus.
- Verified integrity with `tests.test_dictionary_schema`.

### Lexicon Expansion & Architectural Hardening
- Injected and refined the full **Genesis 22** expansion with **10 entries**: **Burnt Offering**, **To split/chop wood**, **Slaughtering Knife**, **Altar**, **To bind**, **Ram**, **Thicket**, **Jehovah-jire**, **Offspring / Seed**, and **Concubine**.
- **Architectural Normalization**:
    - Migrated all remaining `usage_example` fields from `lexicon.json` to the parallel `corpus.json` and `attestations.json` datasets.
    - Hardened the `inject_entries.py` script to strictly enforce the "split" architecture, ensuring the lexicon remains clean.
    - Standardized stable hashing for all manual and automated injections.
- All entries strictly conform to **Sesotho PEMS (ss-LS)** orthography.
- Verified integrity with `make validate-all` and `make test`.

### Lexicon Expansion
- Injected and refined the full **Genesis 23** expansion with **6 entries**: **To mourn / Lament**, **Burial Place**, **Cave**, **Full Price**, **To weigh out**, and **Deeded / Confirmed**.
- All entries strictly conform to **Sesotho PEMS (ss-LS)** orthography and the normalized split architecture.
- Verified integrity with `make validate-all`.

### Lexicon Expansion
- Injected and refined the full **Genesis 24** expansion with **10 entries**: **Thigh (oath-taking)**, **Mesopotamia**, **To kneel (camels)**, **Pitcher / Jar**, **Trough**, **Nose ring**, **Straw & Feed**, **Nurse / Caretaker**, **To meditate**, and **Veil**.
- All entries strictly conform to **Sesotho PEMS (ss-LS)** orthography and the normalized split architecture.
- Verified integrity with `make validate-all`.

## 2026-04-27

### Architectural Reorganization
- **Workspace Normalization**: Successfully executed the "Workspace Reorganisation Plan," moving from a cluttered root directory (99 files) to a structured hierarchy (7 files in root).
- **Directory Hierarchy**:
    - `data/`: Source-of-truth datasets (`lexicon.json`, `corpus.json`, `attestations.json`).
    - `schemas/`: JSON schemas for all datasets.
    - `pipeline/`: Reorganized into `ocr/`, `staging/`, `enrichment/`, and `export/`.
    - `historical/`: Dedicated space for `casalis/` and `mabille/` OCR artifacts.
    - `sources/`: Parallel Bible HTML and external wordlists.
    - `reports/`: Centralized for extraction and deduplication reports.
- **Path Hardening**: Updated all pipeline scripts, test suites, and the Makefile to reflect the new directory structure. Verified with a full pass of 21 tests.

## 2026-04-30

### Massive Lexicon Expansion (Pentateuch Phase)
- **High-Volume Injection**: Completed a massive "Conversation Extraction" injection, adding **3,253 entries** to the lexicon.
- **Biblical Coverage**:
    - Completed **Genesis (Chapters 25-50)**.
    - Completed **Exodus (Chapters 1-40)**.
    - Completed **Leviticus (Chapters 1-27)**.
    - Completed **Numbers (Chapters 1-25)**.
- **Historical Integration**: Fully integrated historical entries from **Casalis Batches A, B, C, D, E, and F** into the main lexicon.
- **Standardization**:
    - Normalized `entry_id` conventions for book-based entries (e.g., `st_EX01_01`, `st_NUM25_01`).
    - Standardized `derivation` metadata to track provenance (e.g., "Historical Entry (Casalis)").
- **Legacy Compatibility**: Rebuilt `dictionary.joined.json` to ensure backward compatibility with downstream tools after the massive data influx.

### Next Steps
- Continue biblical expansion from **Numbers 26** through the end of the Pentateuch (Deuteronomy).
- Audit recent high-volume entries for empty POS fields and skeletal metadata.
- Begin staging and refining **Mabille Batch A** historical entries.


## 2026-05-10

### Historical Extraction (Mabille Batch 3 & 4)
- **Batch 3**: Processed PDF pages 51-52 (dictionary pages 41-42). Injected 80 entries (Bophefali to Borafi).
- **Batch 4**: Processed PDF pages 53-57 (dictionary pages 43-47). Injected 194 entries (Borahane to Bothaōthè).
- **Tooling**: Verified refined PDF splitter and vision-based extraction pipeline. Standardized staging scripts for rapid ingestion.
- **Batch 5**: Processed PDF pages 58-62 (dictionary pages 48-51). Injected 148 entries (Bothapisi to Botsoali).
- **Batch 6**: Processed PDF pages 62-66 (dictionary pages 52-54). Injected 53 entries (Botsoalle to Butsoèla).

## 2026-06-23

### OCR Stack Verification + eng+fra Default

Verified the OCR → headword-extraction → dictionary chain end-to-end on 3 sample Casalis-A pages (page_012 left/right, page_013 left). The pipeline works at 100% precision against the combined lexicon: every re-OCR'd headword corresponds to a real entry in either `historical/staged/staged_casalis_a.json` or `data/lexicon.json`, including OCR-corruption variants recoverable by fuzzy match.

**Headline numbers (3 pages × 35 baseline lines = 105 lines total):**

| Engine | Baseline-line recovery | Headword match vs lexicon |
|---|---|---|
| Tesseract 5.5.2 (eng) | 92.4% (97/105) | 38/42 = 90.5% direct, +4 fuzzy = 100% precision |
| Tesseract 5.5.2 (eng+fra) | 54.3% by exact-line / 92% by structure | **40/44 = 90.9% direct, +4 fuzzy = 100% precision** |
| Surya 0.20+ | 29.5% (31/105) | wins on per-character conf (0.97) but collapses column-flow into single lines — wrong tool for 2-column dictionaries |

**Key finding:** `eng+fra` is strictly better than `eng`-only for this corpus. It picks up 2 additional real headwords per 3 pages (`Against`, `Agility`) that `eng`-only garbled into variants. Patched `OCRConfig.languages` to default to `["eng", "fra"]` (commit `7c6e00a`).

**Important caveat:** `eng+fra` improves Sesotho diacritics (`mothé` → `mothô`, `éohang` → `tëohang`) but introduces *occasional* new errors in non-Sesotho English words. The "baseline line recovery" metric went *down* on `eng+fra` despite the text being objectively more correct — because the metric does exact-string matching on full lines, and small character-level differences (better diacritics) count as "misses". Don't trust that metric alone; always ground-truth against the lexicon.

### Tools, Lessons, and Gotchas

- **Tesseract lang packs** are not bundled with `tesseract` on Homebrew. `brew install tesseract-lang` pulls the entire ~700 MB bottle — slow on flaky networks (took 22 min before throttling). Workaround: download individual packs (e.g. `fra.traineddata` is 1.1 MB) directly from `https://raw.githubusercontent.com/tesseract-ocr/tessdata_fast/main/<lang>.traineddata` into `/opt/homebrew/share/tessdata/`. No Sesotho pack exists in `tessdata_fast` (`st`, `sso`, `sot` all 404). French is the closest match for Casalis/Mabille/Jacottet/Paroz sources.

- **Surya is the wrong tool for column-scan dictionary OCR.** 121 s/page vs Tesseract 0.6 s/page, and 92% vs 29% line recovery. Surya's architecture is tuned for prose documents and it collapses multi-line definitions into single lines. Keep Tesseract as the primary engine for `casalis_*`/`mabille_*` flows; reserve Surya for full-page scans.

- **OCR "noise" is often a feature, not a bug.** The 4 OCR-corruption variants we found (`Aflernoon`→`Afternoon`, `Ayitate`→`Agitate`, `Afilict`→`Afflict`, `Agarust`→`Against`) all fuzzy-match to real headwords via `difflib.get_close_matches(cutoff=0.7)`. Any downstream inject step should include a fuzzy-match layer or validate against the lexicon before injection. The existing `inject_historical_entries.py` has dedupe but no fuzzy-correct step — candidate improvement.

- **OCR audits must always check the lexicon, not just line counts.** "92% baseline line recovery" sounds great until you learn the 8% miss is real headwords, and "54% line recovery" sounds bad until you learn those lines are actually more correct. Always end-to-end ground-truth against `data/lexicon.json` + `historical/staged/*.json`.

- **`python -m` vs direct invocation**: `pipeline/ocr/test_casalis_extraction.py` line 11 uses `from enhanced_ocr_stack import ...` (bare). Runs fine via `python -m unittest` but fails with `ImportError: attempted relative import` when invoked directly. Pre-existing on `main HEAD`; not caused by today's edits. **Fix candidate**: change to `from .sesotho_ocr_enhancer import ...` is already correct in `enhanced_ocr_stack.py` line 17; the test file just needs the matching relative imports.

### Repo Hygiene Findings (audit, not fixes)

- **5 OCR files were untracked on `main`**, including the very files we just patched. `enhanced_ocr_stack.py` and `test_casalis_extraction.py` were committed in `7c6e00a`. `sesotho_ocr_enhancer.py` is a required runtime dependency of `enhanced_ocr_stack.py` and is committed today as a separate "missing dependency" patch. **6 more `pipeline/ocr/*.py` files remain untracked** (`general_vision_extractor.py`, `vision_model_extractor.py`, `ocr_paroz.py`, `ocr_split_pages_refined.py`, `parse_mabille_batch_12.py`, `parse_mabille_batch_13.py`); none are imported by the committed code, so they can stay untracked for now.

- **`brew install tesseract-lang` failed on flaky ghcr.io download**; **workaround**: direct `fra.traineddata` download. Documented in skill update.

- **`.gitignore` is too narrow.** Doesn't cover `historical/**/images*`, `historical/mabille/batch_*_raw.json`, `historical/staged/staged_demo*.json`, `data/*.backup*`, `reports/_run_*.py`, `reports/ocr_pipeline_audit_*/`. Adding ~3,500 files to staging by accident is a real risk (encountered during this session — recovered via `git reset HEAD --`).

### Files Modified Today

- `pipeline/ocr/enhanced_ocr_stack.py` — `OCRConfig.languages` defaults to `["eng", "fra"]`; `__post_init__` mutator; `DEFAULT_LANGUAGES` constant exported.
- `pipeline/ocr/test_casalis_extraction.py` — hardcoded `languages=["eng"]` → `["eng", "fra"]`.
- `pipeline/ocr/sesotho_ocr_enhancer.py` — committed as required dependency (no functional changes).
- `_agents/skills/historical_pdf_extraction/SKILL.md` — added "Tesseract Language Packs" and "Audit Before Commit" sections.
- `dev_log.md` — this entry.

### Artifacts (audit trail in `reports/`)

- `reports/ocr_pipeline_audit_20260623T045518Z/` — eng-only baseline (3 pages)
- `reports/ocr_pipeline_audit_v2_20260623T062007Z/` — eng+fra results
- `reports/_run_*.py` — 6 helper scripts (intentionally untracked, see `.gitignore` candidate)
- `reports/enhanced_ocr_test_results.json`, `reports/sesotho_enhancement_test_results.json` — pre-existing

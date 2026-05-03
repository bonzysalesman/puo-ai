# Walkthrough: Sesotho-English Dictionary Enrichment

This walkthrough documents the current enrichment flow and the repository state as of February 24, 2026.

## Overview

The project enriches dictionary senses in `dictionary.json` by matching Sesotho terms against local JW Bible chapter HTML and attaching aligned English verse text.

## Current Local Corpus

- Sesotho Genesis 1: `st_gen1.html`
- English Genesis 1: `en_gen1.html`
- English Bible (Complete): `NEW KING JAMES VERSION.json`
- Placeholder file (empty): `st_ps103.html`

## Enrichment Workflow

1. Parse local verse HTML (`span.verse`) for both Sesotho and English files.
2. Remove inline markers and normalize text.
3. Match each `sesotho_term` using whole-term, case-insensitive matching.
   - Candidate verses are ranked by configurable weighted score:
     - matched term count
     - matched term total length
     - verse length penalty
4. If a verse id exists in both languages, write a `usage_example` to the matched sense.
5. Save changes either in-place or to an output file.

## Commands

Dry run (no writes):

```bash
python3 enricher.py --dry-run --source-label "JW Bible - Genesis 1"
```

Dry run while ignoring generic terms:

```bash
python3 enricher.py --dry-run --source-label "JW Bible - Genesis 1" --stop-terms "le,ea,ho"
```

Dry run with custom scoring weights:

```bash
python3 enricher.py --dry-run --source-label "JW Bible - Genesis 1" --weight-term-count 1200 --weight-term-length 1 --weight-verse-length-penalty 0.02
```

Write to a new file:

```bash
python3 enricher.py --output dictionary.enriched.json --source-label "JW Bible - Genesis 1"
```

Generate deterministic review diff:

```bash
python3 review_enrichment_diff.py --base dictionary.json --candidate dictionary.enriched.json --output enrichment_diff.md
```

Generate deduplicated word list:

```bash
python3 extract_wordlist.py --dictionary dictionary.json --output wordlist.md
```

Run tests:

```bash
python3 -m unittest discover -s tests -v
```

Validate schema only:

```bash
python3 -m unittest tests.test_dictionary_schema -v
```

## Notes on Sources

- Most `usage_example.source` values are Genesis 1 verse references generated from local HTML.
- A small number of dictionary entries currently contain source strings for Psalm 103:12 and Romans 13:7.
- Those two references are present as data labels in `dictionary.json`; equivalent local chapter HTML is not currently committed in this repository.
- `NEW KING JAMES VERSION.json` provides a comprehensive English reference source. Its structure follows a nested hierarchy: `{"BookName": {"ChapterNumber": {"VerseNumber": "Text"}}}`.

## Updated Casalis F Data
The `casalis_f_cleaned_ocrsplit.json` file was updated to replace a range of entries (lines 1289-2575) with cleaned, accurate data.

### Changes Made:
- **Cleaned OCR Noise**: Removed transcription errors and extra characters (e.g., `]`, `|`, `5`, `“iz`).
- **Corrected Headwords and POS**: Fixed misrecognized words like `Fuar` -> `Fix`, `Fisher-man` -> `Fisherman`, and corrected parts of speech where applicable.
- **Improved Sesotho Translations**: Cleaned and standardized Sesotho definitions.
- **Removed Duplicates**: Identified and eliminated a duplicate entry for "Flux".

### Validation:
- Verified the JSON structure using `jq`, confirming the file is valid.
- Manually checked the first and last entries of the replacement range for correctness.

## Lexicon Integration
Entries from `casalis_f_cleaned_ocrsplit.json` have been extracted and merged into the master `lexicon.json`.

### Integration Summary:
- **Entries Processed**: 316
- **New Entries Injected**: 315
- **Merged Senses**: 1
- **New Attestations**: 80 (matched against Genesis 1, Genesis 2, Psalm 103, and Romans 13)

### Process:
1. Created `stage_f_entries.py` to extract Sesotho headwords and map parts of speech from the Casalis format.
2. Verified usage examples in the local corpus during the staging phase.
3. Used `inject_historical_entries.py` to perform a stable-hash-based merge into the master lexicon.

## Genesis 2 Parallel Corpus Processing
The lexicon was enriched with matches from the Genesis 2 parallel corpus (`st_gen2.html` and `en_gen2.html`).

### Enrichment Results:
- **New Senses Enriched**: 19
- **Total Existing Covered**: 512
- **Source Label**: `JW Bible - Gen2`

### Verification:
- Confirmed new attestations in `attestations.json` for several entries (e.g., `Firmness` and `Forego` where applicable).
- Verified consistent formatting with existing `enricher_split_v1` entries.

## New King James Version (NKJV) Enrichment
The lexicon was enriched with usage examples from the `NEW KING JAMES VERSION.json`, stored alongside existing NWT (JW Bible) examples.

### Enrichment Results:
- **New Senses Enriched with NKJV**: 552
- **Coexistence**: Verified that senses now concurrently hold both NWT and NKJV attestations.
- **Source Label**: `NKJV`

### Process:
1. Created `enrich_with_nkjv.py` to map the nested JSON structure of the NKJV file to the `vBBCCCVVV` ID format.
2. Modified the injection logic to allow multiple attestations per sense (NWT + NKJV).
3. Processed Genesis 1, Genesis 2, Psalms 103, and Romans 13 against the master lexicon.

## NKJV Word List Extraction
Generated an exhaustive unique word list from the `NEW KING JAMES VERSION.json`.

### Results:
- **Unique Words Extracted**: 12,839
- **Output File**: `nkjv_wordlist.txt`

### Process:
1. Created `extract_nkjv_words.py` with custom tokenization (filtering punctuation, maintaining apostrophes for contractions/possessives).
2. Processed the entire NKJV JSON structure to deduplicate and lowercase all English tokens.
3. Sorted the resulting list alphabetically.

## Dictionary Injection Skill
Formalized the dictionary enrichment workflow into a reusable **Agent Skill**.

### Improvements:
- **`SKILL.md`**: Standardized instructions for agents to follow.
- **`inject_entries.py`**: A robust script that handles multiple JSON formats, creates automatic backups, and ensures `lexicon.json` sorting.
- **Safety**: Integrated schema validation and timestamped backups (`backups/` directory).

## Structured Lexicon Expansion (Genesis Chapters 1 & 2)
Added high-fidelity dictionary entries from Genesis 1 and 2 using the `dictionary_injection` skill.

### Results:
- **Batches 15-21**: 76 entries
- **Batches 22-26 (Gen 2 Refinement Phase)**: Iterative refinement of Genesis 2 terms.
- **Batch 27 (Gen 2 Consolidation)**: 16 entriessynchronized with stable `st_G2_001`-`016` IDs.
- **Manual Refinement (Batch 28)**: Re-added displaced terms **'Sleep'** (`st_G2_020`) and **'Flesh'** (`st_G2_021`) under new stable IDs.
- **Lexicon Cleanup**: Successfully removed redundant orphans (`st_G2_017`, `st_G2_019`) to maintain a clean record set.
- **Batch 28 (Genesis 3 Kickoff)**: Added first 6 entries from Genesis 3.
- **Batch 29 (Genesis 3 Expansion)**: Added 6 more entries (Hide, Deceive, etc.).
- **Batch 30 (Genesis 3 Refinement/Re-mapping)**: Refined 'Serpent', 'To deceive', and 'Enmity'.
- **Batch 31 (Genesis 3 Expansion)**: Added 6 entries (Pain, Thorn, etc.).
- **Batch 32 (Genesis 3 Consolidation)**: 13 entries synchronized with stable `st_G3_001`-`013` IDs.
- **Batch 33 (Genesis 4 Expansion)**: Added 14 entries (Brother, Shepherd, etc.).
- **Batch 34 (Genesis 4 Refinement/Re-mapping)**: Refined 7 key terms ('Shepherd', 'Offering', 'Blood', 'Wanderer', 'Iron', 'City', and 'Vengeance') with stable `st_G4_001`-`007` IDs.
- **Manual Refinement (Batch 35)**: Re-added displaced G4 terms **'Brother'** (`st_G4_008`), **'Firstborn'** (`st_G4_009`), **'Anger'** (`st_G4_010`), and **'Attack'** (`st_G4_014`).
- **Genesis 5 Kickoff (Batch 35)**: Added first 4 entries from Genesis 5 ('Likeness / Shape', 'To beget', 'Comfort / Relief', and 'To die') with stable `st_G5_001`-`004` IDs.
- **Genesis 6 Expansion (Batch 36)**: Added 9 entries ('Wickedness', 'Regret', etc.).
- **Batch 37 (Genesis 6 Refinement/Re-mapping)**: Refined 5 key terms ('Violence', 'Flood', 'Covenant', 'Cubit', and 'Regret').
- **Manual Refinement (Batch 39)**: Re-added displaced G6 terms **'Wickedness'** (`st_G6_007`), **'Just / Righteous'** (`st_G6_008`), and **'Ark'** (`st_G6_009`).
- **Genesis 7 Expansion (Batch 38)**: Added 9 entries ('Household', 'Clean', etc.).
- **Batch 40 (Genesis 7 Refinement/Re-mapping)**: Refined 5 key terms ('Clean', 'Fountain', 'Deep', 'Float', and 'Remain').
- **Manual Refinement (Batch 41)**: Re-added displaced G7 terms **'Household / Family'** (`st_G7_007`) and **'To cause rain'** (`st_G7_009`).
- **Genesis 8 Expansion (Batch 42)**: Added 5 entries ('To subside / decrease', 'Dove', 'Harvest', 'Aroma / Scent', 'Winter') with stable `st_G8_001`-`005` IDs. 
- **Batch 42 Refinement**: Updated these entries with high-fidelity usage examples from Genesis 8 and refined POS/Syllable metadata.
- **Genesis 9 Expansion (Batch 43)**: Added 5 refined entries ('Rainbow', 'Sign / Token', 'Farmer', 'Vineyard', 'Servant / Slave') with stable `st_G9_001`-`005` IDs.
- **Genesis 10 Expansion (Batch 44)**: Added 8 entries ('Hunter', 'Kingdom / Government', 'To divide', 'Boundary / Border', 'Island / Coastland', 'Language / Tongue', 'Mighty / Strong', 'Lineage / Ancestry') with stable `st_G10_001`-`008` IDs.
- **Genesis 11 Expansion (Batch 45)**: Added 7 entries ('To confuse / Muddle', 'To scatter / Disperse', 'Barren', 'Daughter-in-law', 'Bricks', 'Tower', 'Grandchild') with stable `st_G11_001`-`007` IDs.
- **Genesis 12 Expansion (Batch 46)**: Added 8 entries ('Blessing', 'Famine / Hunger', 'Sojourner / Residing Alien', 'Sister', 'Plagues / Blows', 'Kin / Relatives', 'To curse', 'To pitch a tent') with stable `st_G12_001`-`008` IDs.
- **Genesis 13 Expansion (Batch 47)**: Added 19 entries ('Strife / Quarrel', 'Herdsmen / Shepherds', 'Dust', 'Brethren / Kin', 'To be wealthy', 'Right (Direction)', 'Length', 'Silver', 'Well-watered / Irrigated', 'Width / Breadth', 'Sinners', 'Left (Direction)', 'District / Plain', 'Gold', 'Journey / Travels', 'Garden', 'North', 'South', 'Large trees / Oaks') with stable `st_G13_001`-`019` IDs. 
- **Genesis 14 Expansion (Batch 48)**: Added 10 entries ('To rebel', 'Pits', 'Allies', 'Captivity', 'Trained men', 'To rescue / recover', 'Priest', 'Tithe / Tenth', 'Oath / Vow', 'Sandal strap') with stable `st_G14_001`-`010` IDs.
- **Genesis 15 Mega Expansion (Batch 49)**: Added 27 entries ('Word', 'Vision', 'Shield', 'Reward', 'Lord / Ruler', 'Childless', 'Offspring / Seed', 'Heir', 'Stars', 'To count / Number', 'Faith / Belief', 'Righteousness', 'Heifer', 'She-goat', 'Ram', 'Turtledove', 'To slice / Cut in two', 'Carcasses', 'Deep sleep', 'Horror / Terror', 'Strangers / Sojourners', 'To afflict / Oppress', 'To judge', 'Generation', 'Furnace / Oven', 'Torch', 'River') with stable `st_G15_EX_001`-`027` IDs.
- **Genesis 16 Expansion & Refinement (Batch 50)**: Added 10 entries ('Maidservant', 'Restrained / Closed', 'Despised / Belittled', 'To treat harshly', 'Angel', 'Spring / Well', 'To submit / Humble', 'Affliction / Sorrow', 'Wild donkey', 'God of seeing') with stable `st_G16_C01`-`C10` IDs. Refined with linguistic nuance and final user-provided JSON structure.
- **Genesis 17 Expansion (Batch 51)**: Added 11 entries ('Almighty God', 'Blameless / Faultless', 'To Circumcise', 'Sign / Token', 'Princes / Small Kings', 'Set time / Appointed time', 'Name / Identity', 'Everlasting / Eternal', 'Cut off / Expelled', 'To Bless', 'To laugh') with stable `st_G17_001`-`011` IDs.
- **Comprehensive JW/PEMS Audit (Genesis 1-3)**: Audited and updated **43+ entries** across Batches 35-37. Integrated **JW New World Translation (Sesotho)** and **NKJV (English)** usage examples. Strictly aligned all headwords/text with **Sesotho PEMS (ss-LS)** orthography.
- **Comprehensive JW/PEMS Audit (Genesis 1-3)**: Audited and updated **43+ entries** across Batches 35-37. Integrated **JW New World Translation (Sesotho)** and **NKJV (English)** usage examples. Strictly aligned all headwords/text with **Sesotho PEMS (ss-LS)** orthography.
- **Genesis 19 Expansion & Refinement (Batch 53)**: Added and re-audited **11 entries** ('City Gate', 'Unleavened Bread', 'To share mats / Intimacy', 'Sojourner / Alien', 'Blindness', 'Joking / Mocking', 'Mercy / Compassion', 'The Plain / District', 'Brimstone / Sulfur', 'Pillar of Salt', 'Firstborn') with stable `st_G19_EX_01`-`11` IDs. **Integrated user nuances, exactly matched provided JSON, and strictly conformed to JW Bible (Sesotho) and NKJV (English) orthography/examples.** Preserved `nuance_en` and `usage_example` within the lexicon for high-fidelity auditing.
- **Genesis 20 Expansion & Refinement (Batch 54)**: Added **9 entries** ('Integrity of heart', 'Prophet', 'Intercessory Prayer', 'Vindication / Veil', 'Womb', 'South / Negeb', 'Owned by a master', 'Fear of God', 'Wander / Roam') with stable `st_G20_EX_01`-`09` IDs. **Integrated user nuances, strictly conformed to JW Bible (Sesotho) and NKJV (English) orthography/examples, and preserved all metadata in the lexicon.**
- **Genesis 18 Expansion & Refinement (Batch 52)**: Added and refined **10 entries** ('Terebinth / Great Trees', 'Favor / Grace', 'To refresh', 'Menstrual cycle / Period', 'Outcry / Loud complaint', 'Dust and Ashes', 'Fine Flour', 'Butter / Curds', 'Truly / Indeed', 'Far be it') with stable `st_G18_C01`-`10` IDs. **Integrated user nuances and strictly conformed to JW Bible (Sesotho) and NKJV (English) orthography/examples.**
- **Comprehensive JW/PEMS Audit (Genesis 5-8)**: Audited and updated **32 entries** across Batches 39-42. Integrated **JW New World Translation (Sesotho)** and **NKJV (English)** usage examples. Strictly aligned all headwords/text with **Sesotho PEMS (ss-LS)** orthography.
- **Comprehensive JW/PEMS Audit (Genesis 4)**: Audited and updated **14 entries** in Batch 38. Integrated **JW New World Translation (Sesotho)** and **NKJV (English)** usage examples. Strictly aligned all headwords/text with **Sesotho PEMS (ss-LS)** orthography.
- **Comprehensive JW/PEMS Audit (Genesis 9-17)**: Audited and updated **108+ entries** across Batches 43-51. Integrated **JW New World Translation** usage examples and strictly aligned all headwords/text with **Sesotho PEMS (ss-LS)** orthography (vowel markings, `oa`/`ea` spellings).
- **Verification**: Passed `tests.test_dictionary_schema`.

## Normalization & Architectural Hardening (April 2026)
Successfully transitioned the repository to a fully normalized "split" architecture.

### Key Refinements:
- **Lexicon Normalization**: Migrated all remaining `usage_example` fields from `lexicon.json` to the parallel `corpus.json` and `attestations.json` datasets.
- **Source of Truth Enforcement**: Formally decommissioned `dictionary.json` as a source of truth, moving it to `data/legacy/`.
- **Pipeline Hardening**: Updated `inject_entries.py` and `enricher.py` to strictly enforce split-mode operations, ensuring the lexicon remains free of embedded usage examples.
- **Maintenance Tooling**:
    - `make normalize-lexicon`: Automated extraction of any orphaned examples in the lexicon.
    - `make prune-backups`: Automatic rotation of the `backups/` directory.
    - `make ci`: Comprehensive validation suite for continuous integration.

### Validation:
- Verified that all datasets strictly conform to their respective JSON schemas.
- Confirmed that `lexicon.json` contains exactly 0 `usage_example` fields.

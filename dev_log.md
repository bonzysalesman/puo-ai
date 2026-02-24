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

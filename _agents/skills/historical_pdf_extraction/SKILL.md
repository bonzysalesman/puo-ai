---
name: historical_pdf_extraction
description: Extracts text from historical two-column dictionary PDFs and uses an LLM to clean up OCR noise.
---

# Historical PDF Extraction Pipeline

This skill provides a reproducible workflow for extracting and cleaning dictionary entries from scanned historical PDFs containing noisy OCR and two-column layouts.

## The Challenge
Historical dictionary PDFs (e.g., Casalis, Mabille) typically suffer from:
1. **Severe OCR Degradation**: Characters are frequently misread (e.g., `in` instead of `m`, `11.` instead of `n.`).
2. **Column Layouts**: Standard text extraction mixes text horizontally across columns, scrambling the reading order.
3. **Mangled Formatting**: Critical entry delimiters are often lost.

## The Pipeline

### Step 1: Spatial Parsing
Run the spatial parser to extract text blocks while respecting column boundaries.
```bash
python3 scripts/test_historical_extraction.py
```
This script uses `PyMuPDF` (`fitz`) to sort text blocks first by the X-axis (defining the left/right column) and then by the Y-axis (top-to-bottom reading flow). It uses heuristic Regex to bundle the text into noisy JSON chunks.

### Step 2: LLM Contextual Cleanup
Because the raw JSON chunks contain severe OCR artifacts that cannot be reliably fixed with Regex alone, they must be processed by an LLM.
```bash
python3 scripts/llm_pipeline_demo.py
```
This step acts as the cognitive layer. The script takes the noisy strings and uses semantic context to correct spelling, modernize orthography, and format the data perfectly for database injection.

## Environment Requirements
- `PyMuPDF` must be installed: `pip3 install PyMuPDF`
- An active LLM API Key (OpenAI, Gemini, Anthropic) configured in the environment is required to scale the `llm_pipeline_demo.py` script across full hundreds-of-pages documents.

## Usage Instructions
When a user requests to extract more pages:
1. Ensure the target PDF is in the workspace.
2. Modify `scripts/test_historical_extraction.py` to target the desired page range.
3. Execute the Python scripts sequentially to generate the `*_cleaned.json` output.

## Tesseract Language Packs

Tesseract on Homebrew installs **without any language data** beyond `eng`. For historical Sesotho sources (Casalis, Mabille, Jacottet, Paroz) the source language is French, so `fra` improves Sesotho diacritic handling dramatically.

**Install `fra` directly (recommended, ~1 MB, fast):**
```bash
sudo curl -sSL -o /opt/homebrew/share/tessdata/fra.traineddata \
  https://raw.githubusercontent.com/tesseract-ocr/tessdata_fast/main/fra.traineddata
```

**Verify available languages:** `tesseract --list-langs` should list `eng fra osd snum`.

**Avoid `brew install tesseract-lang`** — it pulls a ~700 MB bottle that is slow on flaky networks (took 22 min in a 2026-06-23 audit before throttling). Individual packs are 1-3 MB each and install in seconds.

**No Sesotho pack exists** in `tessdata_fast` (`st`, `sso`, `sot` all 404). `fra` is the closest match.

**Use both:** pass `-l eng+fra` to Tesseract. `pipeline/ocr/enhanced_ocr_stack.py` defaults to `["eng", "fra"]` for historical work as of 2026-06-23.

## Audit Before Commit (Repo Hygiene)

When committing OCR-related changes, **always check that required runtime dependencies are tracked in git**. The 2026-06-23 audit caught `pipeline/ocr/enhanced_ocr_stack.py` and `pipeline/ocr/test_casalis_extraction.py` being committed without their required dependency `pipeline/ocr/sesotho_ocr_enhancer.py` (which had been sitting untracked on `main`). A fresh checkout from that commit would have failed at import time.

Before committing any change to `pipeline/ocr/`:
1. `git ls-files pipeline/ocr/` to see what's tracked.
2. `ls pipeline/ocr/*.py | xargs -I {} sh -c 'git ls-files {} >/dev/null 2>&1 || echo "UNTRACKED: {}"'` to find untracked siblings.
3. If the file you're editing imports a sibling that's untracked, **commit the sibling in the same commit** or split the commit so the dependency lands first.

When staging OCR work:
- `git add -- pipeline/ocr/enhanced_ocr_stack.py` (use `--` to avoid accidentally staging thousands of untracked image dumps, raw OCR JSON, and demo files that lack `.gitignore` entries).
- Always run `git diff --staged --stat` before committing.
- If you accidentally stage everything: `git reset HEAD --` (preserves working-tree edits).

## Engine Selection (Tesseract vs Surya)

For 2-column historical dictionaries, **Tesseract wins** decisively:

| | Tesseract (eng+fra) | Surya 0.20+ |
|---|---|---|
| Wall time per page | ~0.6 s | ~120 s |
| Baseline-line recovery | 92% | 29% |
| Best for | Column-scan dictionary OCR | Full-page prose scans |

Surya collapses multi-line definitions onto single lines (good for prose, bad for dictionaries). Reserve Surya for full-page prose documents where per-character confidence matters more than column-flow ordering.

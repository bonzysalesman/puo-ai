# Casalis A OCR-Split Provenance

## Source
- PDF: `englishsothovoca00casauoft.pdf`
- Page range rendered: 0-based `11..19` (human pages `12..20`)
- Split method: each page rendered at 300 DPI and split into left/right column images.

## OCR Method
- OCR engine: `tesseract 5.5.2`
- Pipeline script: `ocr_split_pages.py`
- OCR text inputs: `ocr_splits/casalis_a/page_XXX_{left|right}.txt`
- Manifest: `ocr_splits/casalis_a/manifest.json`

## Extraction Method
- Parser script: `extract_casalis_from_ocrsplit.py`
- Output filtered to headwords normalized to initial `A`.
- Each extracted entry includes a `source` object:
  - `page_index`, `page_number`, `column`, `image`, `text_file`, `method`

## Output Files
- `casalis_a_raw_ocrsplit.json`
  - Fields: `headword_english`, `pos_raw`, `definition_raw`, `source`
- `casalis_a_cleaned_ocrsplit.json`
  - Fields: `headword_english`, `pos`, `sesotho`, `source`

## Current Extraction Count
- `246` entries

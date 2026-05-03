# Casalis B OCR-Split Provenance

## Source
- PDF: `englishsothovoca00casauoft.pdf`
- Page range rendered: 0-based `20..30` (human pages `21..31`)
- Split method: each page rendered at 300 DPI and split into left/right column images.

## OCR Method
- OCR engine: `tesseract 5.5.2`
- Pipeline script: `ocr_split_pages.py`
- OCR text inputs: `ocr_splits/casalis_b/page_XXX_{left|right}.txt`
- Manifest: `ocr_splits/casalis_b/manifest.json`

## Extraction Method
- Parser script: `extract_casalis_from_ocrsplit.py`
- Target letter: `B`
- Each extracted entry includes a `source` object:
  - `page_index`, `page_number`, `column`, `image`, `text_file`, `method`

## Output Files
- `casalis_b_raw_ocrsplit.json`
- `casalis_b_cleaned_ocrsplit.json`

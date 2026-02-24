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

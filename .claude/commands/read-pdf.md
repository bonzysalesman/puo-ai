---
name: read-pdf
description: 'Read and extract text from a PDF file in this project, with page-range support. Optimised for the historical scanned dictionaries (Casalis, Mabille). Usage: /read-pdf <filename> [pages]'
---

You are reading a PDF file from this project. Follow these steps:

## Step 1 – Identify the file

If the user supplied a filename argument, use it.  Known project PDFs:
- `englishsothovoca00casauoft.pdf` — Casalis *English-Sesotho Vocabulary* (scanned, two-column)
- `Mabille_Adolphe_Sesuto_English_Dictionary.pdf` — Mabille dictionary (scanned, two-column)

If no filename was supplied, ask the user which PDF to read.

## Step 2 – Determine page range

If the user supplied a page range (e.g. "pages 10-15"), extract only those pages.
For large PDFs (> 10 pages), always ask for a page range before reading — do not attempt to read the whole file at once.

## Step 3 – Read the PDF

Use the Read tool with the absolute path `/Users/bonzysalesman/Project/PUO-AI/<filename>` and the `pages` parameter if a range was specified.

## Step 4 – Report what you found

After reading, summarise:
- Number of pages read
- Language(s) detected (Sesotho / English)
- Column layout (single / two-column)
- Any OCR quality issues noticed
- Sample headwords found (up to 10)

## Step 5 – Offer next actions

Suggest what to do with the extracted content:
1. Run through the existing `_agents/skills/historical_pdf_extraction/` pipeline (PyMuPDF + LLM cleanup)
2. Extract entries directly into a staging JSON for injection via `_agents/skills/dictionary_injection/`
3. Read additional pages

## Notes

- The Casalis PDF is ~200 pages; the Mabille PDF is larger.
- Both are **scanned images** — Claude's vision layer reads them but `pdftotext` will produce empty output on them.
- For automated bulk extraction across many pages, use `_agents/skills/historical_pdf_extraction/scripts/` (PyMuPDF + tesseract pipeline) instead of this skill.
- Maximum 20 pages per Read call.

---
name: add-karpathy-llm-wiki
description: 'Set up a persistent wiki knowledge base using the Karpathy LLM Wiki pattern. Use when the user wants to build a structured, queryable wiki from sources like PDFs, URLs, or text. Especially useful for organising the Sesotho lexicon knowledge base.'
---

# Add Karpathy LLM Wiki

Set up a persistent wiki knowledge base for this project, based on Karpathy's LLM Wiki pattern.

## Step 1: Explain the pattern

Briefly summarise the LLM Wiki idea to the user:

> A wiki that lives as plain markdown files in your repo. You feed it sources (PDFs, URLs, notes, transcripts). An LLM ingests each source sequentially, extracts knowledge, and writes or updates wiki pages. A schema file defines conventions. An index tracks all pages. Periodic lint runs keep it coherent.

Ask if this matches what they want to build.

## Step 2: Choose a location

Ask the user where the wiki should live:
1. **`docs/wiki/`** — alongside existing project docs (recommended for PUO-AI)
2. **A dedicated top-level `wiki/` folder**
3. **Somewhere else** — ask for the path

## Step 3: Design the wiki collaboratively

Discuss with the user:
- **Domain**: What is this wiki about? (e.g. "Sesotho linguistic knowledge", "Casalis dictionary analysis", "Lexicography methodology")
- **Source types**: What will be ingested? Options relevant to this project:
  - PDF pages from Casalis / Mabille dictionaries (use `/read-pdf` skill)
  - Entries already in `lexicon.json`
  - Bible parallel verses from `corpus.json`
  - Research notes / dev log entries
  - Web URLs (linguistic references, orthography guides)
- **Architecture**: Full three-layer (sources / wiki pages / schema) or simplified (wiki pages + index only)?
- **Conventions**: Any specific naming or structure preferences?

## Step 4: Create the directory structure

Based on the agreed location (e.g. `docs/wiki/`), create:

```
<wiki-root>/
  sources/          # raw ingested source files (PDFs, txt dumps, urls.md)
  pages/            # curated wiki pages, one topic per file
  index.md          # master index of all pages and their status
  log.md            # ingestion log (what was processed, when, what changed)
  SCHEMA.md         # conventions: naming rules, page structure, tag vocabulary
```

Create `index.md`, `log.md`, and `SCHEMA.md` with appropriate starter content for this project's domain.

## Step 5: Create SCHEMA.md

Write a schema tailored to this project. For a Sesotho lexicography wiki, a good schema covers:
- Page naming: `topic-kebab-case.md`
- Frontmatter fields: `title`, `tags`, `last-updated`, `sources`
- Section conventions: Overview, Linguistic notes, Examples, Cross-references
- Tag vocabulary: `sesotho`, `etymology`, `biblical`, `casalis`, `mabille`, `orthography`, `morphology`

## Step 6: Check source handling capabilities

Based on the source types from Step 3, confirm what's available:
- **PDFs**: Use `/read-pdf` (installed in this project) — reads up to 20 pages at a time via Claude's vision
- **URLs**: Use the built-in WebFetch tool
- **JSON data**: Read directly from `lexicon.json`, `corpus.json` etc.
- **Images** (scanned pages): Claude can read PNG/JPG directly with the Read tool

No additional installs are needed for this project's typical sources.

## Step 7: Ingest a first source (optional)

Offer to run the first ingestion now as a test:
1. Pick one source with the user (e.g. "read Casalis PDF pages 1-5")
2. Use `/read-pdf` or Read tool to extract content
3. Write one or two wiki pages based on what was found
4. Update `index.md` and `log.md`

## Step 8: Document the wiki workflow

Add a brief section to this project's `dev_log.md` or `walkthrough.md` explaining:
- Where the wiki lives
- How to add a new source
- How to run a lint/consistency check

## Notes

- Ingest **one source at a time**, sequentially — do not batch multiple sources in a single pass.
- The wiki is intentionally low-structure: the schema guides, but the LLM figures out the rest.
- For bulk lexicon data, it is better to query `lexicon.json` programmatically than to duplicate it into the wiki.
- Periodic lint: ask the user if they want a reminder scheduled to review wiki coherence (e.g. monthly).

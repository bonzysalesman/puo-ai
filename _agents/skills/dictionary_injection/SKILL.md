---
name: dictionary_injection
description: Use this skill to inject new dictionary entries into the Sesotho-English lexicon datasets (lexicon.json, corpus.json, attestations.json). It handles both simple and structured JSON input formats, updates all related files, and ensures schema compliance.
---

# Dictionary Injection Skill

This skill automates the process of adding new, validated entries to the **PUO-AI** Sesotho-English dictionary.

## Prerequisites

- Python 3.x
- Existing `lexicon.json`, `corpus.json`, and `attestations.json` files in the root directory.

## Core Workflow

### 1. Receive/Prepare New Entries
The user provides new dictionary entries in JSON format. These can be:
- **Simple format**: Basic fields like `headword_english`, `pos`, `headword_sesotho`, etc.
- **Structured format**: More detailed fields including `tone_marked`, `ipa`, and structured `pos` objects.

### 2. Run the Injection Script
Use the bundled `inject_entries.py` script to process the new data.

```bash
python3 _agents/skills/dictionary_injection/scripts/inject_entries.py path/to/new_entries.json
```

The script will:
- Generate unique IDs for entries, senses, and corpus fragments.
- Partition the data correctly across `lexicon.json`, `corpus.json`, and `attestations.json`.
- Sort the `lexicon.json` alphabetically.
- Create a timestamped backup of existing files before modification.

### 3. Verify Integrity
After injection, always run the schema validation tests to ensure the datasets are still valid.

```bash
python3 -m unittest tests.test_dictionary_schema -v
```

## Best Practices

- **Atomic Batches**: Inject words in small, logical batches (e.g., words starting with the same letter or related semantic groups).
- **Manual Review**: Occasionally spot-check the `lexicon.json` to ensure morphological derivations and noun classes are correctly formatted.
- **Cleaning Up**: Remove temporary JSON files provided by the user after successful injection and validation.

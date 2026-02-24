PYTHON ?= python3

.PHONY: install test validate-schema enrich-dry enrich-write enrich-stage review-stage wordlist

install:
	$(PYTHON) -m pip install -r requirements.txt

test:
	$(PYTHON) -m unittest discover -s tests -v

validate-schema:
	$(PYTHON) -m unittest tests.test_dictionary_schema -v

enrich-dry:
	$(PYTHON) enricher.py --dry-run --source-label "JW Bible - Genesis 1"

enrich-write:
	$(PYTHON) enricher.py --output dictionary.enriched.json --source-label "JW Bible - Genesis 1"

enrich-stage:
	$(PYTHON) enricher.py --output dictionary.enriched.json --source-label "JW Bible - Genesis 1"

review-stage:
	$(PYTHON) review_enrichment_diff.py --base dictionary.json --candidate dictionary.enriched.json --output enrichment_diff.md

wordlist:
	$(PYTHON) extract_wordlist.py --dictionary dictionary.json --output wordlist.md

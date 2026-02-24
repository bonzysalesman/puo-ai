PYTHON ?= python3

.PHONY: install test enrich-dry enrich-write wordlist

install:
	$(PYTHON) -m pip install -r requirements.txt

test:
	$(PYTHON) -m unittest discover -s tests -v

enrich-dry:
	$(PYTHON) enricher.py --dry-run --source-label "JW Bible - Genesis 1"

enrich-write:
	$(PYTHON) enricher.py --output dictionary.enriched.json --source-label "JW Bible - Genesis 1"

wordlist:
	$(PYTHON) extract_wordlist.py --dictionary dictionary.json --output wordlist.md

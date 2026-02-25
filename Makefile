PYTHON ?= python3

.PHONY: install test validate-schema enrich-dry enrich-write enrich-stage review-stage wordlist split-datasets join-view inject-historical enrich-historical

install:
	$(PYTHON) -m pip install -r requirements.txt

test:
	$(PYTHON) -m unittest discover -s tests -v

validate-schema:
	$(PYTHON) -m unittest tests.test_dictionary_schema -v

enrich-dry:
	$(PYTHON) enricher.py --mode split --dry-run --source-label "JW Bible - Genesis 1"

enrich-write:
	$(PYTHON) enricher.py --mode split --source-label "JW Bible - Genesis 1"

enrich-stage:
	$(PYTHON) enricher.py --mode split --source-label "JW Bible - Genesis 1"

review-stage:
	$(PYTHON) review_enrichment_diff.py --base dictionary.json --candidate dictionary.enriched.json --output enrichment_diff.md

wordlist:
	$(PYTHON) extract_wordlist.py --dictionary dictionary.json --output wordlist.md

split-datasets:
	$(PYTHON) split_datasets.py --dictionary dictionary.json --lexicon-out lexicon.json --corpus-out corpus.json --attestations-out attestations.json

join-view:
	$(PYTHON) join_view.py --lexicon lexicon.json --corpus corpus.json --attestations attestations.json --output dictionary.joined.json

inject-historical:
	$(PYTHON) inject_historical_entries.py --lexicon lexicon.json --corpus corpus.json --attestations attestations.json --staged-files "staged_casalis_a.json,staged_mabille_a.json"

enrich-historical:
	$(PYTHON) enrich_historical.py

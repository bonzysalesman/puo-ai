PYTHON ?= python3

.PHONY: install test validate-schema validate-all normalize-lexicon prune-backups ci enrich-dry enrich-write enrich-stage review-stage wordlist split-datasets join-view inject-historical enrich-historical feynman-process feynman-explain whatsapp-status

install:
	$(PYTHON) -m pip install -r requirements.txt

test:
	$(PYTHON) -m unittest discover -s tests -t . -v

validate-schema:
	$(PYTHON) -m unittest tests.test_dictionary_schema -v

validate-all:
	$(PYTHON) -m unittest tests.test_dictionary_schema tests.test_split_datasets tests.test_split_native_pipeline -v
	@echo "Checking for lexicon normalization..."
	@grep -q "usage_example" data/lexicon.json && (echo "Error: lexicon.json contains usage_example fields. Run 'make normalize-lexicon'." && exit 1) || echo "Lexicon is normalized."

normalize-lexicon:
	$(PYTHON) pipeline/export/normalize_lexicon.py

prune-backups:
	$(PYTHON) pipeline/cleanup_backups.py

ci: validate-all test prune-backups

enrich-dry:
	$(PYTHON) pipeline/enrichment/enricher.py --mode split --dry-run --source-label "JW Bible - Genesis 1"

enrich-write:
	$(PYTHON) pipeline/enrichment/enricher.py --mode split --source-label "JW Bible - Genesis 1"

enrich-stage:
	$(PYTHON) pipeline/enrichment/enricher.py --mode split --source-label "JW Bible - Genesis 1"

review-stage:
	$(PYTHON) pipeline/enrichment/review_enrichment_diff.py --base data/legacy/dictionary.json --candidate data/legacy/dictionary.enriched.json --output reports/enrichment_diff.md

wordlist:
	$(PYTHON) pipeline/export/extract_wordlist.py --dictionary data/lexicon.json --output wordlist.md

split-datasets:
	$(PYTHON) pipeline/export/split_datasets.py --dictionary data/legacy/dictionary.json --lexicon-out data/lexicon.json --corpus-out data/corpus.json --attestations-out data/attestations.json

join-view:
	$(PYTHON) pipeline/export/join_view.py --lexicon data/lexicon.json --corpus data/corpus.json --attestations data/attestations.json --output data/dictionary.joined.json

inject-historical:
	$(PYTHON) pipeline/export/inject_historical_entries.py --lexicon data/lexicon.json --corpus data/corpus.json --attestations data/attestations.json --staged-files "historical/staged/staged_casalis_a.json,historical/staged/staged_mabille_a.json"

enrich-historical:
	$(PYTHON) pipeline/enrichment/enrich_historical.py

# New Feynman Technique targets
feynman-process:
	$(PYTHON) _agents/skills/feynman_document_processor/scripts/feynman_pipeline.py $(FILE) --output reports/feynman_$(shell basename $(FILE) .pdf).md

feynman-explain:
	$(PYTHON) _agents/skills/feynman_document_processor/scripts/feynman_pipeline.py --concept "$(CONCEPT)" --output reports/concept_$(CONCEPT).md

feynman-weekly-review:
	@echo "🧠 Running weekly Feynman review..."
	$(PYTHON) _agents/skills/feynman_document_processor/scripts/feynman_pipeline.py data/lexicon.json --output reports/weekly_lexicon_review.md
	@echo "📱 Sending WhatsApp notification..."
	$(PYTHON) _agents/skills/whatsapp_integration/whatsapp_notifier.py --status weekly-review

# WhatsApp integration targets  
whatsapp-status:
	$(PYTHON) _agents/skills/whatsapp_integration/whatsapp_notifier.py --command status

whatsapp-notify:
	$(PYTHON) _agents/skills/whatsapp_integration/whatsapp_notifier.py --message "$(MESSAGE)" --to "$(TO)"

# Combined workflow targets
process-and-notify:
	make feynman-process FILE=$(FILE)
	make whatsapp-notify MESSAGE="✅ Processed $(FILE) using Feynman technique. Check reports/ for results." TO=$(PHONE)

inject-and-notify:
	make inject-historical
	make whatsapp-notify MESSAGE="💉 Injected historical entries. Lexicon updated." TO=$(PHONE)

# Scheduled automation (add to crontab)
daily-status:
	@echo "📊 Daily status check..."
	make validate-all
	make whatsapp-status

weekly-review:
	@echo "📝 Weekly review process..."
	make feynman-weekly-review
	make prune-backups
# Database & Seeding (Phase 1-3)
init-db:
	python3 pipeline/init/pems_init_db.py --output data/pems_core.db
	python3 pipeline/init/seed_orthography.py
	python3 pipeline/init/seed_exceptions.py
	python3 pipeline/init/seed_adjectives.py
	python3 pipeline/init/seed_morphology.py
	python3 pipeline/init/seed_noun_lexicon.py

# Quality Assurance
test:
	PYTHONPATH=. python3 -m unittest discover tests

# Phase 1: Smoke test for the Warden (Orthography Firewall)
warden-check:
	@echo "Verifying Warden: 'tjhuna ya me oena'..."
	@PYTHONPATH=. python3 pipeline/warden/normalize_orthography.py --text "tjhuna ya me oena" | grep "chuna ea me oena"

# Phase 2: Agreement Engine smoke tests
agreement-check:
	@echo "Verifying Agreement Engine..."
	@PYTHONPATH=. python3 -m unittest tests.test_agreement -v | grep -E "(possessive|adjective|agreement)" | head -5

# Phase 3: Morphological Architect tests
architect-check:
	@echo "Verifying Morphological Architect..."
	@PYTHONPATH=. python3 -m unittest tests.test_architect tests.test_mutation_zones -v | tail -15

# Red Dog Test: Complete Phase 3 integration
red-dog-test:
	@echo "🐕 Running Red Dog Test: Ntja o fubelu -> Ntja e nkhubelu"
	@PYTHONPATH=. python3 -m unittest tests.test_mutation_zones.TestMutationZones.test_red_dog_mutation_fubelu_to_khubelu -v

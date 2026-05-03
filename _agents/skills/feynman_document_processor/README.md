# Feynman Document Processor

A lightweight implementation of the Feynman Technique for document processing, inspired by nanoclaw's modular architecture but designed to work with existing BMAD infrastructure.

## Features Adopted from Nanoclaw (Without Installation)

### ✅ Skills-Based Architecture
- Modular capabilities that can be added/removed
- Clean separation of concerns
- Reusable components across different workflows

### ✅ Multi-Channel Output Pattern  
- File system (markdown, JSON)
- WhatsApp Business API integration
- Email notifications (via existing tools)
- Webhook support for Slack/Discord

### ✅ Scheduled Task Pattern
- Cron integration via Makefile targets
- Automated weekly reviews
- Status monitoring and notifications

### ✅ Container-Inspired Isolation
- Each processing step is self-contained
- Clear input/output contracts
- Error isolation and recovery

## What We Excluded from Nanoclaw

- ❌ Full Docker container system (too heavy)
- ❌ Complex multi-agent orchestration (we have BMAD)
- ❌ Node.js dependency (Python-first approach)
- ❌ SQLite session management (file-based is simpler)
- ❌ Channel adapter infrastructure (direct API calls)

## Integration Points

### With Existing PUO-AI Pipeline
```bash
# Process historical PDFs with Feynman clarity
make feynman-process FILE=sources/pdfs/mabille.pdf

# Explain concepts from lexicon
make feynman-explain CONCEPT="morphological derivation"

# Weekly automated review
make feynman-weekly-review
```

### With BMAD Agents
- **Analyst (Mary)**: Concept extraction and domain research
- **Storyteller (Sophia)**: Analogies and narrative explanations  
- **QA Engineer (Quinn)**: Gap analysis and quality assurance
- **Tech Writer (Paige)**: Final documentation polish

### With WhatsApp Integration
```bash
# Send processing notifications
make whatsapp-notify MESSAGE="Document processed" TO="+1234567890"

# Get pipeline status via WhatsApp
make whatsapp-status

# Combined workflows
make process-and-notify FILE=document.pdf PHONE="+1234567890"
```

## Usage Examples

### 1. Process a New Dictionary PDF
```bash
# Automatic via Kiro hook when PDF added to sources/pdfs/
# Or manual:
make feynman-process FILE=sources/pdfs/new_dictionary.pdf
```

### 2. Explain a Complex Concept
```bash
# Generate Feynman explanation for linguistic concept
python3 _agents/skills/feynman_document_processor/scripts/feynman_pipeline.py \
  --concept "Bantu noun class system" \
  --output reports/noun_classes_explained.md
```

### 3. WhatsApp Command Interface
```
Send to WhatsApp: "process mabille.pdf"
Receive: "🚀 Starting Feynman processing for mabille.pdf..."
Later: "✅ Processing complete. Generated 23 clear explanations."
```

### 4. Scheduled Automation
```bash
# Add to crontab for weekly reviews
0 9 * * 1 cd /path/to/puo-ai && make feynman-weekly-review
```

## File Structure

```
_agents/skills/feynman_document_processor/
├── SKILL.md                    # Skill documentation
├── README.md                   # This file
├── scripts/
│   ├── feynman_pipeline.py     # Main processing pipeline
│   └── concept_explainer.py    # Standalone concept explanations
└── templates/
    ├── explanation.md          # Markdown templates
    └── concept_card.md         # Concept card format
```

## Benefits Over Full Nanoclaw Installation

✅ **Lightweight**: No Docker, Node.js, or complex dependencies
✅ **Integrated**: Works with existing BMAD and Python pipeline  
✅ **Focused**: Only the features we need for document workflows
✅ **Maintainable**: Simple, readable Python code
✅ **Extensible**: Easy to add new capabilities as needed
✅ **Familiar**: Uses existing tools and patterns

## Future Enhancements

- [ ] Visual concept map generation (Mermaid diagrams)
- [ ] Multi-language explanation support
- [ ] Integration with more messaging platforms
- [ ] Advanced gap analysis using ML models
- [ ] Collaborative explanation editing via web interface
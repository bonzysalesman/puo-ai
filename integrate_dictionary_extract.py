#!/usr/bin/env python3
"""
Integrate English-Sesotho dictionary extract into PUO-AI datasets
Transforms dictionary format to match existing lexicon schema
Uses Feynman technique principles for clear, step-by-step processing
"""

import json
import hashlib
import re
from datetime import datetime
from pathlib import Path

def stable_hash(parts, prefix, length=16):
    """Generate consistent hash IDs"""
    joined = "|".join(str(p) for p in parts)
    digest = hashlib.sha1(joined.encode("utf-8")).hexdigest()[:length]
    return f"{prefix}{digest}"

def parse_sesotho_translations(sesotho_text):
    """
    Parse complex Sesotho translation strings
    
    Simple explanation: Break apart the Sesotho translations that have multiple options
    """
    # Handle parenthetical explanations like "(to wonder at) ho makala ke"
    parts = []
    
    # Split on semicolons first (major semantic divisions)
    major_parts = sesotho_text.split(';')
    
    for part in major_parts:
        part = part.strip()
        if not part:
            continue
            
        # Handle parenthetical context like "(to wonder at) ho makala ke"
        if '(' in part and ')' in part:
            # Extract context and translation
            context_match = re.match(r'\(([^)]+)\)\s*(.+)', part)
            if context_match:
                context = context_match.group(1)
                translation = context_match.group(2).strip()
                parts.append({
                    'context': context,
                    'translation': translation,
                    'variants': [t.strip() for t in translation.split(',') if t.strip()]
                })
            else:
                # No clear parenthetical, treat as simple translation
                variants = [t.strip() for t in part.split(',') if t.strip()]
                parts.append({
                    'context': None,
                    'translation': part,
                    'variants': variants
                })
        else:
            # Simple translation without context
            variants = [t.strip() for t in part.split(',') if t.strip()]
            parts.append({
                'context': None,
                'translation': part,
                'variants': variants
            })
    
    return parts

def transform_dictionary_entry(entry):
    """
    Transform dictionary entry to lexicon schema
    
    Simple explanation: Convert the dictionary recipe format to match our cookbook format
    """
    # Generate entry ID based on English headword
    entry_id = f"dict_{entry['headword_english'].lower().replace(' ', '_')}"
    
    # Parse Sesotho translations
    sesotho_parts = parse_sesotho_translations(entry['sesotho'])
    
    # Create base entry structure
    transformed_entry = {
        "entry_id": entry_id,
        "headword_english": entry['headword_english'],
        "pos": [entry['pos']] if entry['pos'] else [],
        "headword_sesotho": [],
        "syllables": [],
        "morphology": {
            "source": "English-Sesotho Dictionary Extract",
            "translation_variants": len(sesotho_parts)
        },
        "senses": [],
        "thesaurus": {
            "synonyms_en": [],
            "antonyms_en": [],
            "synonyms_st": [],
            "antonyms_st": []
        }
    }
    
    # Process each Sesotho translation as a separate sense
    for i, part in enumerate(sesotho_parts):
        sense_id = f"{entry_id}.sense_{i+1}"
        
        # Create definition from context or use generic
        if part['context']:
            definition = f"{entry['headword_english']} ({part['context']})"
        else:
            definition = entry['headword_english']
        
        # Extract primary Sesotho term (first variant)
        primary_sesotho = part['variants'][0] if part['variants'] else part['translation']
        
        # Clean up Sesotho term (remove "ho " prefix for verbs)
        clean_sesotho = primary_sesotho.replace('ho ', '').strip()
        
        sense = {
            "sense_id": sense_id,
            "definition_en": definition,
            "sesotho_term": [clean_sesotho],
            "translation_context": part['context'],
            "variants": part['variants']
        }
        
        transformed_entry["senses"].append(sense)
        
        # Add to headword_sesotho if not already present
        if clean_sesotho not in [hs.get('orthographic', '') for hs in transformed_entry["headword_sesotho"]]:
            transformed_entry["headword_sesotho"].append({
                "orthographic": clean_sesotho,
                "tone_marked": clean_sesotho  # Would need tone marking system
            })
    
    return transformed_entry

def create_usage_examples(dictionary_entries):
    """
    Generate usage examples from dictionary context
    
    Simple explanation: Create example sentences showing how to use these words
    """
    corpus_entries = []
    
    for entry in dictionary_entries:
        entry_id = f"dict_{entry['headword_english'].lower().replace(' ', '_')}"
        
        # Create generic usage example
        english_example = f"This is an example of {entry['headword_english'].lower()}."
        
        # Use first Sesotho translation for example
        sesotho_parts = parse_sesotho_translations(entry['sesotho'])
        if sesotho_parts and sesotho_parts[0]['variants']:
            primary_sesotho = sesotho_parts[0]['variants'][0].replace('ho ', '').strip()
            sesotho_example = f"Sena ke mohlala oa {primary_sesotho}."
        else:
            sesotho_example = "Sena ke mohlala."
        
        corpus_id = stable_hash([
            sesotho_example,
            english_example
        ], "corpus_")
        
        corpus_entry = {
            "corpus_id": corpus_id,
            "source": "Dictionary Extract Integration",
            "ref": entry_id,
            "sesotho_text": sesotho_example,
            "english_text": english_example
        }
        corpus_entries.append(corpus_entry)
    
    return corpus_entries

def create_attestations_from_dictionary(transformed_entries, corpus_entries):
    """
    Create attestation links for dictionary entries
    
    Simple explanation: Draw lines connecting dictionary words to their example sentences
    """
    attestations = []
    
    # Create mapping of entry IDs to corpus entries
    entry_to_corpus = {}
    for corpus_entry in corpus_entries:
        entry_to_corpus[corpus_entry["ref"]] = corpus_entry["corpus_id"]
    
    for entry in transformed_entries:
        corpus_id = entry_to_corpus.get(entry["entry_id"])
        if not corpus_id:
            continue
            
        for sense in entry["senses"]:
            attestation_id = stable_hash([sense["sense_id"], corpus_id], "att_")
            
            # Use primary Sesotho term for matching
            match_terms = sense["sesotho_term"]
            
            attestation = {
                "attestation_id": attestation_id,
                "sense_id": sense["sense_id"],
                "corpus_id": corpus_id,
                "source_raw": f"Dictionary Integration ({entry['entry_id']})",
                "match_terms": match_terms,
                "score": 900.0,  # High confidence for dictionary entries
                "method": "dictionary_integration_v1"
            }
            attestations.append(attestation)
    
    return attestations

def analyze_overlap_with_existing(transformed_entries, existing_lexicon):
    """
    Analyze overlap between dictionary extract and existing lexicon
    
    Simple explanation: Check which words we already have vs which are new
    """
    existing_english = set()
    existing_sesotho = set()
    
    # Extract existing headwords
    for entry in existing_lexicon:
        if entry.get("headword_english"):
            existing_english.add(entry["headword_english"].lower())
        
        for hs in entry.get("headword_sesotho", []):
            if hs.get("orthographic"):
                existing_sesotho.add(hs["orthographic"].lower())
    
    # Analyze new entries
    overlap_stats = {
        "total_dictionary_entries": len(transformed_entries),
        "english_overlaps": 0,
        "sesotho_overlaps": 0,
        "completely_new": 0,
        "overlapping_entries": [],
        "new_entries": []
    }
    
    for entry in transformed_entries:
        english_exists = entry["headword_english"].lower() in existing_english
        
        sesotho_exists = False
        for hs in entry["headword_sesotho"]:
            if hs["orthographic"].lower() in existing_sesotho:
                sesotho_exists = True
                break
        
        if english_exists:
            overlap_stats["english_overlaps"] += 1
        if sesotho_exists:
            overlap_stats["sesotho_overlaps"] += 1
            
        if english_exists or sesotho_exists:
            overlap_stats["overlapping_entries"].append({
                "entry_id": entry["entry_id"],
                "english": entry["headword_english"],
                "english_exists": english_exists,
                "sesotho_exists": sesotho_exists
            })
        else:
            overlap_stats["completely_new"] += 1
            overlap_stats["new_entries"].append(entry["entry_id"])
    
    return overlap_stats

def integrate_dictionary_extract():
    """
    Main integration function for dictionary extract
    
    Simple explanation: Add the dictionary words to all our word collections
    """
    
    # The dictionary extract data
    dictionary_data = [
        {"headword_english": "Adjunction", "pos": "n.", "sesotho": "kekeletso"},
        {"headword_english": "Adjure", "pos": "v.", "sesotho": "ho hlaponya, antsa"},
        {"headword_english": "Administer", "pos": "v.", "sesotho": "ho lisa, tsamaisa"},
        {"headword_english": "Administration", "pos": "n.", "sesotho": "puso, tiso"},
        {"headword_english": "Admire", "pos": "v.", "sesotho": "(to wonder at) ho makala ke, bōha, tsota, babatsa; (to feel respect) ho hlompha"},
        {"headword_english": "Admit", "pos": "v.", "sesotho": "(to permit to enter) ho amohela, kenya; (to receive as true) ho lumela, kholoa ke"},
        {"headword_english": "Admonish", "pos": "v.", "sesotho": "ho laea"},
        {"headword_english": "Adolescent", "pos": "n.", "sesotho": "mohlankana"},
        {"headword_english": "Adopt", "pos": "v.", "sesotho": "(to adopt a child) ho thola ngoana"},
        {"headword_english": "Adoration", "pos": "n.", "sesotho": "ho khumamela, ho sebeletsa Molimo"},
        {"headword_english": "Adorn", "pos": "v.", "sesotho": "ho khabisa, lilopha, hlophisa"},
        {"headword_english": "Adulterate", "pos": "v.", "sesotho": "ho tsoberenya, senya bolisa"},
        {"headword_english": "Adultery", "pos": "n.", "sesotho": "bofebe"},
        {"headword_english": "Advance", "pos": "v.", "sesotho": "ho tsoela pele"},
        {"headword_english": "Advantage", "pos": "n.", "sesotho": "molemo"},
        {"headword_english": "Adventure", "pos": "n.", "sesotho": "ntho e tsohang e hlahela motho, tsietsi, ngope-a-sesoha"},
        {"headword_english": "Adversary", "pos": "n.", "sesotho": "sera, mohanyetsi"},
        {"headword_english": "Adversity", "pos": "n.", "sesotho": "bomalibe, bosoto"},
        {"headword_english": "Advice", "pos": "n.", "sesotho": "keletso, temoso"},
        {"headword_english": "Advise", "pos": "v.", "sesotho": "ho lemosa, elotsa"},
        {"headword_english": "Advocate", "pos": "v.", "sesotho": "ho bulella, emela"},
        {"headword_english": "Afar", "pos": "adv.", "sesotho": "hole, moniamo"},
        {"headword_english": "Affability", "pos": "n.", "sesotho": "mosa, molemo"},
        {"headword_english": "Affair", "pos": "n.", "sesotho": "taba, mosebetsi"},
        {"headword_english": "Affect", "pos": "v.", "sesotho": "(to move or touch) ho ama pelo, sisimosa; (to be moved) ho perama, sisa pelo; (to make a show) ho iketsisa"},
        {"headword_english": "Affection", "pos": "n.", "sesotho": "lerato"},
        {"headword_english": "Affirm", "pos": "v.", "sesotho": "ho tiisa, omela"},
        {"headword_english": "Affirmation", "pos": "n.", "sesotho": "tiiso, komelo"},
        {"headword_english": "Afflict", "pos": "v.", "sesotho": "ho hlokofatsa; (to be afflicted) ho hlomoha, siaba"},
        {"headword_english": "Affliction", "pos": "n.", "sesotho": "masuabi, mahlomola"},
        {"headword_english": "Affright", "pos": "v.", "sesotho": "ho tsosa, tšabisa"},
        {"headword_english": "Affront", "pos": "v.", "sesotho": "ho fahla"},
        {"headword_english": "Afoot", "pos": "adv.", "sesotho": "ka maoto"},
        {"headword_english": "Aforetime", "pos": "adv.", "sesotho": "pele, khale"},
        {"headword_english": "Afraid", "pos": "adj.", "sesotho": "e tsohileng, e tsohang; (to be afraid) ho tšaba, tsoha, qaea, feha mahlo"},
        {"headword_english": "Afresh", "pos": "adv.", "sesotho": "hape, bocha"},
        {"headword_english": "After", "pos": "adv./prep.", "sesotho": "morao, ka morao, ka mora"},
        {"headword_english": "Afternoon", "pos": "n.", "sesotho": "motšehare oa mantsibōeng"},
        {"headword_english": "Afterwards", "pos": "adv.", "sesotho": "kamorao"},
        {"headword_english": "Against", "pos": "prep.", "sesotho": "(opposition) ho loantsa, ho hanyetsa; (support) ho itsetleha ka"},
        {"headword_english": "Age", "pos": "n.", "sesotho": "(time of life) lilemo; (period) motsotso, ngoaha"},
        {"headword_english": "Agent", "pos": "n.", "sesotho": "moemeli, ajiante"},
        {"headword_english": "Agility", "pos": "n.", "sesotho": "bobebe, lebelo"},
        {"headword_english": "Agitate", "pos": "v.", "sesotho": "(to stir) ho tsukutla, fulua, tsoka, tsokotsa; (to disturb) ho ferekanya, tsosa; (mentally) ho ferekana, ho erehana"},
        {"headword_english": "Ago", "pos": "adv.", "sesotho": "khale, pele"},
        {"headword_english": "Agony", "pos": "n.", "sesotho": "mahlomola a letsoalo, bohloko bo boholo"},
        {"headword_english": "Agree", "pos": "v.", "sesotho": "ho lumellana, ho utloana"},
        {"headword_english": "Agreeable", "pos": "adj.", "sesotho": "(pleasing) e khahlelang, e khahlisoang; (to be agreeable) ho khahliha"},
        {"headword_english": "Agreement", "pos": "n.", "sesotho": "tumellano"},
        {"headword_english": "Agriculture", "pos": "n.", "sesotho": "bolemi, temo"},
        {"headword_english": "Ahead", "pos": "adv.", "sesotho": "ka pele; (to go ahead) ho tsoela pele"}
    ]
    
    print("🚀 Starting integration of English-Sesotho dictionary extract...")
    print(f"📊 Processing {len(dictionary_data)} dictionary entries...")
    
    # Step 1: Load existing datasets
    print("📖 Step 1: Loading existing datasets...")
    with open('data/lexicon.json', 'r', encoding='utf-8') as f:
        lexicon = json.load(f)
    
    with open('data/corpus.json', 'r', encoding='utf-8') as f:
        corpus = json.load(f)
    
    with open('data/attestations.json', 'r', encoding='utf-8') as f:
        attestations = json.load(f)
    
    print(f"   Current lexicon entries: {len(lexicon)}")
    print(f"   Current corpus entries: {len(corpus)}")
    print(f"   Current attestations: {len(attestations)}")
    
    # Step 2: Transform dictionary entries
    print("🔄 Step 2: Transforming dictionary entries to lexicon schema...")
    transformed_entries = []
    for entry in dictionary_data:
        try:
            transformed = transform_dictionary_entry(entry)
            transformed_entries.append(transformed)
        except Exception as e:
            print(f"   ⚠️  Error transforming {entry['headword_english']}: {e}")
    
    print(f"   Successfully transformed: {len(transformed_entries)} entries")
    
    # Step 3: Analyze overlap with existing lexicon
    print("🔍 Step 3: Analyzing overlap with existing lexicon...")
    overlap_stats = analyze_overlap_with_existing(transformed_entries, lexicon)
    
    print(f"   📊 Overlap Analysis:")
    print(f"      Total dictionary entries: {overlap_stats['total_dictionary_entries']}")
    print(f"      English headword overlaps: {overlap_stats['english_overlaps']}")
    print(f"      Sesotho term overlaps: {overlap_stats['sesotho_overlaps']}")
    print(f"      Completely new entries: {overlap_stats['completely_new']}")
    
    # Step 4: Create corpus entries
    print("📝 Step 4: Creating corpus entries...")
    new_corpus_entries = create_usage_examples(dictionary_data)
    
    # Step 5: Create attestations
    print("🔗 Step 5: Creating attestation links...")
    new_attestations = create_attestations_from_dictionary(transformed_entries, new_corpus_entries)
    
    # Step 6: Filter for truly new entries (avoid duplicates)
    print("🎯 Step 6: Filtering for new entries...")
    existing_entry_ids = {entry.get("entry_id") for entry in lexicon}
    existing_corpus_ids = {entry.get("corpus_id") for entry in corpus}
    existing_attestation_ids = {entry.get("attestation_id") for entry in attestations}
    
    new_lexicon_entries = [e for e in transformed_entries if e["entry_id"] not in existing_entry_ids]
    new_corpus_filtered = [e for e in new_corpus_entries if e["corpus_id"] not in existing_corpus_ids]
    new_attestations_filtered = [e for e in new_attestations if e["attestation_id"] not in existing_attestation_ids]
    
    print(f"   New lexicon entries to add: {len(new_lexicon_entries)}")
    print(f"   New corpus entries to add: {len(new_corpus_filtered)}")
    print(f"   New attestations to add: {len(new_attestations_filtered)}")
    
    # Step 7: Show sample transformations
    print("\n📋 Step 7: Sample transformations:")
    for i, entry in enumerate(transformed_entries[:3]):
        print(f"   {i+1}. {entry['headword_english']} → {len(entry['senses'])} senses")
        for sense in entry['senses']:
            context = f" ({sense['translation_context']})" if sense['translation_context'] else ""
            print(f"      - {sense['sesotho_term'][0]}{context}")
    
    # Step 8: Integration decision
    print(f"\n🤔 Step 8: Integration recommendation:")
    if len(new_lexicon_entries) > 0:
        print(f"   ✅ Recommend integrating {len(new_lexicon_entries)} new entries")
        print(f"   📈 This would increase lexicon size by {len(new_lexicon_entries)/len(lexicon)*100:.1f}%")
    else:
        print(f"   ℹ️  All dictionary entries already exist in lexicon")
        print(f"   💡 Consider enhancing existing entries with translation variants")
    
    # Step 9: Save analysis report
    print("📄 Step 9: Saving analysis report...")
    report = {
        "timestamp": datetime.now().isoformat(),
        "dictionary_entries_processed": len(dictionary_data),
        "transformed_entries": len(transformed_entries),
        "overlap_analysis": overlap_stats,
        "integration_candidates": {
            "new_lexicon_entries": len(new_lexicon_entries),
            "new_corpus_entries": len(new_corpus_filtered),
            "new_attestations": len(new_attestations_filtered)
        },
        "sample_transformations": [
            {
                "english": entry["headword_english"],
                "senses": len(entry["senses"]),
                "sesotho_terms": [sense["sesotho_term"][0] for sense in entry["senses"]]
            }
            for entry in transformed_entries[:5]
        ]
    }
    
    with open('reports/dictionary_integration_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("✅ Dictionary extract analysis completed!")
    print("📊 See reports/dictionary_integration_analysis.json for detailed results")
    
    return overlap_stats, new_lexicon_entries, new_corpus_filtered, new_attestations_filtered

if __name__ == "__main__":
    integrate_dictionary_extract()
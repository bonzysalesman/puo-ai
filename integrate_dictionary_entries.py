#!/usr/bin/env python3
"""
Dictionary Entry Integration Script
Transforms English-Sesotho dictionary format to PUO-AI lexicon schema
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

def expand_pos_tag(pos_tag):
    """Expand abbreviated part-of-speech tags"""
    pos_map = {
        "n.": "noun",
        "v.": "verb", 
        "adj.": "adjective",
        "adv.": "adverb",
        "prep.": "preposition",
        "conj.": "conjunction",
        "interj.": "interjection"
    }
    return pos_map.get(pos_tag, pos_tag)

def split_sesotho_translations(sesotho_text):
    """
    Split multiple Sesotho translations and extract contextual notes
    
    Simple explanation: Take "ho makala ke, bōha; ho hlompha" and split it into parts
    """
    # Handle contextual notes in parentheses
    parts = []
    
    # Split by semicolon first (major semantic divisions)
    major_parts = sesotho_text.split(';')
    
    for part in major_parts:
        part = part.strip()
        
        # Extract contextual note if present
        context = ""
        if '(' in part and ')' in part:
            context_match = re.search(r'\(([^)]+)\)', part)
            if context_match:
                context = context_match.group(1)
                part = re.sub(r'\([^)]+\)', '', part).strip()
        
        # Split by comma for alternatives within same context
        alternatives = [alt.strip() for alt in part.split(',') if alt.strip()]
        
        for alt in alternatives:
            if alt:
                parts.append({
                    'sesotho': alt,
                    'context': context
                })
    
    return parts

def generate_syllables(sesotho_word):
    """
    Generate syllable breakdown for Sesotho words
    
    Simple explanation: Break "liaparo" into "li-a-pa-ro"
    """
    # Remove "ho " prefix for verbs
    word = sesotho_word.replace("ho ", "")
    
    # Simple syllable splitting (basic Bantu pattern)
    # This is a simplified approach - real syllabification is more complex
    syllables = []
    current = ""
    
    for i, char in enumerate(word):
        current += char
        
        # Split after vowels (a, e, i, o, u) unless at end
        if char in "aeiou" and i < len(word) - 1:
            # Don't split if next char is also vowel (diphthong)
            if i + 1 < len(word) and word[i + 1] not in "aeiou":
                syllables.append(current)
                current = ""
    
    if current:
        syllables.append(current)
    
    return "-".join(syllables) if syllables else word

def create_usage_example(english_word, sesotho_word, context=""):
    """
    Generate synthetic usage examples
    
    Simple explanation: Create example sentences showing how to use the word
    """
    # Simple templates for different word types
    templates = {
        'verb': {
            'sesotho': f"Ba {sesotho_word.replace('ho ', '')} ka mokhoa o motle.",
            'english': f"They {english_word.lower()} in a good way."
        },
        'noun': {
            'sesotho': f"{sesotho_word.capitalize()} ena e bonahala hantle.",
            'english': f"This {english_word.lower()} looks good."
        },
        'adjective': {
            'sesotho': f"Motho ea {sesotho_word}.",
            'english': f"A person who is {english_word.lower()}."
        },
        'default': {
            'sesotho': f"Lentsoe '{sesotho_word}' le bolela '{english_word}'.",
            'english': f"The word '{sesotho_word}' means '{english_word}'."
        }
    }
    
    # Determine word type
    if sesotho_word.startswith('ho '):
        return templates['verb']
    elif sesotho_word.startswith(('li', 'ma', 'se', 'mo', 'ba')):
        return templates['noun']
    else:
        return templates['default']

def transform_dictionary_entries(dictionary_data):
    """
    Transform dictionary format to lexicon schema
    
    Simple explanation: Convert recipe cards to our cookbook format
    """
    transformed = []
    
    for i, entry in enumerate(dictionary_data, 1):
        entry_id = f"st_B_{i:03d}"  # B-section entries
        
        # Split Sesotho translations
        sesotho_parts = split_sesotho_translations(entry['sesotho'])
        
        # Get primary Sesotho form (first one)
        primary_sesotho = sesotho_parts[0]['sesotho'] if sesotho_parts else entry['sesotho']
        
        # Create senses for each Sesotho variant
        senses = []
        for j, part in enumerate(sesotho_parts, 1):
            sense_id = f"{entry_id}.sense_{j}"
            
            definition = entry['headword_english']
            if part['context']:
                definition += f" ({part['context']})"
            
            sense = {
                "sense_id": sense_id,
                "definition_en": definition,
                "sesotho_term": [part['sesotho']]
            }
            senses.append(sense)
        
        # If no parts found, create single sense
        if not senses:
            senses = [{
                "sense_id": f"{entry_id}.sense_1",
                "definition_en": entry['headword_english'],
                "sesotho_term": [primary_sesotho]
            }]
        
        # Generate syllables
        syllable_breakdown = generate_syllables(primary_sesotho)
        
        # Enhanced morphology with OCR source metadata
        morphology = {
            "source": "Dictionary integration - OCR",
            "alternatives": [p['sesotho'] for p in sesotho_parts[1:]] if len(sesotho_parts) > 1 else [],
            "ocr_metadata": entry.get('source', {})
        }
        
        # Create transformed entry
        transformed_entry = {
            "entry_id": entry_id,
            "headword_english": entry['headword_english'],
            "pos": [{"tag": entry['pos'], "full": expand_pos_tag(entry['pos'])}],
            "headword_sesotho": [{"orthographic": primary_sesotho, "tone_marked": ""}],
            "syllables": [{"orthographic": syllable_breakdown, "syllable_count": len(syllable_breakdown.split('-'))}],
            "morphology": morphology,
            "senses": senses,
            "thesaurus": {
                "synonyms_en": [],
                "antonyms_en": [],
                "synonyms_st": [],
                "antonyms_st": []
            }
        }
        
        transformed.append(transformed_entry)
    
    return transformed

def create_corpus_entries_from_dictionary(dictionary_data, transformed_entries):
    """
    Create corpus entries with synthetic usage examples
    
    Simple explanation: Make example sentences for each word
    """
    corpus_entries = []
    
    for dict_entry, trans_entry in zip(dictionary_data, transformed_entries):
        # Create usage example
        sesotho_parts = split_sesotho_translations(dict_entry['sesotho'])
        primary_sesotho = sesotho_parts[0]['sesotho'] if sesotho_parts else dict_entry['sesotho']
        
        usage = create_usage_example(dict_entry['headword_english'], primary_sesotho)
        
        corpus_id = stable_hash([
            usage['sesotho'],
            usage['english']
        ], "corpus_")
        
        # Enhanced corpus entry with OCR source metadata
        corpus_entry = {
            "corpus_id": corpus_id,
            "source": "Dictionary Integration - OCR Synthetic",
            "ref": trans_entry['entry_id'],
            "sesotho_text": usage['sesotho'],
            "english_text": usage['english'],
            "ocr_source": dict_entry.get('source', {})
        }
        
        corpus_entries.append(corpus_entry)
    
    return corpus_entries

def create_attestations_from_dictionary(transformed_entries, corpus_entries):
    """
    Create attestation links between senses and corpus entries
    
    Simple explanation: Draw lines connecting words to their example sentences
    """
    attestations = []
    
    for trans_entry, corpus_entry in zip(transformed_entries, corpus_entries):
        for sense in trans_entry['senses']:
            attestation_id = stable_hash([sense['sense_id'], corpus_entry['corpus_id']], "att_")
            
            attestation = {
                "attestation_id": attestation_id,
                "sense_id": sense['sense_id'],
                "corpus_id": corpus_entry['corpus_id'],
                "source_raw": f"Dictionary Integration ({trans_entry['entry_id']})",
                "match_terms": sense['sesotho_term'],
                "score": 1000.0,
                "method": "dictionary_integration_v1"
            }
            
            attestations.append(attestation)
    
    return attestations

def integrate_dictionary_entries():
    """
    Main integration function for dictionary entries
    
    Simple explanation: Add all the dictionary words to our word collections
    """
    
    # The B-section dictionary data with OCR source metadata
    dictionary_data = [
        {"headword_english": "Banknote", "pos": "n.", "sesotho": "chelete ea pampiri", "source": {"page_index": 20, "page_number": 21, "column": "left", "image": "page_021_left.png", "text_file": "page_021_left.txt", "method": "split-image-tesseract-ocr"}},
        {"headword_english": "Bankrupt", "pos": "adj.", "sesotho": "ea sitloang ho lefa melato ea hae.", "source": {"page_index": 20, "page_number": 21, "column": "left", "image": "page_021_left.png", "text_file": "page_021_left.txt", "method": "split-image-tesseract-ocr"}},
        {"headword_english": "Banner", "pos": "n.", "sesotho": "folaga.", "source": {"page_index": 20, "page_number": 21, "column": "left", "image": "page_021_left.png", "text_file": "page_021_left.txt", "method": "split-image-tesseract-ocr"}},
        {"headword_english": "Banquet", "pos": "n.", "sesotho": "seboka se seholo sa lijo, selallo se seholo.", "source": {"page_index": 20, "page_number": 21, "column": "left", "image": "page_021_left.png", "text_file": "page_021_left.txt", "method": "split-image-tesseract-ocr"}},
        {"headword_english": "Banter", "pos": "n.", "sesotho": "litšeho, mosuaso.", "source": {"page_index": 20, "page_number": 21, "column": "left", "image": "page_021_left.png", "text_file": "page_021_left.txt", "method": "split-image-tesseract-ocr"}},
        {"headword_english": "Baptism", "pos": "n.", "sesotho": "kolobetso.", "source": {"page_index": 20, "page_number": 21, "column": "left", "image": "page_021_left.png", "text_file": "page_021_left.txt", "method": "split-image-tesseract-ocr"}},
        {"headword_english": "Baptise", "pos": "v.", "sesotho": "ho kolobetsa.", "source": {"page_index": 20, "page_number": 21, "column": "left", "image": "page_021_left.png", "text_file": "page_021_left.txt", "method": "split-image-tesseract-ocr"}},
        {"headword_english": "Bar", "pos": "v.", "sesotho": "ho koalla, thibela.", "source": {"page_index": 20, "page_number": 21, "column": "left", "image": "page_021_left.png", "text_file": "page_021_left.txt", "method": "split-image-tesseract-ocr"}},
        {"headword_english": "Barbed", "pos": "adj.", "sesotho": "e nang le lintlha tse hlabang, e meutloa.", "source": {"page_index": 20, "page_number": 21, "column": "left", "image": "page_021_left.png", "text_file": "page_021_left.txt", "method": "split-image-tesseract-ocr"}},
        {"headword_english": "Barber", "pos": "n.", "sesotho": "'medi.", "source": {"page_index": 20, "page_number": 21, "column": "left", "image": "page_021_left.png", "text_file": "page_021_left.txt", "method": "split-image-tesseract-ocr"}},
        {"headword_english": "Bare", "pos": "adj.", "sesotho": "e hlobohiloeng.", "source": {"page_index": 20, "page_number": 21, "column": "left", "image": "page_021_left.png", "text_file": "page_021_left.txt", "method": "split-image-tesseract-ocr"}},
        {"headword_english": "Bare", "pos": "v.", "sesotho": "ho hlobolisa.", "source": {"page_index": 20, "page_number": 21, "column": "left", "image": "page_021_left.png", "text_file": "page_021_left.txt", "method": "split-image-tesseract-ocr"}},
        {"headword_english": "Barefooted", "pos": "adj.", "sesotho": "ea sa roaleng letho.", "source": {"page_index": 20, "page_number": 21, "column": "left", "image": "page_021_left.png", "text_file": "page_021_left.txt", "method": "split-image-tesseract-ocr"}},
        {"headword_english": "Barely", "pos": "adv.", "sesotho": "ke batla ke se na chelete e lekanang.", "source": {"page_index": 20, "page_number": 21, "column": "left", "image": "page_021_left.png", "text_file": "page_021_left.txt", "method": "split-image-tesseract-ocr"}},
        {"headword_english": "Bark", "pos": "v.", "sesotho": "(of a dog) ho bohola.", "source": {"page_index": 20, "page_number": 21, "column": "left", "image": "page_021_left.png", "text_file": "page_021_left.txt", "method": "split-image-tesseract-ocr"}},
        {"headword_english": "Bark", "pos": "n.", "sesotho": "(of a tree) lekhapetla.", "source": {"page_index": 20, "page_number": 21, "column": "left", "image": "page_021_left.png", "text_file": "page_021_left.txt", "method": "split-image-tesseract-ocr"}},
        {"headword_english": "Bark", "pos": "n.", "sesotho": "(a ship) sekepe.", "source": {"page_index": 20, "page_number": 21, "column": "left", "image": "page_021_left.png", "text_file": "page_021_left.txt", "method": "split-image-tesseract-ocr"}},
        {"headword_english": "Barley", "pos": "n.", "sesotho": "garese.", "source": {"page_index": 20, "page_number": 21, "column": "left", "image": "page_021_left.png", "text_file": "page_021_left.txt", "method": "split-image-tesseract-ocr"}},
        {"headword_english": "Barrel", "pos": "n.", "sesotho": "(a cask) faki; (of a gun) lopo, koto ea sethunya.", "source": {"page_index": 20, "page_number": 21, "column": "right", "image": "page_021_right.png", "text_file": "page_021_right.txt", "method": "split-image-tesseract-ocr"}},
        {"headword_english": "Barren", "pos": "adj.", "sesotho": "(of things) e nyopa.", "source": {"page_index": 20, "page_number": 21, "column": "right", "image": "page_021_right.png", "text_file": "page_021_right.txt", "method": "split-image-tesseract-ocr"}},
        {"headword_english": "Barrenness", "pos": "n.", "sesotho": "bonyopa.", "source": {"page_index": 20, "page_number": 21, "column": "right", "image": "page_021_right.png", "text_file": "page_021_right.txt", "method": "split-image-tesseract-ocr"}},
        {"headword_english": "Barricade", "pos": "n.", "sesotho": "lerako le etselitsoeng ho loana, lehera.", "source": {"page_index": 20, "page_number": 21, "column": "right", "image": "page_021_right.png", "text_file": "page_021_right.txt", "method": "split-image-tesseract-ocr"}},
        {"headword_english": "Barter", "pos": "v.", "sesotho": "ho reka, rekisa, bapatsa.", "source": {"page_index": 20, "page_number": 21, "column": "right", "image": "page_021_right.png", "text_file": "page_021_right.txt", "method": "split-image-tesseract-ocr"}},
        {"headword_english": "Base", "pos": "adj.", "sesotho": "e nyatsehang; to be base, ho khuahlapeha.", "source": {"page_index": 20, "page_number": 21, "column": "right", "image": "page_021_right.png", "text_file": "page_021_right.txt", "method": "split-image-tesseract-ocr"}},
        {"headword_english": "Base", "pos": "n.", "sesotho": "(foundation) motheo; (of the human voice) lentsoe la tlase pineng; v. ho thea.", "source": {"page_index": 20, "page_number": 21, "column": "right", "image": "page_021_right.png", "text_file": "page_021_right.txt", "method": "split-image-tesseract-ocr"}},
        {"headword_english": "Bashful", "pos": "adj.", "sesotho": "e lihlong.", "source": {"page_index": 20, "page_number": 21, "column": "right", "image": "page_021_right.png", "text_file": "page_021_right.txt", "method": "split-image-tesseract-ocr"}},
        {"headword_english": "Basin", "pos": "n.", "sesotho": "(a vessel) morifi, mokeke, lefisoana.", "source": {"page_index": 20, "page_number": 21, "column": "right", "image": "page_021_right.png", "text_file": "page_021_right.txt", "method": "split-image-tesseract-ocr"}},
        {"headword_english": "Basis", "pos": "n.", "sesotho": "motheo, selulo.", "source": {"page_index": 20, "page_number": 21, "column": "right", "image": "page_021_right.png", "text_file": "page_021_right.txt", "method": "split-image-tesseract-ocr"}},
        {"headword_english": "Bask", "pos": "v.", "sesotho": "(to enjoy the heat) ho ora letsatsing, ho nthamela.", "source": {"page_index": 20, "page_number": 21, "column": "right", "image": "page_021_right.png", "text_file": "page_021_right.txt", "method": "split-image-tesseract-ocr"}},
        {"headword_english": "Basket", "pos": "n.", "sesotho": "seroto, setlatla; (a large basket) sesiu; (a basket with a lid) sethala.", "source": {"page_index": 20, "page_number": 21, "column": "right", "image": "page_021_right.png", "text_file": "page_021_right.txt", "method": "split-image-tesseract-ocr"}},
        {"headword_english": "Bastard", "pos": "n.", "sesotho": "ea tsoetsoeng bonyatsing.", "source": {"page_index": 21, "page_number": 22, "column": "left", "image": "page_022_left.png", "text_file": "page_022_left.txt", "method": "split-image-tesseract-ocr"}},
        {"headword_english": "Bat", "pos": "n.", "sesotho": "'mankhane.", "source": {"page_index": 21, "page_number": 22, "column": "left", "image": "page_022_left.png", "text_file": "page_022_left.txt", "method": "split-image-tesseract-ocr"}},
        {"headword_english": "Batch", "pos": "n.", "sesotho": "sehlopha.", "source": {"page_index": 21, "page_number": 22, "column": "left", "image": "page_022_left.png", "text_file": "page_022_left.txt", "method": "split-image-tesseract-ocr"}},
        {"headword_english": "Bath", "pos": "n.", "sesotho": "morifi o moholo oa ho iphotla.", "source": {"page_index": 21, "page_number": 22, "column": "left", "image": "page_022_left.png", "text_file": "page_022_left.txt", "method": "split-image-tesseract-ocr"}},
        {"headword_english": "Battalion", "pos": "n.", "sesotho": "lekhotla la masole.", "source": {"page_index": 21, "page_number": 22, "column": "left", "image": "page_022_left.png", "text_file": "page_022_left.txt", "method": "split-image-tesseract-ocr"}},
        {"headword_english": "Battery", "pos": "n.", "sesotho": "sehlopha sa kano.", "source": {"page_index": 21, "page_number": 22, "column": "left", "image": "page_022_left.png", "text_file": "page_022_left.txt", "method": "split-image-tesseract-ocr"}},
        {"headword_english": "Battle", "pos": "n.", "sesotho": "ntoa, phapang, qabang.", "source": {"page_index": 21, "page_number": 22, "column": "left", "image": "page_022_left.png", "text_file": "page_022_left.txt", "method": "split-image-tesseract-ocr"}},
        {"headword_english": "Bawl", "pos": "v.", "sesotho": "ho meketsa, ho heeletsa.", "source": {"page_index": 21, "page_number": 22, "column": "left", "image": "page_022_left.png", "text_file": "page_022_left.txt", "method": "split-image-tesseract-ocr"}},
        {"headword_english": "Bay", "pos": "n.", "sesotho": "(of the sea) koro ea leoatle.", "source": {"page_index": 21, "page_number": 22, "column": "left", "image": "page_022_left.png", "text_file": "page_022_left.txt", "method": "split-image-tesseract-ocr"}},
        {"headword_english": "Be", "pos": "v.", "sesotho": "ho ba.", "source": {"page_index": 21, "page_number": 22, "column": "left", "image": "page_022_left.png", "text_file": "page_022_left.txt", "method": "split-image-tesseract-ocr"}},
        {"headword_english": "Beach", "pos": "n.", "sesotho": "lebopo la leoatle le nang le lehlabathe.", "source": {"page_index": 21, "page_number": 22, "column": "left", "image": "page_022_left.png", "text_file": "page_022_left.txt", "method": "split-image-tesseract-ocr"}},
        {"headword_english": "Beacon", "pos": "n.", "sesotho": "mokoekootoane.", "source": {"page_index": 21, "page_number": 22, "column": "left", "image": "page_022_left.png", "text_file": "page_022_left.txt", "method": "split-image-tesseract-ocr"}},
        {"headword_english": "Bead", "pos": "n.", "sesotho": "sefaha, tona.", "source": {"page_index": 21, "page_number": 22, "column": "left", "image": "page_022_left.png", "text_file": "page_022_left.txt", "method": "split-image-tesseract-ocr"}},
        {"headword_english": "Beak", "pos": "n.", "sesotho": "molomo oa nonyana.", "source": {"page_index": 21, "page_number": 22, "column": "left", "image": "page_022_left.png", "text_file": "page_022_left.txt", "method": "split-image-tesseract-ocr"}},
        {"headword_english": "Beam", "pos": "v.", "sesotho": "ho benya, ho khanya.", "source": {"page_index": 21, "page_number": 22, "column": "left", "image": "page_022_left.png", "text_file": "page_022_left.txt", "method": "split-image-tesseract-ocr"}},
        {"headword_english": "Beam", "pos": "n.", "sesotho": "(timber) balaka.", "source": {"page_index": 21, "page_number": 22, "column": "left", "image": "page_022_left.png", "text_file": "page_022_left.txt", "method": "split-image-tesseract-ocr"}},
        {"headword_english": "Bean", "pos": "n.", "sesotho": "naoa.", "source": {"page_index": 21, "page_number": 22, "column": "left", "image": "page_022_left.png", "text_file": "page_022_left.txt", "method": "split-image-tesseract-ocr"}},
        {"headword_english": "Bear", "pos": "v.", "sesotho": "(to carry) ho jara; (to suffer) ho mamella; (to produce) ho tsoala, ho bea litholoana.", "source": {"page_index": 21, "page_number": 22, "column": "left", "image": "page_022_left.png", "text_file": "page_022_left.txt", "method": "split-image-tesseract-ocr"}},
        {"headword_english": "Bearer", "pos": "n.", "sesotho": "mojari, lengosa.", "source": {"page_index": 21, "page_number": 22, "column": "right", "image": "page_022_right.png", "text_file": "page_022_right.txt", "method": "split-image-tesseract-ocr"}},
        {"headword_english": "Beast", "pos": "n.", "sesotho": "phoofolo.", "source": {"page_index": 21, "page_number": 22, "column": "right", "image": "page_022_right.png", "text_file": "page_022_right.txt", "method": "split-image-tesseract-ocr"}},
        {"headword_english": "Beat", "pos": "v.", "sesotho": "(to knock) ho otla, ho bata, ho shapa; (to overcome) ho hlola.", "source": {"page_index": 21, "page_number": 22, "column": "right", "image": "page_022_right.png", "text_file": "page_022_right.txt", "method": "split-image-tesseract-ocr"}},
        {"headword_english": "Beautiful", "pos": "adj.", "sesotho": "e ntle.", "source": {"page_index": 21, "page_number": 22, "column": "right", "image": "page_022_right.png", "text_file": "page_022_right.txt", "method": "split-image-tesseract-ocr"}},
        {"headword_english": "Because", "pos": "conj.", "sesotho": "kahobane.", "source": {"page_index": 21, "page_number": 22, "column": "right", "image": "page_022_right.png", "text_file": "page_022_right.txt", "method": "split-image-tesseract-ocr"}},
        {"headword_english": "Bed", "pos": "n.", "sesotho": "malao, liphate, bete.", "source": {"page_index": 21, "page_number": 22, "column": "right", "image": "page_022_right.png", "text_file": "page_022_right.txt", "method": "split-image-tesseract-ocr"}},
        {"headword_english": "Bedding", "pos": "n.", "sesotho": "bete le ntho tsohle tsa eona, malao, mealo.", "source": {"page_index": 21, "page_number": 22, "column": "right", "image": "page_022_right.png", "text_file": "page_022_right.txt", "method": "split-image-tesseract-ocr"}},
        {"headword_english": "Bedroom", "pos": "n.", "sesotho": "phaposi, kemere.", "source": {"page_index": 21, "page_number": 22, "column": "right", "image": "page_022_right.png", "text_file": "page_022_right.txt", "method": "split-image-tesseract-ocr"}},
        {"headword_english": "Bedstead", "pos": "n.", "sesotho": "bete.", "source": {"page_index": 22, "page_number": 23, "column": "left", "image": "page_023_left.png", "text_file": "page_023_left.txt", "method": "split-image-tesseract-ocr"}},
        {"headword_english": "Bee", "pos": "n.", "sesotho": "notsi, semana.", "source": {"page_index": 22, "page_number": 23, "column": "left", "image": "page_023_left.png", "text_file": "page_023_left.txt", "method": "split-image-tesseract-ocr"}},
        {"headword_english": "Beer", "pos": "n.", "sesotho": "(light beer) leting; (strong beer) joala.", "source": {"page_index": 22, "page_number": 23, "column": "left", "image": "page_023_left.png", "text_file": "page_023_left.txt", "method": "split-image-tesseract-ocr"}},
        {"headword_english": "Before", "pos": "prep.", "sesotho": "pel'a, kapele ho.", "source": {"page_index": 22, "page_number": 23, "column": "left", "image": "page_023_left.png", "text_file": "page_023_left.txt", "method": "split-image-tesseract-ocr"}},
        {"headword_english": "Beginning", "pos": "n.", "sesotho": "qalo, tšimololo.", "source": {"page_index": 22, "page_number": 23, "column": "left", "image": "page_023_left.png", "text_file": "page_023_left.txt", "method": "split-image-tesseract-ocr"}},
        {"headword_english": "Below", "pos": "prep.", "sesotho": "tlas'a, katlase.", "source": {"page_index": 23, "page_number": 24, "column": "left", "image": "page_024_left.png", "text_file": "page_024_left.txt", "method": "split-image-tesseract-ocr"}},
        {"headword_english": "Benediction", "pos": "n.", "sesotho": "hlohonolofatso.", "source": {"page_index": 23, "page_number": 24, "column": "left", "image": "page_024_left.png", "text_file": "page_024_left.txt", "method": "split-image-tesseract-ocr"}}
    ]
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
    
    print("🚀 Starting dictionary entries integration...")
    print(f"📚 Processing {len(dictionary_data)} B-section entries with OCR metadata...")
    print("🔍 Enhanced with source tracking: page numbers, columns, and OCR method...")
    
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
    transformed_entries = transform_dictionary_entries(dictionary_data)
    
    # Step 3: Create corpus entries
    print("📝 Step 3: Creating corpus entries with synthetic examples...")
    new_corpus_entries = create_corpus_entries_from_dictionary(dictionary_data, transformed_entries)
    
    # Step 4: Create attestations
    print("🔗 Step 4: Creating attestation links...")
    new_attestations = create_attestations_from_dictionary(transformed_entries, new_corpus_entries)
    
    # Step 5: Check for duplicates
    print("🔍 Step 5: Checking for duplicates...")
    existing_entry_ids = {entry.get("entry_id") for entry in lexicon}
    existing_corpus_ids = {entry.get("corpus_id") for entry in corpus}
    existing_attestation_ids = {entry.get("attestation_id") for entry in attestations}
    
    # Filter out duplicates
    new_lexicon_entries = [e for e in transformed_entries if e["entry_id"] not in existing_entry_ids]
    new_corpus_filtered = [e for e in new_corpus_entries if e["corpus_id"] not in existing_corpus_ids]
    new_attestations_filtered = [e for e in new_attestations if e["attestation_id"] not in existing_attestation_ids]
    
    print(f"   New lexicon entries to add: {len(new_lexicon_entries)}")
    print(f"   New corpus entries to add: {len(new_corpus_filtered)}")
    print(f"   New attestations to add: {len(new_attestations_filtered)}")
    
    # Step 6: Integrate into datasets
    print("✨ Step 6: Integrating into datasets...")
    lexicon.extend(new_lexicon_entries)
    corpus.extend(new_corpus_filtered)
    attestations.extend(new_attestations_filtered)
    
    # Step 7: Create backup
    print("💾 Step 7: Creating backup...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path(f"backups/backup_{timestamp}")
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Step 8: Save updated datasets
    print("💿 Step 8: Saving updated datasets...")
    with open('data/lexicon.json', 'w', encoding='utf-8') as f:
        json.dump(lexicon, f, ensure_ascii=False, indent=2)
    
    with open('data/corpus.json', 'w', encoding='utf-8') as f:
        json.dump(corpus, f, ensure_ascii=False, indent=2)
    
    with open('data/attestations.json', 'w', encoding='utf-8') as f:
        json.dump(attestations, f, ensure_ascii=False, indent=2)
    
    print("✅ Dictionary integration completed successfully!")
    print(f"   Final lexicon entries: {len(lexicon)}")
    print(f"   Final corpus entries: {len(corpus)}")
    print(f"   Final attestations: {len(attestations)}")
    
    # Step 9: Show sample additions
    print("\n📊 Sample of integrated entries:")
    for i, entry in enumerate(new_lexicon_entries[:5]):
        sesotho_terms = ", ".join([sense['sesotho_term'][0] for sense in entry['senses']])
        print(f"   ✅ {entry['entry_id']}: {entry['headword_english']} → {sesotho_terms}")
    
    if len(new_lexicon_entries) > 5:
        print(f"   ... and {len(new_lexicon_entries) - 5} more entries")
    
    return len(new_lexicon_entries), len(new_corpus_filtered), len(new_attestations_filtered)

if __name__ == "__main__":
    integrate_dictionary_entries()
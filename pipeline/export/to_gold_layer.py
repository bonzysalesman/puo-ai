import sqlite3
import json
import uuid
import re
import sys

def init_db(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Morphology
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS morphology (
        root_id TEXT PRIMARY KEY,
        root_atom TEXT UNIQUE NOT NULL,
        semantic_domain TEXT,
        rehabilitation_notes TEXT
    )''')
    
    # 2. Lexicon
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS lexicon (
        entry_id TEXT PRIMARY KEY,
        headword_st TEXT UNIQUE NOT NULL,
        pos TEXT,
        noun_class VARCHAR(10),
        root_id TEXT,
        pems_standard BOOLEAN DEFAULT TRUE,
        maturity_score REAL DEFAULT 0.0,
        metadata TEXT, -- Store metadata as JSON string
        FOREIGN KEY (root_id) REFERENCES morphology(root_id)
    )''')
    
    # 3. Corpus
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS corpus (
        v450_id VARCHAR(12) PRIMARY KEY,
        book_id INTEGER,
        chapter INTEGER,
        verse INTEGER,
        content_st TEXT NOT NULL,
        content_en TEXT
    )''')
    
    # 4. Attestations
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS attestations (
        attestation_id TEXT PRIMARY KEY,
        entry_id TEXT,
        v450_id VARCHAR(12),
        concord_confidence REAL,
        manual_audit BOOLEAN DEFAULT FALSE,
        FOREIGN KEY (entry_id) REFERENCES lexicon(entry_id),
        FOREIGN KEY (v450_id) REFERENCES corpus(v450_id)
    )''')
    
    conn.commit()
    return conn

def migrate_data(conn, test_batch_path, corpus_path, attestations_path):
    cursor = conn.cursor()
    
    with open(test_batch_path, 'r') as f:
        lexicon_data = json.load(f)
    with open(corpus_path, 'r') as f:
        corpus_data = json.load(f)
    with open(attestations_path, 'r') as f:
        attest_link_data = json.load(f)
        
    # Build a lookup for corpus entries based on extracted v450 ID
    corpus_lookup = {}
    for c in corpus_data:
        source_str = c.get('source', '') or c.get('source_raw', '')
        v_match = re.search(r'v\d{7,9}', source_str)
        if v_match:
            corpus_lookup[v_match.group(0)] = c
            
    # Build a lookup for attestations by term (headword_st)
    term_attest_lookup = {}
    for a in attest_link_data:
        # Use entry_id from attestations if available, otherwise derive from sense_id
        entry_id_from_attestation = a.get('entry_id')
        if not entry_id_from_attestation:
            sense_id = a.get('sense_id', '')
            if '.' in sense_id:
                entry_id_from_attestation = sense_id.split('.')[0]
        
        # Fallback if still no usable ID, though this might be less reliable
        if not entry_id_from_attestation:
            continue 

        # Assuming 'match_terms' contains headwords or related terms for linking
        for term in a.get('match_terms', []):
            t = term.lower()
            if t not in term_attest_lookup: term_attest_lookup[t] = []
            term_attest_lookup[t].append({'attestation_id': a.get('attestation_id'), 'entry_id': entry_id_from_attestation})
    
    for entry in lexicon_data:
        entry_id = entry['entry_id']
        headword_st_raw = entry['headword_sesotho'][0]['orthographic']
        headword_st = headword_st_raw.strip().lower()
        
        # Step 1: Insert Morphology
        morph = entry.get('morphology', {})
        root_atom = morph.get('root', '')
        if isinstance(root_atom, list): root_atom = root_atom[0] if root_atom else ""
        root_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(root_atom)))
        
        # Use INSERT OR IGNORE for morphology to avoid duplicate roots
        cursor.execute('INSERT OR IGNORE INTO morphology (root_id, root_atom) VALUES (?, ?)', (root_id, str(root_atom)))
        
        # Step 2: Insert Lexicon
        pos = entry.get('pos', 'unknown')
        if isinstance(pos, list): pos = pos[0] if pos else "unknown"
        
        nc = morph.get('noun_class', 'unknown')
        if isinstance(nc, list): nc = nc[0] if nc else "unknown"
        
        meta = entry.get('metadata', {})
        # Store metadata as a JSON string
        metadata_json = json.dumps(meta) if meta else None
        
        cursor.execute('''
            INSERT OR REPLACE INTO lexicon (entry_id, headword_st, pos, noun_class, root_id, pems_standard, maturity_score, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            str(entry_id), str(headword_st_raw),
            str(pos), str(nc), str(root_id),
            bool(meta.get('rehabilitated', False)),
            float(meta.get('source_maturity', 0.0)),
            metadata_json
        ))
        
        # Step 3: Insert Evidence
        links = term_attest_lookup.get(headword_st, [])
        for link in links:
            # Use the entry_id derived from attestations for linking
            attestation_entry_id = link.get('entry_id')
            if not attestation_entry_id:
                continue # Skip if no usable ID can be determined

            # Assuming source_raw in attestations.json contains the v450 ID
            source_str = link.get('source_raw', '')
            v_match = re.search(r'v\d{7,9}', source_str)
            if v_match:
                v450_id = v_match.group(0)
                verse_info = corpus_lookup.get(v450_id)
                if verse_info:
                    cursor.execute('INSERT OR IGNORE INTO corpus (v450_id, content_st, content_en) VALUES (?, ?, ?)', 
                                 (v450_id, verse_info.get('sesotho', verse_info.get('sesotho_text')), verse_info.get('english', verse_info.get('english_text'))))
                    cursor.execute('INSERT OR REPLACE INTO attestations (attestation_id, entry_id, v450_id, concord_confidence) VALUES (?, ?, ?, ?)',
                                 (str(uuid.uuid4()), str(attestation_entry_id), v450_id, 0.9))

    conn.commit()
    print(f"Migration of {len(lexicon_data)} entries to Gold Layer complete.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 to_gold_layer.py <audited_lexicon_json>")
        sys.exit(1)
        
    lexicon_path = sys.argv[1]
    db_path = "data/puo_gold.db"
    conn = init_db(db_path)
    migrate_data(conn, lexicon_path, "data/corpus.json", "data/attestations.json")
    conn.close()

import fitz
import re
import json

def test_extract_casalis(pdf_path, dest_file):
    doc = fitz.open(pdf_path)
    page_num = 50
    page = doc[page_num]
    
    # Get text blocks
    blocks = page.get_text("blocks")
    
    # Determine horizontal midpoint to separate columns
    mid_x = page.rect.width / 2
    
    col1 = []
    col2 = []
    
    # Sort blocks by column
    for b in blocks:
        if b[6] == 0:  # Check if it's a text block
            if b[0] < mid_x:
                col1.append(b)
            else:
                col2.append(b)
                
    # Sort blocks top-to-bottom within each column
    col1.sort(key=lambda b: b[1])
    col2.sort(key=lambda b: b[1])
    
    # Combine text, preserving basic flow
    full_text = "\n".join([b[4].replace('\n', ' ').strip() for b in col1 + col2])
    
    entries = []
    
    # Mabille headwords are Capitalized (e.g. "Bopaki", "Bopalami") at the start of blocks.
    # Often followed by "(from...)" or a part of speech like "n.,", "v. n.,", etc.
    # We remove the ^ anchor because blocks might be merged, and instead anchor on the pos markers.
    pattern = re.compile(r'\b([A-ZŠ\’\'][a-zš\’\']+)\b\s*(?:\(from [^\)]+\))?\s*[,;\.]\s*(n\.|v\. [tn]\.|adj\.|adv\.|v\.)')
    
    matches = list(pattern.finditer(full_text))
    
    for i, match in enumerate(matches):
        hw = match.group(1)
        pos = match.group(2) if match.group(2) else "unknown"
        start_idx = match.end()
        
        end_idx = matches[i+1].start() if i + 1 < len(matches) else len(full_text)
        
        definition = full_text[start_idx:end_idx].strip()
        definition = re.sub(r'\s+', ' ', definition)
        
        # Only keep it if the definition is substantial (ignores random OCR floating capitals)
        if len(definition) > 5:
            entries.append({
                "headword_sesotho_raw": hw,
                "pos_raw": pos,
                "definition_raw": definition
            })
        
    with open(dest_file, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)
        
    print(f"Test Extraction of {pdf_path} Page {page_num}: Found {len(entries)} entries. Saved to {dest_file}")

test_extract_casalis("/Users/bonzysalesman/Project/PUO-AI/Mabille_Adolphe_Sesuto_English_Dictionary.pdf", "test_mabille_extraction.json")


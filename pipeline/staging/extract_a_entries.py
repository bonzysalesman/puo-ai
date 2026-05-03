import fitz
import re
import json

def extract_casalis_pages(pdf_path, dest_file, start_page, end_page):
    doc = fitz.open(pdf_path)
    entries = []
    
    # Capitalized word, optional punctuation/spaces, 1-4 lowercase letters/numbers, followed by a dot
    pattern = re.compile(r'([A-Z][A-Za-z]+)\s*[,;\.]\s*([a-z0-9]{1,4}\.)')
    
    for page_num in range(start_page, end_page + 1):
        try:
            page = doc[page_num]
            blocks = page.get_text("blocks")
            mid_x = page.rect.width / 2
            
            col1, col2 = [], []
            for b in blocks:
                if b[6] == 0:  # Check if it's a text block
                    if b[0] < mid_x:
                        col1.append(b)
                    else:
                        col2.append(b)
                        
            col1.sort(key=lambda b: b[1])
            col2.sort(key=lambda b: b[1])
            
            full_text = "\n".join([b[4].replace('\n', ' ').strip() for b in col1 + col2])
            
            matches = list(pattern.finditer(full_text))
            for i, match in enumerate(matches):
                hw = match.group(1)
                pos = match.group(2)
                start_idx = match.end()
                end_idx = matches[i+1].start() if i + 1 < len(matches) else len(full_text)
                definition = full_text[start_idx:end_idx].strip()
                pos = pos.replace('11.', 'n.')
                definition = re.sub(r'\s+', ' ', definition)
                
                # Only keep ones starting with A (allowing for some OCR noise at start, but checking first char)
                if hw.upper().startswith('A'):
                    entries.append({
                        "headword_english": hw,
                        "pos_raw": pos,
                        "definition_raw": definition
                    })
        except Exception as e:
            print(f"Error on Casalis page {page_num}: {e}")

    with open(dest_file, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)
    print(f"Extracted {len(entries)} 'A' entries from Casalis. Saved to {dest_file}")

def extract_mabille_pages(pdf_path, dest_file, start_page, end_page):
    doc = fitz.open(pdf_path)
    entries = []
    
    pattern = re.compile(r'\b([A-ZŠ\’\'][a-zš\’\']+)\b\s*(?:\(from [^\)]+\))?\s*[,;\.]\s*(n\.|v\. [tn]\.|adj\.|adv\.|v\.|int\.|prep\.|conj\.)')
    
    for page_num in range(start_page, end_page + 1):
        try:
            page = doc[page_num]
            blocks = page.get_text("blocks")
            mid_x = page.rect.width / 2
            
            col1, col2 = [], []
            for b in blocks:
                if b[6] == 0:
                    if b[0] < mid_x:
                        col1.append(b)
                    else:
                        col2.append(b)
                        
            col1.sort(key=lambda b: b[1])
            col2.sort(key=lambda b: b[1])
            
            full_text = "\n".join([b[4].replace('\n', ' ').strip() for b in col1 + col2])
            
            matches = list(pattern.finditer(full_text))
            for i, match in enumerate(matches):
                hw = match.group(1)
                pos = match.group(2) if match.group(2) else "unknown"
                start_idx = match.end()
                end_idx = matches[i+1].start() if i + 1 < len(matches) else len(full_text)
                
                definition = full_text[start_idx:end_idx].strip()
                definition = re.sub(r'\s+', ' ', definition)
                
                if len(definition) > 5 and hw.upper().startswith('A'):
                    entries.append({
                        "headword_sesotho_raw": hw,
                        "pos_raw": pos,
                        "definition_raw": definition
                    })
        except Exception as e:
            print(f"Error on Mabille page {page_num}: {e}")

    with open(dest_file, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)
    print(f"Extracted {len(entries)} 'A' entries from Mabille. Saved to {dest_file}")

casalis_path = "/Users/bonzysalesman/Project/PUO-AI/englishsothovoca00casauoft.pdf"
mabille_path = "/Users/bonzysalesman/Project/PUO-AI/Mabille_Adolphe_Sesuto_English_Dictionary.pdf"

print("Extracting Casalis 'A' section...")
extract_casalis_pages(casalis_path, "casalis_a_raw.json", 11, 19)

print("Extracting Mabille 'A' section...")
extract_mabille_pages(mabille_path, "mabille_a_raw.json", 11, 17)

import fitz
import re

pdf_files = {
    "Casalis": "/Users/bonzysalesman/Project/PUO-AI/englishsothovoca00casauoft.pdf",
    "Mabille": "/Users/bonzysalesman/Project/PUO-AI/Mabille_Adolphe_Sesuto_English_Dictionary.pdf"
}

def locate_letter_a(filepath, is_mabille=False):
    doc = fitz.open(filepath)
    start_page = -1
    end_page = -1
    
    # We'll scan the first 100 pages to find where 'A' starts and ends.
    # We look for standalone letter 'A' or the first few entries.
    for i in range(10, min(100, doc.page_count)):
        page = doc[i]
        text = page.get_text()
        
        # Look for the start of B
        if is_mabille:
            if re.search(r'\nBA\b', text) or re.search(r'\nBABA\b', text):
                if end_page == -1:
                    end_page = i
                    break
            elif re.search(r'\bA\b', text) and start_page == -1:
                start_page = i
        else:
            if re.search(r'\bB[a-z]{3,}\b', text) and i > 15:
                # We found a B word after page 15, let's say it's the end of A
                if end_page == -1:
                    end_page = i
                    break
            elif re.search(r'\bA[a-z]{3,}\b', text) and i > 10:
                if start_page == -1:
                    start_page = i
    
    print(f"{filepath} 'A' section: Start Page ~{start_page}, End Page ~{end_page}")

for name, path in pdf_files.items():
    locate_letter_a(path, is_mabille=(name == "Mabille"))

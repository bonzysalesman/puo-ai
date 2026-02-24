import fitz  # PyMuPDF
import os

pdf_files = [
    "/Users/bonzysalesman/Project/PUO-AI/Mabille_Adolphe_Sesuto_English_Dictionary.pdf",
    "/Users/bonzysalesman/Project/PUO-AI/englishsothovoca00casauoft.pdf"
]

def analyze_pdf(filepath):
    print(f"--- Analyzing {os.path.basename(filepath)} ---")
    try:
        doc = fitz.open(filepath)
        print(f"Total Pages: {doc.page_count}")
        print(f"Metadata: {doc.metadata}")
        
        # Sample a page from the middle of the document
        sample_page_num = min(50, doc.page_count // 2)
        page = doc[sample_page_num]
        
        # Extract text in blocks to see layout
        blocks = page.get_text("blocks")
        print(f"\nSample Page {sample_page_num} Text Blocks:")
        for b in blocks[:10]:  # Print first 10 blocks
            print(f"Block rect: {b[:4]}")
            print(f"Text:\n{b[4].strip()}")
            print("-" * 20)
            
        print("\n\n")
    except Exception as e:
        print(f"Error reading {filepath}: {e}")

for f in pdf_files:
    if os.path.exists(f):
        analyze_pdf(f)
    else:
        print(f"File not found: {f}")

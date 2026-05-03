import json

def extract_b_batch(lexicon_path, output_path, count=500):
    with open(lexicon_path, 'r') as f:
        lexicon = json.load(f)
    
    b_batch = []
    for entry in lexicon:
        if entry.get("headword_sesotho") and entry["headword_sesotho"]:
            ortho = entry["headword_sesotho"][0].get("orthographic", "").lower()
            if ortho.startswith("b"):
                b_batch.append(entry)
                if len(b_batch) >= count:
                    break
                    
    with open(output_path, 'w') as f:
        json.dump(b_batch, f, indent=2, ensure_ascii=False)
    
    print(f"Extracted {len(b_batch)} entries starting with 'B' to {output_path}")

if __name__ == "__main__":
    extract_b_batch("data/lexicon.json", "data/b_batch_500.json")

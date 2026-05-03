import json

def extract_batch(lexicon_path, output_path, letter, count=500):
    with open(lexicon_path, 'r') as f:
        lexicon = json.load(f)
    
    batch = []
    for entry in lexicon:
        if entry.get("headword_sesotho") and entry["headword_sesotho"]:
            ortho = entry["headword_sesotho"][0].get("orthographic", "").lower()
            if ortho.startswith(letter.lower()):
                batch.append(entry)
                if len(batch) >= count:
                    break
                    
    with open(output_path, 'w') as f:
        json.dump(batch, f, indent=2, ensure_ascii=False)
    
    print(f"Extracted {len(batch)} entries starting with '{letter.upper()}' to {output_path}")

if __name__ == "__main__":
    extract_batch("data/lexicon.json", "data/d_batch_500.json", "d")

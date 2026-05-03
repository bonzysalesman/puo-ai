import json
from collections import Counter

def analyze_lexicon_distribution(lexicon_path, exclude_letter='d'):
    letter_counts = Counter()
    total_entries = 0

    with open(lexicon_path, 'r') as f:
        lexicon = json.load(f)
    
    total_entries = len(lexicon)

    for entry in lexicon:
        if entry.get("headword_sesotho") and entry["headword_sesotho"]:
            ortho = entry["headword_sesotho"][0].get("orthographic", "").lower()
            if ortho and ortho[0].isalpha():
                first_letter = ortho[0]
                if first_letter != exclude_letter:
                    letter_counts[first_letter] += 1

    if not letter_counts:
        print(f"No entries found starting with letters other than '{exclude_letter.upper()}'.")
        return None, 0

    # Sort by count descending
    sorted_counts = sorted(letter_counts.items(), key=lambda item: item[1], reverse=True)
    
    print(f"Analysis of {total_entries} total entries:")
    print("Lexicon distribution by first letter (excluding '{}'):".format(exclude_letter.upper()))
    for letter, count in sorted_counts:
        print(f"- {letter.upper()}: {count} entries")

    largest_letter, max_count = sorted_counts[0]
    print(f"
Largest batch (excluding '{exclude_letter.upper()}'): '{largest_letter.upper()}' with {max_count} entries.")
    return largest_letter, max_count

if __name__ == "__main__":
    analysis_results = analyze_lexicon_distribution("data/lexicon.json", exclude_letter='d')
    if analysis_results[0]:
        target_letter = analysis_results[0]
        print(f"
Proceeding to extract batch for letter: {target_letter.upper()}")
        # Now, call extract_batch with the identified letter and count=500
        # (Assuming extract_batch.py is available in the path or project root)
        # import subprocess
        # subprocess.run(["python3", "pipeline/staging/extract_batch.py", "data/lexicon.json", f"data/{target_letter.lower()}_batch_500.json", target_letter])


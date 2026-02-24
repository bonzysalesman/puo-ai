import argparse
import json


def add_word(word_map, word):
    word = word.strip()
    if not word:
        return
    key = word.lower()
    if key not in word_map:
        word_map[key] = word


def extract_words(dictionary):
    # Use dicts keyed by lowercase for deduplication, storing preferred display form.
    english_words = {}
    sesotho_words = {}

    for entry in dictionary:
        en_hw = entry.get("headword_english", "").strip()
        if en_hw:
            # Headword display form has highest priority.
            english_words[en_hw.lower()] = en_hw

        thesaurus = entry.get("thesaurus", {})
        for syn in thesaurus.get("synonyms_en", []):
            add_word(english_words, syn)
        for ant in thesaurus.get("antonyms_en", []):
            add_word(english_words, ant)

        for hw in entry.get("headword_sesotho", []):
            orth = hw.get("orthographic", "").strip()
            if orth:
                sesotho_words[orth.lower()] = orth

        for sense in entry.get("senses", []):
            for term in sense.get("sesotho_term", []):
                add_word(sesotho_words, term)

        for syn in thesaurus.get("synonyms_st", []):
            add_word(sesotho_words, syn)
        for ant in thesaurus.get("antonyms_st", []):
            add_word(sesotho_words, ant)

    english_sorted = sorted(english_words.values(), key=str.lower)
    sesotho_sorted = sorted(sesotho_words.values(), key=str.lower)
    return english_sorted, sesotho_sorted


def render_markdown(english_words, sesotho_words):
    lines = [
        "# PUO-AI Word List",
        "",
        "> Auto-extracted from `dictionary.json`. Add new words below each section manually.",
        "",
        f"## English Words ({len(english_words)} unique)",
        "",
    ]
    lines.extend(f"- {word}" for word in english_words)
    lines.extend(
        [
            "",
            f"## Sesotho Words ({len(sesotho_words)} unique)",
            "",
        ]
    )
    lines.extend(f"- {word}" for word in sesotho_words)
    lines.append("")
    return "\n".join(lines)


def load_dictionary(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_wordlist(output_path, content):
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)


def parse_args():
    parser = argparse.ArgumentParser(description="Extract a deduplicated word list from dictionary.json.")
    parser.add_argument("--dictionary", default="dictionary.json")
    parser.add_argument("--output", default="wordlist.md")
    return parser.parse_args()


def main():
    args = parse_args()
    dictionary = load_dictionary(args.dictionary)
    english_words, sesotho_words = extract_words(dictionary)
    markdown = render_markdown(english_words, sesotho_words)
    write_wordlist(args.output, markdown)
    print(f"Done! Extracted {len(english_words)} English and {len(sesotho_words)} Sesotho unique words.")
    print(f"Saved to '{args.output}'.")


if __name__ == "__main__":
    main()

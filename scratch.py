import json

raw = """{
  "entry_id": "st_L_0102",
  "headword_english": "Heaven"
},"""

cleaned = raw.strip()
if cleaned.endswith(","):
    cleaned = cleaned[:-1]

print("Parsed:", json.loads(cleaned))

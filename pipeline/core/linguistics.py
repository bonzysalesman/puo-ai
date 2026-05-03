import re
import json

class LinguisticKernel:
    """
    The Central Nervous System of PUO-AI.
    Handles morphological transformations, noun class validation, and root resolution.
    Refined with Concord Monitor for L/D shifts in root extraction.
    """
    
    # Consonant shifts for Nasal Permutations (handled in PERMUTATOR_MAP) and L/D strengthening reversal
    PERMUTATOR_MAP = {
        'b': 'p',   # ho bala -> palo
        'l': 't',   # ho lora -> toro
        'h': 'kh',  # ho hula -> khulo
        'f': 'ph',  # ho fepa -> phepo
        'r': 'th',  # ho ruta -> thuto
        's': 'tsh', # ho sila -> tshilo
    }
    
    # Reversal of common L/D strengthening patterns for root finding
    STRENGTHENING_REVERSAL_MAP = {
        'd': 'l', # e.g., Dira (to do/act) might be derived from L-root
        't': 'r', # e.g., Tiro (work) from -rir-?
        'p': 'b'  # e.g., Sebopho (shape) from -bope-?
    }
    
    # Noun Class to Concord Mapping
    CONCORD_MAP = {
        "1": ["o", "u", "a"], "2": ["ba"], "3": ["o", "u"], "4": ["e"],
        "5": ["le"], "6": ["a"], "7": ["se"], "8": ["li"], "9": ["e"],
        "10": ["li"], "14": ["bo"], "15": ["ho"]
    }
    
    # Prefix patterns for Noun Class detection
    NOUN_CLASS_PREFIXES = {
        "15": r"^ho",                               # ho lisa, ho khabisa -> Class 15
        "1": r"^(?:'mo|mo(?![aeiou])|m(?=[aeiou]))", 
        "2": r"^ba",                               # batho -> Class 2
        "7": r"^se",                               # sera -> Class 7
        "14": r"^bo",                              # bofebe, bomalibe -> Class 14
        "9": r"^[kptmnšqh]",                        # taba, puso, naha -> Class 9
    }

    VERBAL_EXTENSIONS = [
        {"suffix": "uoa", "type": "Passive"}, {"suffix": "ana", "type": "Reciprocal"},
        {"suffix": "isa", "type": "Causative"}, {"suffix": "ela", "type": "Applied"}
    ]

    def __init__(self, taxonomy_path=None, bridge_path=None):
        self.taxonomy = {}
        self.bridge = {"vowel_shifts": [], "consonant_norm": []}
        
        if taxonomy_path:
            try:
                with open(taxonomy_path, 'r') as f:
                    self.taxonomy = json.load(f).get("categories", {})
            except: pass
            
        if bridge_path:
            try:
                with open(bridge_path, 'r') as f:
                    data = json.load(f)
                    self.bridge["vowel_shifts"] = data.get("historical_vowel_shifts", [])
                    self.bridge["consonant_norm"] = data.get("consonant_normalization", [])
            except: pass

    def normalize_orthography(self, word):
        """Phase I: Orthographic Rehabilitation."""
        normalized = word.lower()
        rehabilitated = False
        for shift in self.bridge["vowel_shifts"]:
            if shift["original"] in normalized:
                normalized = normalized.replace(shift["original"], shift["replacement"])
                rehabilitated = True
        for norm in self.bridge["consonant_norm"]:
            if norm["original"] in normalized:
                normalized = normalized.replace(norm["original"], norm["replacement"])
                rehabilitated = True
        return normalized, rehabilitated

    def get_profile(self, headword_sesotho_list, english_hint=""):
        """Phase IV: Profile Generation with Metadata."""
        if not headword_sesotho_list:
            return {"noun_class": "unknown", "root": "", "rehabilitated": False, "deconstructed": False, "shift_detected": False}
            
        raw_word = headword_sesotho_list[0]["orthographic"].strip().lower()
        word, rehabilitated = self.normalize_orthography(raw_word)
        
        pos = "noun"
        if word.startswith("ho "): pos = "verb"
        
        n_class = self.guess_noun_class(word, english_hint)
        root, deconstructed, shift_detected = self.extract_root(word, pos, n_class) # Pass n_class for context
        
        source_maturity = 0.5
        if n_class in ["1", "3", "7", "9", "14"]: source_maturity = 0.9
        if "AUDIT_REQUIRED" in n_class: source_maturity = 0.3

        return {
            "noun_class": n_class,
            "root": root,
            "pos": pos,
            "is_diminutive": self.check_diminutive(word),
            "rehabilitated": rehabilitated,
            "deconstructed": deconstructed,
            "source_maturity": source_maturity,
            "original_orthography": raw_word if rehabilitated else None,
            "shift_detected": shift_detected # New metadata flag
        }

    def check_diminutive(self, word):
        return word.endswith("nyana") or (word.endswith("ana") and len(word) > 5)

    def guess_noun_class(self, word, english_hint=""):
        """Phase II: Semantic Disambiguation."""
        word = word.strip().lower()
        detected_prefix_class = "unknown"
        for n_class, pattern in self.NOUN_CLASS_PREFIXES.items():
            if re.match(pattern, word):
                detected_prefix_class = n_class
                break
        
        eng_hint = english_hint.lower()
        for cat_name, cat_data in self.taxonomy.items():
            if any(k in eng_hint for k in cat_data.get("indicators_en", [])):
                if detected_prefix_class in ["1", "3", "unknown"]: return cat_data["bias"]
                return detected_prefix_class if detected_prefix_class != "unknown" else cat_data["bias"]
            if any(k in word for k in cat_data.get("indicators_st", [])):
                if detected_prefix_class in ["1", "3", "unknown"]: return cat_data["bias"]
                
        if detected_prefix_class == "1": return "1/3 [AUDIT_REQUIRED]"
        return detected_prefix_class

    def extract_root(self, word, pos, noun_class):
        """Phase III: Atomic Deconstruction (Recursive)."""
        word = word.strip().lower()
        core = word
        deconstructed = False
        shift_detected = False # Flag for L/D shift detection

        # --- Apply L/D Shift Reversal for Root Extraction ---
        # This logic assumes a strengthened 'd' form in Class 9/10 might stem from an 'l' root.
        if pos == "noun" and noun_class in ['9', '10']:
            for strong_consonant, weak_consonant in self.STRENGTHENING_REVERSAL_MAP.items():
                if word.startswith(strong_consonant):
                    potential_base = weak_consonant + word[len(strong_consonant):]
                    if len(potential_base) > 2 and potential_base not in ['unknown']: # Heuristic check
                        core = potential_base
                        deconstructed = True
                        shift_detected = True # Mark that a shift was detected/applied
                        break # Use the first reversed shift found

        if pos == "verb" and word.startswith("ho "):
            core = word[3:]
            changed = True
            while changed:
                changed = False
                sorted_exts = sorted(self.VERBAL_EXTENSIONS, key=lambda x: len(x["suffix"]), reverse=True)
                for ext in sorted_exts:
                    if core.endswith(ext["suffix"]):
                        core = core[:-len(ext["suffix"])]
                        if not core.endswith("a"): core += "a"
                        deconstructed = True
                        changed = True
                        break
        
        # Strip Noun Prefixes (after potential shift reversal)
        if pos == "noun":
            for n_class, pattern in self.NOUN_CLASS_PREFIXES.items():
                if n_class != "9": 
                    prefix_match = re.search(pattern, core)
                    if prefix_match:
                        core = core[prefix_match.end():]
                        deconstructed = True
                        break
        
        return f"-{core}", deconstructed, shift_detected # Return shift_detected flag

    def validate_concord(self, hypothesized_class, context_string):
        if hypothesized_class in ["unknown", "1/3 [AUDIT_REQUIRED]"]:
            return {"is_valid": True, "confidence": 0.0, "detected_class": None}
        context_lower = context_string.lower()
        words = re.findall(r'\b\w+\b', context_lower)
        expected = self.CONCORD_MAP.get(hypothesized_class, [])
        found_matches = [w for w in words if w in expected]
        if found_matches:
            return {"is_valid": True, "confidence": min(1.0, len(found_matches)/2.0), "detected_class": hypothesized_class}
        for n_class, concords in self.CONCORD_MAP.items():
            if n_class == hypothesized_class: continue
            other_matches = [w for w in words if w in concords]
            if other_matches:
                return {"is_valid": False, "confidence": min(1.0, len(other_matches)/2.0), "detected_class": n_class}
        return {"is_valid": True, "confidence": 0.0, "detected_class": None}

    def permutate(self, verb_root):
        clean_root = verb_root.lstrip('-')
        if not clean_root: return ""
        first_char = clean_root[0]
        if first_char in self.PERMUTATOR_MAP:
            return self.PERMUTATOR_MAP[first_char] + clean_root[1:]
        return clean_root

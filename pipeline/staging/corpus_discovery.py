import os
import re

def scan_for_bsep(root_dir):
    print(f"Scanning {root_dir} for BSEP orthography patterns...")
    
    # Patterns for BSEP (South Africa)
    bsep_patterns = {
        "wa_concord": r"\bwa\b",
        "jehofa": r"\bjehofa\b",
        "morena": r"\bmorena\b",
        "sh_sound": r"\bsh",
    }
    
    # Patterns for PEMS (Lesotho)
    pems_patterns = {
        "oa_concord": r"\boa\b",
        "jehova": r"\bjehova\b",
        "s_tilde": r"š",
    }
    
    results = []
    
    for root, dirs, files in os.walk(root_dir):
        if ".git" in dirs: dirs.remove(".git")
        if ".venv" in dirs: dirs.remove(".venv")
        
        for file in files:
            if file.endswith((".html", ".json", ".txt")):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read().lower()
                        
                        bsep_score = sum(len(re.findall(p, content)) for p in bsep_patterns.values())
                        pems_score = sum(len(re.findall(p, content)) for p in pems_patterns.values())
                        
                        if bsep_score > 0 or pems_score > 0:
                            classification = "BSEP (ZA)" if bsep_score > pems_score else "PEMS (LS)"
                            results.append({
                                "file": file_path,
                                "bsep_score": bsep_score,
                                "pems_score": pems_score,
                                "classification": classification
                            })
                except:
                    continue
                    
    return results

if __name__ == "__main__":
    findings = scan_for_bsep(".")
    print("\n--- CORPUS DISCOVERY RESULTS ---")
    for res in sorted(findings, key=lambda x: x['bsep_score'], reverse=True):
        if res['bsep_score'] > 0:
            print(f"File: {res['file']}")
            print(f"  BSEP Score: {res['bsep_score']}, PEMS Score: {res['pems_score']}")
            print(f"  Likely: {res['classification']}")
            print("-" * 30)

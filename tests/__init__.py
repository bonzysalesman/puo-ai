import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
for _sub in ("enrichment", "export", "staging", "ocr"):
    _p = str(_root / "pipeline" / _sub)
    if _p not in sys.path:
        sys.path.insert(0, _p)

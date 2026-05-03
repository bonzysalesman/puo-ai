"""Naked parser: two-pass normalization
Pass 1: protect clusters (collapse to placeholders)
Pass 2: Unicode NFKD + strip combining marks
Finally: restore protected clusters
"""
import re
import unicodedata
from typing import List, Tuple

PLACEHOLDER = "__CLUSTER_{}__"

DEFAULT_PEMS_PROTECT = ['tš', 'š']


def protect_clusters(text: str, clusters: List[str]) -> Tuple[str, List[str]]:
    # Sort clusters by length desc so longer clusters are protected first
    clusters_sorted = sorted(set(clusters), key=lambda s: -len(s))
    mapping = []
    out = text
    for i, cl in enumerate(clusters_sorted):
        if not cl:
            continue
        ph = PLACEHOLDER.format(i)
        out = re.sub(re.escape(cl), ph, out, flags=re.IGNORECASE)
        mapping.append((ph, cl))
    return out, mapping


def restore_clusters(text: str, mapping: List[Tuple[str, str]]) -> str:
    out = text
    for ph, cl in mapping:
        out = out.replace(ph, cl)
    return out


def strip_diacritics(text: str, preserve_placeholders: bool=True) -> str:
    # Removes combining marks while leaving placeholders intact
    nfkd = unicodedata.normalize('NFKD', text)
    out_chars = []
    for c in nfkd:
        if unicodedata.combining(c):
            # skip combining marks
            continue
        out_chars.append(c)
    return ''.join(out_chars)


def naked(text: str, clusters: List[str]=None, preserve_pems: bool=True) -> str:
    clusters = clusters or []
    if preserve_pems:
        # ensure PEMS special chars like 'š' and 'tš' are protected
        clusters = list(clusters) + DEFAULT_PEMS_PROTECT
    # Pass 1: protect clusters
    protected, mapping = protect_clusters(text, clusters)
    # Pass 2: strip diacritics
    stripped = strip_diacritics(protected)
    # Normalize whitespace
    stripped = re.sub(r'\s+', ' ', stripped).strip()
    # Restore clusters
    restored = restore_clusters(stripped, mapping)
    return restored


if __name__ == '__main__':
    sample = "hōle tjhā ya á ša tšā"
    print(naked(sample, clusters=['tjh','ya']))
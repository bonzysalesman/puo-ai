#!/usr/bin/env python3
"""
Sesotho OCR Enhancement Module
Provides specialized OCR processing for Sesotho historical documents.
Includes orthographic correction, diacritic handling, and historical text normalization.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class SesothoOCRConfig:
    """Configuration for Sesotho-specific OCR enhancements."""
    enable_orthographic_correction: bool = True
    enable_diacritic_restoration: bool = True
    enable_historical_normalization: bool = True
    confidence_boost_threshold: float = 0.1
    dictionary_path: str = "data/lexicon.json"


class SesothoOCREnhancer:
    """
    Enhances OCR results for Sesotho text using linguistic knowledge.
    
    Features:
    - Orthographic error correction based on known patterns
    - Diacritic restoration for historical texts
    - Context-aware confidence boosting
    - Integration with existing lexicon for validation
    """
    
    def __init__(self, config: SesothoOCRConfig = None):
        self.config = config or SesothoOCRConfig()
        self.lexicon = self._load_lexicon()
        self.orthography_mappings = self._initialize_orthography_mappings()
        self.common_ocr_errors = self._initialize_ocr_error_patterns()
        
    def _load_lexicon(self) -> Dict[str, Any]:
        """Load the Sesotho lexicon for validation."""
        try:
            lexicon_path = Path(self.config.dictionary_path)
            if lexicon_path.exists():
                with open(lexicon_path, 'r', encoding='utf-8') as f:
                    lexicon_data = json.load(f)
                
                # Create lookup dictionary
                lookup = {}
                # Handle both list and dict formats
                if isinstance(lexicon_data, list):
                    for entry in lexicon_data:
                        if isinstance(entry, dict):
                            headword = entry.get('headword_sesotho', '').lower()
                            if headword:
                                lookup[headword] = entry
                elif isinstance(lexicon_data, dict):
                    # Handle dictionary format
                    for key, entry in lexicon_data.items():
                        if isinstance(entry, dict):
                            headword = entry.get('headword_sesotho', key).lower()
                            if headword:
                                lookup[headword] = entry
                
                logger.info(f"Loaded {len(lookup)} Sesotho headwords for validation")
                return lookup
        except Exception as e:
            logger.warning(f"Could not load lexicon: {e}")
        
        return {}
    
    def _initialize_orthography_mappings(self) -> Dict[str, str]:
        """Initialize orthographic correction mappings based on historical patterns."""
        return {
            # Common historical spelling variations
            'tj': 'tš',
            'ny': 'ñ',
            'ng': 'ŋ',
            
            # OCR confusion patterns
            'tsh': 'tš',
            'ng\'': 'ŋ',
            'nq': 'ng',
            
            # Diacritic restoration patterns
            'o\'': 'ô',
            'e\'': 'ê',
            'a\'': 'â',
            
            # Common OCR misreads
            'rn': 'm',
            'cl': 'd',
            'ii': 'll',
            '1': 'l',
            '0': 'o',
        }
    
    def _initialize_ocr_error_patterns(self) -> List[Tuple[str, str]]:
        """Initialize common OCR error patterns for Sesotho text."""
        return [
            # Character confusion patterns (regex, replacement)
            (r'\b1([aeiou])', r'l\1'),  # 1 -> l before vowels
            (r'([aeiou])1\b', r'\1l'),  # 1 -> l after vowels
            (r'\brn([aeiou])', r'm\1'),  # rn -> m before vowels
            (r'c1', 'cl'),              # c1 -> cl
            (r'ii', 'll'),              # ii -> ll
            (r'([td])h', r'\1š'),       # th/dh -> tš/dš in some contexts
            
            # Historical orthography corrections
            (r'\btj([aeiou])', r'tš\1'),  # tj -> tš
            (r'\bny([aeiou])', r'ñ\1'),   # ny -> ñ
            (r'ng\'', 'ŋ'),               # ng' -> ŋ
            
            # Punctuation and formatting issues
            (r'\s+', ' '),                # Multiple spaces -> single space
            (r'^\s+|\s+$', ''),           # Trim whitespace
            (r'([.!?])\s*\n\s*([a-z])', r'\1 \2'),  # Fix sentence breaks
        ]
    
    def correct_orthography(self, text: str) -> str:
        """Apply orthographic corrections to text."""
        if not self.config.enable_orthographic_correction:
            return text
        
        corrected = text
        
        # Apply simple mappings
        for old, new in self.orthography_mappings.items():
            corrected = corrected.replace(old, new)
        
        # Apply regex patterns
        for pattern, replacement in self.common_ocr_errors:
            corrected = re.sub(pattern, replacement, corrected)
        
        return corrected
    
    def restore_diacritics(self, text: str) -> str:
        """Attempt to restore missing diacritics based on lexicon."""
        if not self.config.enable_diacritic_restoration or not self.lexicon:
            return text
        
        words = text.split()
        restored_words = []
        
        for word in words:
            # Clean word for lookup
            clean_word = re.sub(r'[^\w\'-]', '', word.lower())
            
            if clean_word in self.lexicon:
                # Found exact match - keep original case pattern
                lexicon_word = self.lexicon[clean_word]['headword_sesotho']
                restored_word = self._preserve_case_pattern(word, lexicon_word)
                restored_words.append(restored_word)
            else:
                # Try without diacritics
                no_diacritic = self._remove_diacritics(clean_word)
                matches = [hw for hw in self.lexicon.keys() 
                          if self._remove_diacritics(hw) == no_diacritic]
                
                if len(matches) == 1:
                    # Single match - likely correct
                    lexicon_word = self.lexicon[matches[0]]['headword_sesotho']
                    restored_word = self._preserve_case_pattern(word, lexicon_word)
                    restored_words.append(restored_word)
                else:
                    # Multiple or no matches - keep original
                    restored_words.append(word)
        
        return ' '.join(restored_words)
    
    def _remove_diacritics(self, text: str) -> str:
        """Remove diacritics from text for comparison."""
        diacritic_map = str.maketrans(
            'àáâãäèéêëìíîïòóôõöùúûüýÿñçšžđťľň',
            'aaaaaeeeeiiiiooooouuruuyyncszddtln'
        )
        return text.translate(diacritic_map)
    
    def _preserve_case_pattern(self, original: str, replacement: str) -> str:
        """Apply case pattern from original word to replacement."""
        if not original or not replacement:
            return replacement
        
        result = []
        for i, char in enumerate(replacement):
            if i < len(original):
                if original[i].isupper():
                    result.append(char.upper())
                else:
                    result.append(char.lower())
            else:
                result.append(char)
        
        return ''.join(result)
    
    def validate_against_lexicon(self, text: str) -> Dict[str, float]:
        """Validate text against lexicon and return confidence metrics."""
        if not self.lexicon:
            return {"lexicon_coverage": 0.0, "word_count": 0, "known_words": 0}
        
        words = re.findall(r'\b\w+\b', text.lower())
        if not words:
            return {"lexicon_coverage": 0.0, "word_count": 0, "known_words": 0}
        
        known_words = sum(1 for word in words if word in self.lexicon)
        coverage = known_words / len(words)
        
        return {
            "lexicon_coverage": coverage,
            "word_count": len(words),
            "known_words": known_words
        }
    
    def enhance_ocr_result(self, text: str, original_confidence: float) -> Dict[str, Any]:
        """
        Enhance OCR result with Sesotho-specific corrections.
        
        Args:
            text: Raw OCR text
            original_confidence: Original OCR confidence score
            
        Returns:
            Dictionary with enhanced text and updated confidence
        """
        if not text.strip():
            return {
                "enhanced_text": text,
                "confidence": original_confidence,
                "enhancements_applied": [],
                "validation_metrics": {}
            }
        
        enhancements_applied = []
        enhanced_text = text
        
        # Step 1: Orthographic correction
        if self.config.enable_orthographic_correction:
            corrected_text = self.correct_orthography(enhanced_text)
            if corrected_text != enhanced_text:
                enhancements_applied.append("orthographic_correction")
                enhanced_text = corrected_text
        
        # Step 2: Diacritic restoration
        if self.config.enable_diacritic_restoration:
            restored_text = self.restore_diacritics(enhanced_text)
            if restored_text != enhanced_text:
                enhancements_applied.append("diacritic_restoration")
                enhanced_text = restored_text
        
        # Step 3: Validation and confidence adjustment
        validation_metrics = self.validate_against_lexicon(enhanced_text)
        
        # Adjust confidence based on lexicon coverage
        confidence_boost = 0.0
        if validation_metrics["lexicon_coverage"] > 0.5:  # More than 50% known words
            confidence_boost = validation_metrics["lexicon_coverage"] * self.config.confidence_boost_threshold
        
        enhanced_confidence = min(1.0, original_confidence + confidence_boost)
        
        return {
            "enhanced_text": enhanced_text,
            "confidence": enhanced_confidence,
            "enhancements_applied": enhancements_applied,
            "validation_metrics": validation_metrics,
            "confidence_boost": confidence_boost
        }
    
    def process_historical_document_batch(self, ocr_results_file: Path, 
                                        output_file: Path) -> Dict[str, Any]:
        """
        Process a batch of OCR results for historical Sesotho documents.
        
        Args:
            ocr_results_file: JSON file with OCR results
            output_file: Output file for enhanced results
            
        Returns:
            Processing statistics
        """
        with open(ocr_results_file, 'r', encoding='utf-8') as f:
            ocr_data = json.load(f)
        
        enhanced_results = []
        stats = {
            "processed": 0,
            "enhanced": 0,
            "total_confidence_improvement": 0.0,
            "average_lexicon_coverage": 0.0
        }
        
        for result in ocr_data.get("results", []):
            original_text = result.get("text", "")
            original_confidence = result.get("confidence", 0.0)
            
            # Enhance the result
            enhancement = self.enhance_ocr_result(original_text, original_confidence)
            
            # Prepare enhanced result
            enhanced_result = result.copy()
            enhanced_result.update({
                "original_text": original_text,
                "enhanced_text": enhancement["enhanced_text"],
                "original_confidence": original_confidence,
                "enhanced_confidence": enhancement["confidence"],
                "enhancements_applied": enhancement["enhancements_applied"],
                "validation_metrics": enhancement["validation_metrics"]
            })
            
            enhanced_results.append(enhanced_result)
            
            # Update statistics
            stats["processed"] += 1
            if enhancement["enhancements_applied"]:
                stats["enhanced"] += 1
            
            confidence_improvement = enhancement["confidence"] - original_confidence
            stats["total_confidence_improvement"] += confidence_improvement
            
            coverage = enhancement["validation_metrics"].get("lexicon_coverage", 0.0)
            stats["average_lexicon_coverage"] += coverage
        
        # Finalize statistics
        if stats["processed"] > 0:
            stats["average_confidence_improvement"] = stats["total_confidence_improvement"] / stats["processed"]
            stats["average_lexicon_coverage"] /= stats["processed"]
        
        # Save enhanced results
        enhanced_data = ocr_data.copy()
        enhanced_data["results"] = enhanced_results
        enhanced_data["enhancement_stats"] = stats
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(enhanced_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Enhanced {stats['enhanced']}/{stats['processed']} results")
        logger.info(f"Average confidence improvement: {stats.get('average_confidence_improvement', 0):.3f}")
        logger.info(f"Average lexicon coverage: {stats['average_lexicon_coverage']:.3f}")
        
        return stats


def main():
    """Command-line interface for Sesotho OCR enhancement."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhance OCR results for Sesotho text")
    parser.add_argument("input_file", help="JSON file with OCR results")
    parser.add_argument("-o", "--output", help="Output file for enhanced results")
    parser.add_argument("--dictionary", help="Path to Sesotho lexicon JSON")
    parser.add_argument("--disable-orthography", action="store_true",
                       help="Disable orthographic correction")
    parser.add_argument("--disable-diacritics", action="store_true", 
                       help="Disable diacritic restoration")
    
    args = parser.parse_args()
    
    # Configure enhancer
    config = SesothoOCRConfig(
        enable_orthographic_correction=not args.disable_orthography,
        enable_diacritic_restoration=not args.disable_diacritics,
        dictionary_path=args.dictionary or "data/lexicon.json"
    )
    
    enhancer = SesothoOCREnhancer(config)
    
    input_file = Path(args.input_file)
    output_file = Path(args.output) if args.output else input_file.with_suffix('.enhanced.json')
    
    stats = enhancer.process_historical_document_batch(input_file, output_file)
    
    print(f"Enhancement complete:")
    print(f"  Processed: {stats['processed']} files")
    print(f"  Enhanced: {stats['enhanced']} files")
    print(f"  Average confidence improvement: {stats.get('average_confidence_improvement', 0):.3f}")
    print(f"  Average lexicon coverage: {stats['average_lexicon_coverage']:.3f}")


if __name__ == "__main__":
    main()
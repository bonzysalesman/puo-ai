#!/usr/bin/env python3
"""
Enhanced OCR Stack for PUO-AI
Provides a unified interface for multiple OCR engines including Tesseract and Surya.
Supports 90+ languages with intelligent engine selection and quality assessment.
"""

import json
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import argparse
import sys
from dataclasses import dataclass
from enum import Enum
import logging
from .sesotho_ocr_enhancer import SesothoOCREnhancer, SesothoOCRConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# PDF support
try:
    import fitz  # PyMuPDF
    from PIL import Image
    PDF_SUPPORT = True
except ImportError:
    logger.warning("PDF support not available - install PyMuPDF and PIL")
    PDF_SUPPORT = False


class OCREngine(Enum):
    TESSERACT = "tesseract"
    SURYA = "surya"
    HYBRID = "hybrid"


@dataclass
class OCRResult:
    """Represents the result of an OCR operation."""
    text: str
    confidence: float
    engine_used: str
    metadata: Dict[str, Any]
    layout_info: Optional[Dict[str, Any]] = None


@dataclass
class OCRConfig:
    """Configuration for OCR operations."""
    primary_engine: OCREngine = OCREngine.TESSERACT
    fallback_engine: Optional[OCREngine] = None
    languages: List[str] = None
    confidence_threshold: float = 0.7
    enable_layout_analysis: bool = True
    enable_reading_order: bool = True
    enable_enhancement: bool = True

    def __post_init__(self):
        # Default to eng+fra for historical Sesotho/French sources (Casalis,
        # Mabille, Jacottet, Paroz). Modern Bible corpora (JW/NKJV) should
        # override with languages=["eng"] via CLI or caller. Audited 2026-06-23:
        # eng+fra added 2 additional real headwords (Against, Agility) per 3
        # sample pages over eng-only, with zero new true-noise tokens.
        if self.languages is None:
            self.languages = ["eng", "fra"]


# Backwards-compatible constant for callers that imported the previous literal
DEFAULT_LANGUAGES = ["eng", "fra"]


def _historical_default_languages() -> List[str]:
    """Return the default OCR language list for historical Sesotho sources."""
    return list(DEFAULT_LANGUAGES)


class EnhancedOCRStack:
    """
    Enhanced OCR Stack that provides unified access to multiple OCR engines.
    
    Features:
    - Multi-engine support (Tesseract, Surya, future engines)
    - Intelligent engine selection based on document type
    - Quality assessment and confidence scoring
    - Layout analysis and reading order detection
    - Language-specific optimizations
    """
    
    def __init__(self, config: OCRConfig = None):
        self.config = config or OCRConfig()
        self.available_engines = self._detect_available_engines()
        self.enhancer = SesothoOCREnhancer(SesothoOCRConfig())
        logger.info(f"Initialized OCR stack with engines: {self.available_engines}")
    
    def _detect_available_engines(self) -> List[str]:
        """Detect which OCR engines are available on the system."""
        available = []
        
        # Check Tesseract
        try:
            result = subprocess.run(["tesseract", "--version"], 
                                 capture_output=True, text=True)
            if result.returncode == 0:
                available.append("tesseract")
                logger.info(f"Tesseract detected: {result.stdout.split()[1]}")
        except FileNotFoundError:
            logger.warning("Tesseract not found")
        
        # Check Surya
        try:
            import surya
            # Test basic import to see if it works with current Python version
            import sys
            if sys.version_info >= (3, 10):
                from surya.detection import DetectionPredictor
                from surya.recognition import RecognitionPredictor
                available.append("surya")
                logger.info("Surya OCR detected and fully available")
            else:
                available.append("surya")
                logger.warning(f"Surya OCR detected but limited functionality (Python {sys.version_info.major}.{sys.version_info.minor} < 3.10)")
        except ImportError:
            logger.warning("Surya OCR not available - install with: pip install surya-ocr")
        except Exception as e:
            logger.warning(f"Surya OCR installed but not functional: {e}")
        
        return available
    
    def get_tesseract_languages(self) -> List[str]:
        """Get list of available Tesseract languages."""
        try:
            result = subprocess.run(["tesseract", "--list-langs"], 
                                 capture_output=True, text=True)
            if result.returncode == 0:
                langs = result.stdout.strip().split('\n')[1:]  # Skip header
                return [lang.strip() for lang in langs if lang.strip()]
        except (FileNotFoundError, subprocess.SubprocessError):
            return []
        return []
    
    def ocr_with_tesseract(self, image_path: Path, languages: List[str] = None) -> OCRResult:
        """Perform OCR using Tesseract."""
        if "tesseract" not in self.available_engines:
            raise RuntimeError("Tesseract not available")
        
        # Default to English if no languages specified
        lang_param = "+".join(languages) if languages else "eng"
        
        try:
            # Basic OCR
            result = subprocess.run([
                "tesseract", str(image_path), "stdout", 
                "-l", lang_param
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                raise RuntimeError(f"Tesseract failed: {result.stderr}")
            
            text = result.stdout.strip()
            
            # Get confidence score if available (TSV output)
            confidence_result = subprocess.run([
                "tesseract", str(image_path), "stdout", 
                "-l", lang_param, "--psm", "6", "-c", "tessedit_create_tsv=1"
            ], capture_output=True, text=True)
            
            confidence = self._parse_tesseract_confidence(confidence_result.stdout)
            
            return OCRResult(
                text=text,
                confidence=confidence,
                engine_used="tesseract",
                metadata={
                    "languages": languages or ["eng"],
                    "psm_mode": "6"
                }
            )
            
        except Exception as e:
            logger.error(f"Tesseract OCR failed for {image_path}: {e}")
            return OCRResult("", 0.0, "tesseract", {"error": str(e)})
    
    def ocr_with_surya(self, image_path: Path) -> OCRResult:
        """Perform OCR using Surya (if available)."""
        if "surya" not in self.available_engines:
            raise RuntimeError("Surya not available")
        
        try:
            # Check Python version compatibility
            import sys
            if sys.version_info < (3, 10):
                logger.warning("Surya OCR requires Python 3.10+ for full functionality. Using fallback approach.")
                # Use a basic extraction approach for older Python versions
                from PIL import Image
                
                # For now, return a placeholder result indicating Surya is installed but needs Python 3.10+
                return OCRResult(
                    text="[Surya OCR available but requires Python 3.10+ for full functionality]",
                    confidence=0.0,
                    engine_used="surya_fallback",
                    metadata={
                        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
                        "surya_installed": True,
                        "requires_upgrade": "Python 3.10+"
                    }
                )
            
            # For Python 3.10+, use full Surya functionality with v0.20+ API
            from surya.recognition import RecognitionPredictor
            from PIL import Image
            
            # Load image
            image = Image.open(image_path)
            
            # Initialize recognition predictor (uses full-page OCR by default)
            predictor = RecognitionPredictor()
            
            # Perform OCR (full-page mode for better accuracy)
            ocr_results = predictor([image], full_page=True)
            
            # Extract text and confidence from blocks
            text_lines = []
            confidences = []
            
            if ocr_results and len(ocr_results) > 0:
                page_result = ocr_results[0]
                # Sort blocks by reading order
                sorted_blocks = sorted(page_result.blocks, key=lambda b: b.reading_order)
                
                for block in sorted_blocks:
                    if not block.skipped and not block.error and block.html:
                        # Extract plain text from HTML
                        import re
                        text = re.sub('<[^<]+?>', '', block.html)  # Strip HTML tags
                        text = text.strip()
                        if text:
                            text_lines.append(text)
                            confidences.append(getattr(block, 'confidence', 0.8))
            
            full_text = "\n".join(text_lines)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            return OCRResult(
                text=full_text,
                confidence=avg_confidence,
                engine_used="surya",
                metadata={
                    "surya_version": "0.20+",
                    "blocks_processed": len(ocr_results[0].blocks) if ocr_results else 0,
                    "text_blocks_found": len(text_lines),
                    "full_page_mode": True
                }
            )
            
        except Exception as e:
            logger.error(f"Surya OCR failed for {image_path}: {e}")
            return OCRResult("", 0.0, "surya", {"error": str(e)})
    
    def _convert_pdf_to_images(self, pdf_path: Path) -> List[Path]:
        """Convert PDF pages to images for OCR processing."""
        if not PDF_SUPPORT:
            raise RuntimeError("PDF support not available - install PyMuPDF")
        
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        
        # Create temporary directory for images
        temp_dir = pdf_path.parent / f"{pdf_path.stem}_images"
        temp_dir.mkdir(exist_ok=True)
        
        try:
            doc = fitz.open(pdf_path)
            image_paths = []
            
            logger.info(f"Converting {len(doc)} pages from PDF to images")
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # Get page as image (high DPI for better OCR)
                mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for higher resolution
                pix = page.get_pixmap(matrix=mat)
                
                # Save as PNG
                image_path = temp_dir / f"page_{page_num + 1:03d}.png"
                pix.save(str(image_path))
                image_paths.append(image_path)
            
            doc.close()
            logger.info(f"Converted PDF to {len(image_paths)} images in {temp_dir}")
            return image_paths
            
        except Exception as e:
            logger.error(f"Failed to convert PDF {pdf_path}: {e}")
            raise
    
    def _is_pdf(self, file_path: Path) -> bool:
        """Check if the file is a PDF."""
        return file_path.suffix.lower() == '.pdf'

    def _parse_tesseract_confidence(self, tsv_output: str) -> float:
        """Parse confidence score from Tesseract TSV output."""
        if not tsv_output.strip():
            return 0.0
        
        lines = tsv_output.strip().split('\n')
        if len(lines) < 2:  # Header + at least one data line
            return 0.0
        
        confidences = []
        for line in lines[1:]:  # Skip header
            parts = line.split('\t')
            if len(parts) >= 11 and parts[10].strip() != '-1':  # conf column
                try:
                    conf = float(parts[10])
                    if conf > 0:  # Valid confidence
                        confidences.append(conf)
                except ValueError:
                    continue
        
        return sum(confidences) / len(confidences) / 100.0 if confidences else 0.0
    
    def ocr_document(self, file_path: Path, config_override: OCRConfig = None) -> OCRResult:
        """
        Perform OCR on a document (image or PDF) using the best available engine.
        
        Args:
            file_path: Path to the image or PDF file
            config_override: Optional configuration override
            
        Returns:
            OCRResult with text, confidence, and metadata
        """
        config = config_override or self.config
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Handle PDF files
        if self._is_pdf(file_path):
            logger.info(f"Processing PDF: {file_path}")
            
            try:
                image_paths = self._convert_pdf_to_images(file_path)
                
                # Process all pages and combine results
                all_text = []
                all_confidences = []
                
                for i, image_path in enumerate(image_paths, 1):
                    logger.info(f"Processing page {i}/{len(image_paths)}")
                    
                    page_result = self._ocr_image(image_path, config)
                    all_text.append(f"--- Page {i} ---")
                    all_text.append(page_result.text)
                    all_confidences.append(page_result.confidence)
                
                combined_text = "\n".join(all_text)
                avg_confidence = sum(all_confidences) / len(all_confidences) if all_confidences else 0.0
                
                return OCRResult(
                    text=combined_text,
                    confidence=avg_confidence,
                    engine_used=all_confidences[0] if all_confidences else "unknown",
                    metadata={
                        "file_type": "pdf",
                        "pages_processed": len(image_paths),
                        "source_pdf": str(file_path),
                        "page_confidences": all_confidences
                    }
                )
                
            except Exception as e:
                logger.error(f"Failed to process PDF {file_path}: {e}")
                return OCRResult("", 0.0, "error", {"error": str(e)})
        else:
            # Handle image files
            return self._ocr_image(file_path, config)
    
    def _ocr_image(self, image_path: Path, config: OCRConfig) -> OCRResult:
        """
        Perform OCR on a single image using the configured engine.
        
        Args:
            image_path: Path to the image file
            config: OCR configuration
            
        Returns:
            OCRResult with text, confidence, and metadata
        """
        
        # Determine which engine to use
        primary_engine = config.primary_engine.value
        
        # Try primary engine
        if primary_engine == "surya" and "surya" in self.available_engines:
            result = self.ocr_with_surya(image_path)
        elif primary_engine == "tesseract" and "tesseract" in self.available_engines:
            result = self.ocr_with_tesseract(image_path, config.languages)
        else:
            # Fallback to available engine
            if "surya" in self.available_engines:
                result = self.ocr_with_surya(image_path)
            elif "tesseract" in self.available_engines:
                result = self.ocr_with_tesseract(image_path, config.languages)
            else:
                raise RuntimeError("No OCR engines available")
        
        # Check if we should try fallback
        if (result.confidence < config.confidence_threshold and 
            config.fallback_engine and 
            config.fallback_engine.value in self.available_engines and
            config.fallback_engine.value != primary_engine):
            
            logger.info(f"Primary engine confidence {result.confidence:.2f} below threshold, trying fallback")
            
            if config.fallback_engine.value == "surya":
                fallback_result = self.ocr_with_surya(image_path)
            else:
                fallback_result = self.ocr_with_tesseract(image_path, config.languages)
            
            # Return better result
            if fallback_result.confidence > result.confidence:
                fallback_result.metadata["fallback_from"] = primary_engine
                result = fallback_result
        
        # Apply enhancement if enabled
        if config.enable_enhancement and result.text.strip():
            try:
                enhancement = self.enhancer.enhance_ocr_result(result.text, result.confidence)
                result.text = enhancement["enhanced_text"]
                result.confidence = enhancement["confidence"]
                result.metadata["enhancements_applied"] = enhancement["enhancements_applied"]
            except Exception as e:
                logger.warning(f"Enhancement failed: {e}")
        
        return result
    
    def batch_ocr_directory(self, input_dir: Path, output_file: Path, 
                           pattern: str = "*.*", config_override: OCRConfig = None) -> Dict[str, Any]:
        """
        Perform batch OCR on all files (images and PDFs) in a directory.
        
        Args:
            input_dir: Directory containing images and PDFs
            output_file: Output JSON file for results
            pattern: File pattern to match (default: *.*)
            config_override: Optional configuration override
            
        Returns:
            Summary statistics
        """
        input_dir = Path(input_dir)
        output_file = Path(output_file)
        
        if not input_dir.exists():
            raise FileNotFoundError(f"Input directory not found: {input_dir}")
        
        # Find all matching files (images and PDFs)
        all_files = list(input_dir.glob(pattern))
        # Filter for supported file types
        supported_extensions = {'.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif', '.pdf'}
        files = [f for f in all_files if f.suffix.lower() in supported_extensions]
        
        if not files:
            logger.warning(f"No supported files found matching pattern: {pattern}")
            return {"processed": 0, "errors": 0}
        
        results = []
        errors = 0
        
        logger.info(f"Processing {len(files)} files...")
        
        for i, file_path in enumerate(files, 1):
            logger.info(f"Processing {i}/{len(files)}: {file_path.name}")
            
            try:
                ocr_result = self.ocr_document(file_path, config_override)
                
                results.append({
                    "source_file": str(file_path.relative_to(input_dir)),
                    "text": ocr_result.text,
                    "confidence": ocr_result.confidence,
                    "engine_used": ocr_result.engine_used,
                    "metadata": ocr_result.metadata,
                    "layout_info": ocr_result.layout_info
                })
                
            except Exception as e:
                logger.error(f"Failed to process {file_path}: {e}")
                results.append({
                    "source_file": str(file_path.relative_to(input_dir)),
                    "text": "",
                    "confidence": 0.0,
                    "engine_used": "none",
                    "metadata": {"error": str(e)}
                })
                errors += 1
        
        # Save results
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                "metadata": {
                    "total_files": len(files),
                    "processed": len(results),
                    "errors": errors,
                    "config": {
                        "primary_engine": config_override.primary_engine.value if config_override else self.config.primary_engine.value,
                        "languages": config_override.languages if config_override else self.config.languages
                    }
                },
                "results": results
            }, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Batch processing complete. Results saved to {output_file}")
        
        return {
            "processed": len(results),
            "errors": errors,
            "output_file": str(output_file)
        }


def main():
    """Command-line interface for the Enhanced OCR Stack."""
    parser = argparse.ArgumentParser(description="Enhanced OCR Stack for PUO-AI")
    parser.add_argument("input_path", help="Input image file, PDF file, or directory")
    parser.add_argument("-o", "--output", help="Output file (JSON for batch, text for single)")
    parser.add_argument("-e", "--engine", choices=["tesseract", "surya", "hybrid"], 
                       default="tesseract", help="OCR engine to use")
    parser.add_argument("-l", "--languages", nargs="+", 
                       help="Languages for OCR (e.g., eng st)")
    parser.add_argument("--pattern", default="*.*", 
                       help="File pattern for batch processing")
    parser.add_argument("--confidence-threshold", type=float, default=0.7,
                       help="Confidence threshold for fallback")
    parser.add_argument("--list-engines", action="store_true",
                       help="List available OCR engines and exit")
    
    args = parser.parse_args()
    
    # Create OCR stack
    ocr_stack = EnhancedOCRStack()
    
    if args.list_engines:
        print("Available OCR engines:")
        for engine in ocr_stack.available_engines:
            print(f"  - {engine}")
        
        print("\nTesseract languages:")
        for lang in ocr_stack.get_tesseract_languages():
            print(f"  - {lang}")
        
        return
    
    # Configure OCR
    config = OCRConfig(
        primary_engine=OCREngine(args.engine),
        languages=args.languages,
        confidence_threshold=args.confidence_threshold
    )
    
    input_path = Path(args.input_path)
    
    if input_path.is_file():
        # Single file processing
        result = ocr_stack.ocr_document(input_path, config)
        
        if args.output:
            output_path = Path(args.output)
            if output_path.suffix == '.json':
                with open(output_path, 'w') as f:
                    json.dump({
                        "text": result.text,
                        "confidence": result.confidence,
                        "engine_used": result.engine_used,
                        "metadata": result.metadata
                    }, f, indent=2)
            else:
                with open(output_path, 'w') as f:
                    f.write(result.text)
        else:
            print(result.text)
        
        print(f"\nConfidence: {result.confidence:.2f}, Engine: {result.engine_used}", 
              file=sys.stderr)
    
    elif input_path.is_dir():
        # Batch processing
        output_file = Path(args.output) if args.output else input_path / "ocr_results.json"
        
        stats = ocr_stack.batch_ocr_directory(input_path, output_file, args.pattern, config)
        print(f"Processed {stats['processed']} files with {stats['errors']} errors")
    
    else:
        print(f"Error: {input_path} is not a valid file or directory", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
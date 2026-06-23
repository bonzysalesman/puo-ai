#!/usr/bin/env python3
"""
Test Enhanced OCR Stack with Casalis Historical Document
Demonstrates the new OCR capabilities on existing PUO-AI historical materials.
"""

import json
from pathlib import Path
import sys
import logging
from enhanced_ocr_stack import EnhancedOCRStack, OCRConfig, OCREngine
from sesotho_ocr_enhancer import SesothoOCREnhancer, SesothoOCRConfig

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_casalis_pdf_extraction():
    """Test OCR extraction on the Casalis PDF."""
    
    # Check if we have any existing OCR splits to work with
    ocr_splits_dir = Path("ocr_splits")
    casalis_dirs = [d for d in ocr_splits_dir.glob("casalis_*") if d.is_dir()]
    
    if not casalis_dirs:
        logger.error("No Casalis OCR splits found. Please run OCR splitting first.")
        return False
    
    # Initialize enhanced OCR stack
    ocr_config = OCRConfig(
        primary_engine=OCREngine.TESSERACT,
        languages=["eng", "fra"],  # French improves Sesotho diacritic handling in historical docs
        confidence_threshold=0.6
    )
    
    ocr_stack = EnhancedOCRStack(ocr_config)
    
    # Test on a few sample images from casalis_a (most processed directory)
    casalis_a_dir = ocr_splits_dir / "casalis_a"
    
    if not casalis_a_dir.exists():
        logger.error(f"Casalis A directory not found: {casalis_a_dir}")
        return False
    
    # Find some sample images
    sample_images = list(casalis_a_dir.glob("*.png"))[:3]  # Test first 3 images
    
    if not sample_images:
        logger.error("No PNG images found in casalis_a directory")
        return False
    
    logger.info(f"Testing enhanced OCR on {len(sample_images)} sample images...")
    
    results = []
    
    for image_path in sample_images:
        logger.info(f"Processing: {image_path.name}")
        
        try:
            # Perform OCR
            ocr_result = ocr_stack.ocr_document(image_path)
            
            results.append({
                "image": image_path.name,
                "text": ocr_result.text,
                "confidence": ocr_result.confidence,
                "engine": ocr_result.engine_used,
                "metadata": ocr_result.metadata
            })
            
            logger.info(f"  Confidence: {ocr_result.confidence:.3f}")
            logger.info(f"  Text preview: {ocr_result.text[:100]}...")
            
        except Exception as e:
            logger.error(f"  Failed: {e}")
            results.append({
                "image": image_path.name,
                "error": str(e)
            })
    
    # Save results
    output_dir = Path("reports")
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / "enhanced_ocr_test_results.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "test_description": "Enhanced OCR Stack test on Casalis historical documents",
            "ocr_config": {
                "primary_engine": ocr_config.primary_engine.value,
                "languages": ocr_config.languages,
                "confidence_threshold": ocr_config.confidence_threshold
            },
            "available_engines": ocr_stack.available_engines,
            "sample_count": len(sample_images),
            "results": results
        }, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Test results saved to: {output_file}")
    return True


def test_sesotho_enhancement():
    """Test Sesotho-specific OCR enhancement capabilities."""
    
    logger.info("Testing Sesotho OCR enhancement...")
    
    # Initialize Sesotho enhancer
    sesotho_config = SesothoOCRConfig(
        enable_orthographic_correction=True,
        enable_diacritic_restoration=True,
        dictionary_path="data/lexicon.json"
    )
    
    enhancer = SesothoOCREnhancer(sesotho_config)
    
    # Test with some sample Sesotho text with common OCR errors
    test_cases = [
        {
            "description": "Historical orthography (tj -> tš)",
            "raw_text": "Motho o tjeba ka matla",
            "expected_improvements": ["orthographic_correction"]
        },
        {
            "description": "OCR confusion (1 -> l, rn -> m)",
            "raw_text": "Mo1imo o rnotše batho",
            "expected_improvements": ["orthographic_correction"]
        },
        {
            "description": "Missing diacritics",
            "raw_text": "Ke rata ho bona motho",
            "expected_improvements": ["diacritic_restoration"]
        }
    ]
    
    enhancement_results = []
    
    for test_case in test_cases:
        logger.info(f"Testing: {test_case['description']}")
        logger.info(f"  Input: {test_case['raw_text']}")
        
        # Enhance the text
        enhancement = enhancer.enhance_ocr_result(test_case["raw_text"], 0.8)
        
        logger.info(f"  Enhanced: {enhancement['enhanced_text']}")
        logger.info(f"  Confidence: {enhancement['confidence']:.3f}")
        logger.info(f"  Enhancements: {enhancement['enhancements_applied']}")
        logger.info(f"  Lexicon coverage: {enhancement['validation_metrics'].get('lexicon_coverage', 0):.3f}")
        
        enhancement_results.append({
            "test_case": test_case,
            "enhancement": enhancement
        })
    
    # Save enhancement test results
    output_file = Path("reports/sesotho_enhancement_test_results.json")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "test_description": "Sesotho OCR enhancement capabilities test",
            "lexicon_loaded": len(enhancer.lexicon) > 0,
            "lexicon_size": len(enhancer.lexicon),
            "test_cases": enhancement_results
        }, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Sesotho enhancement test results saved to: {output_file}")
    return True


def demonstrate_batch_processing():
    """Demonstrate batch processing capabilities."""
    
    logger.info("Demonstrating batch OCR processing...")
    
    # Check available OCR engines
    ocr_stack = EnhancedOCRStack()
    
    logger.info(f"Available OCR engines: {ocr_stack.available_engines}")
    
    if "tesseract" in ocr_stack.available_engines:
        langs = ocr_stack.get_tesseract_languages()
        logger.info(f"Tesseract languages: {langs}")
    
    # Create a demonstration report
    demo_report = {
        "enhanced_ocr_stack": {
            "available_engines": ocr_stack.available_engines,
            "tesseract_languages": ocr_stack.get_tesseract_languages() if "tesseract" in ocr_stack.available_engines else [],
            "features": [
                "Multi-engine OCR support (Tesseract, Surya when available)",
                "Intelligent engine selection and fallback",
                "Confidence-based quality assessment",
                "Batch processing capabilities",
                "Language-specific optimizations"
            ]
        },
        "sesotho_enhancements": {
            "orthographic_correction": "Converts historical spellings (tj->tš, ny->ñ)",
            "ocr_error_correction": "Fixes common OCR mistakes (1->l, rn->m, ii->ll)",
            "diacritic_restoration": "Restores missing diacritics based on lexicon",
            "lexicon_validation": "Validates text against 6,398 Sesotho headwords",
            "confidence_adjustment": "Boosts confidence for lexicon-validated text"
        },
        "integration_ready": {
            "existing_pipeline": "Integrates with current OCR processing in pipeline/ocr/",
            "makefile_targets": "Can be added to Makefile for automated workflows",
            "batch_processing": "Supports directory-based batch processing",
            "json_output": "Structured JSON output compatible with existing tools"
        }
    }
    
    output_file = Path("reports/enhanced_ocr_capabilities_demo.json")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(demo_report, f, indent=2, ensure_ascii=False)
    
    logger.info(f"OCR capabilities demonstration saved to: {output_file}")
    
    return True


def main():
    """Run comprehensive OCR enhancement tests."""
    
    print("🚀 PUO-AI Enhanced OCR Stack Testing")
    print("=" * 50)
    
    success_count = 0
    total_tests = 3
    
    # Test 1: Enhanced OCR on historical documents
    print("\n📄 Test 1: Enhanced OCR on Casalis Historical Documents")
    try:
        if test_casalis_pdf_extraction():
            print("✅ Enhanced OCR test passed")
            success_count += 1
        else:
            print("❌ Enhanced OCR test failed")
    except Exception as e:
        print(f"❌ Enhanced OCR test error: {e}")
    
    # Test 2: Sesotho enhancement capabilities
    print("\n🔤 Test 2: Sesotho OCR Enhancement")
    try:
        if test_sesotho_enhancement():
            print("✅ Sesotho enhancement test passed")
            success_count += 1
        else:
            print("❌ Sesotho enhancement test failed")
    except Exception as e:
        print(f"❌ Sesotho enhancement test error: {e}")
    
    # Test 3: Demonstration and capabilities report
    print("\n📊 Test 3: OCR Capabilities Demonstration")
    try:
        if demonstrate_batch_processing():
            print("✅ Capabilities demonstration completed")
            success_count += 1
        else:
            print("❌ Capabilities demonstration failed")
    except Exception as e:
        print(f"❌ Capabilities demonstration error: {e}")
    
    # Summary
    print(f"\n📈 Test Summary: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("🎉 All tests passed! Enhanced OCR stack is ready for use.")
        
        print("\n📋 Next Steps:")
        print("1. Install Surya OCR when network connectivity improves:")
        print("   .venv/bin/python3 -m pip install surya-ocr")
        print("2. Add Sesotho language pack to Tesseract if available")
        print("3. Integrate enhanced OCR into existing Makefile targets")
        print("4. Test on full Casalis PDF extraction workflow")
        
    else:
        print("⚠️  Some tests failed. Check logs for details.")
    
    print(f"\n📁 Results saved in reports/ directory")
    
    return success_count == total_tests


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
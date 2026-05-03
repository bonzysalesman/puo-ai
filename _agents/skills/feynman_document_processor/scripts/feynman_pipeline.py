#!/usr/bin/env python3
"""
Feynman Technique Document Processor
Implements 4-step Feynman method with BMAD agent integration
"""

import json
import argparse
import os
from pathlib import Path
from typing import Dict, List, Any
import subprocess
import tempfile

class FeynmanProcessor:
    """
    Lightweight Feynman technique processor inspired by nanoclaw's 
    modular approach but using existing BMAD infrastructure
    """
    
    def __init__(self, bmad_path="_bmad"):
        self.bmad_path = bmad_path
        self.agents = {
            'analyst': 'bmad-agent-bmm-analyst',
            'storyteller': 'bmad-agent-cis-storyteller', 
            'qa': 'bmad-agent-bmm-qa',
            'tech_writer': 'bmad-agent-bmm-tech-writer'
        }
    
    def step1_learn(self, document_path: str) -> Dict[str, Any]:
        """
        Step 1: Learn - Extract and understand core concepts
        Uses BMAD Analyst for domain research and concept identification
        """
        print("🧠 Step 1: Learn - Extracting concepts...")
        
        # Read document content
        content = self._read_document(document_path)
        
        # Create analyst prompt
        analyst_prompt = f"""
        Analyze this document and extract the core concepts that need explanation.
        Focus on:
        1. Key terminology and definitions
        2. Complex processes or relationships  
        3. Domain-specific knowledge
        4. Concepts that would be difficult for a general audience
        
        Document content:
        {content[:2000]}...
        
        Output as JSON with: concepts, definitions, complexity_areas, prerequisites
        """
        
        # Use BMAD analyst (would integrate with actual BMAD CLI)
        concepts = self._call_bmad_agent('analyst', analyst_prompt)
        
        return {
            'source_document': document_path,
            'concepts': concepts,
            'step': 1,
            'status': 'completed'
        }
    
    def step2_explain(self, concepts_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Step 2: Explain - Create simple explanations using analogies
        Uses BMAD Storyteller for narrative clarity
        """
        print("📖 Step 2: Explain - Creating simple explanations...")
        
        storyteller_prompt = f"""
        Take these complex concepts and explain them as if teaching a curious 12-year-old.
        Use analogies, metaphors, and simple language.
        
        Concepts to explain:
        {json.dumps(concepts_data.get('concepts', {}), indent=2)}
        
        For each concept, provide:
        1. Simple explanation (1-2 sentences)
        2. Analogy or metaphor
        3. Real-world example
        4. Why it matters
        
        Make it engaging and memorable!
        """
        
        explanations = self._call_bmad_agent('storyteller', storyteller_prompt)
        
        return {
            **concepts_data,
            'explanations': explanations,
            'step': 2,
            'status': 'completed'
        }
    
    def step3_identify_gaps(self, explanations_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Step 3: Identify Gaps - Find unclear areas and missing information
        Uses BMAD QA Engineer for systematic gap analysis
        """
        print("🔍 Step 3: Identify Gaps - Finding unclear areas...")
        
        qa_prompt = f"""
        Review these explanations for clarity and completeness.
        Identify:
        1. Concepts that are still too complex
        2. Missing prerequisite knowledge
        3. Unclear analogies or examples
        4. Logical gaps in the explanation flow
        5. Areas needing visual aids or diagrams
        
        Original concepts:
        {json.dumps(explanations_data.get('concepts', {}), indent=2)}
        
        Current explanations:
        {json.dumps(explanations_data.get('explanations', {}), indent=2)}
        
        Provide specific, actionable feedback for improvement.
        """
        
        gap_analysis = self._call_bmad_agent('qa', qa_prompt)
        
        return {
            **explanations_data,
            'gap_analysis': gap_analysis,
            'step': 3,
            'status': 'completed'
        }
    
    def step4_simplify(self, gap_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Step 4: Simplify - Refine explanations and create final documentation
        Uses BMAD Tech Writer for documentation polish
        """
        print("✨ Step 4: Simplify - Creating final documentation...")
        
        tech_writer_prompt = f"""
        Create polished, accessible documentation based on this analysis.
        
        Original concepts: {json.dumps(gap_data.get('concepts', {}), indent=2)}
        Draft explanations: {json.dumps(gap_data.get('explanations', {}), indent=2)}
        Gap analysis: {json.dumps(gap_data.get('gap_analysis', {}), indent=2)}
        
        Create:
        1. Progressive explanations (simple → intermediate → advanced)
        2. Visual concept maps (Mermaid diagrams where helpful)
        3. Structured documentation with clear headings
        4. Examples and use cases
        5. Cross-references and related concepts
        
        Follow documentation standards and ensure accessibility.
        Output as structured markdown.
        """
        
        final_documentation = self._call_bmad_agent('tech_writer', tech_writer_prompt)
        
        return {
            **gap_data,
            'final_documentation': final_documentation,
            'step': 4,
            'status': 'completed'
        }
    
    def process_document(self, document_path: str, output_path: str = None) -> Dict[str, Any]:
        """
        Run complete Feynman pipeline on a document
        """
        print(f"🚀 Starting Feynman processing for: {document_path}")
        
        # Step 1: Learn
        step1_result = self.step1_learn(document_path)
        
        # Step 2: Explain  
        step2_result = self.step2_explain(step1_result)
        
        # Step 3: Identify Gaps
        step3_result = self.step3_identify_gaps(step2_result)
        
        # Step 4: Simplify
        final_result = self.step4_simplify(step3_result)
        
        # Save results
        if output_path:
            self._save_results(final_result, output_path)
        
        print("✅ Feynman processing completed!")
        return final_result
    
    def _read_document(self, document_path: str) -> str:
        """Read document content (supports text, JSON, basic PDF)"""
        path = Path(document_path)
        
        if path.suffix.lower() == '.json':
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return json.dumps(data, indent=2)
        elif path.suffix.lower() in ['.txt', '.md']:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            # For PDFs, use existing OCR pipeline
            return f"[Document: {document_path}] - Use OCR pipeline for full extraction"
    
    def _call_bmad_agent(self, agent_type: str, prompt: str) -> Dict[str, Any]:
        """
        Simulate BMAD agent call - in real implementation, this would
        integrate with your BMAD CLI or API
        """
        # For now, return structured placeholder
        # In real implementation: subprocess.run([bmad_cli, agent_type, prompt])
        
        agent_responses = {
            'analyst': {
                'concepts': ['morphology', 'noun_classes', 'tone_patterns'],
                'definitions': {'morphology': 'word structure analysis'},
                'complexity_areas': ['linguistic_terminology', 'bantu_grammar'],
                'prerequisites': ['basic_grammar', 'phonetics']
            },
            'storyteller': {
                'morphology': {
                    'simple_explanation': 'Words are like LEGO buildings - made of smaller pieces',
                    'analogy': 'Root word = foundation, prefixes/suffixes = add-on blocks',
                    'example': 'unhappiness = un- (not) + happy + -ness (thing)',
                    'why_matters': 'Helps you understand new words without a dictionary'
                }
            },
            'qa': {
                'gaps_found': ['need_visual_diagram', 'missing_examples', 'too_technical'],
                'improvements': ['add_step_by_step_breakdown', 'more_analogies'],
                'clarity_score': 7
            },
            'tech_writer': {
                'documentation': '# Understanding Word Structure\n\n## Simple Version\nWords are built from pieces...',
                'diagrams': ['word_structure_diagram.mermaid'],
                'cross_references': ['related_concepts']
            }
        }
        
        return agent_responses.get(agent_type, {'response': 'Agent response placeholder'})
    
    def _save_results(self, results: Dict[str, Any], output_path: str):
        """Save processing results to file"""
        output_file = Path(output_path)
        
        if output_file.suffix.lower() == '.json':
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
        else:
            # Save as markdown
            markdown_content = self._format_as_markdown(results)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
    
    def _format_as_markdown(self, results: Dict[str, Any]) -> str:
        """Format results as readable markdown"""
        md = f"""# Feynman Analysis: {results.get('source_document', 'Document')}

## Processing Summary
- **Steps Completed**: {results.get('step', 0)}/4
- **Status**: {results.get('status', 'unknown')}

## Final Documentation
{results.get('final_documentation', {}).get('documentation', 'No documentation generated')}

## Processing Details

### Concepts Identified
{json.dumps(results.get('concepts', {}), indent=2)}

### Explanations Generated  
{json.dumps(results.get('explanations', {}), indent=2)}

### Gap Analysis
{json.dumps(results.get('gap_analysis', {}), indent=2)}

---
*Generated by Feynman Document Processor*
"""
        return md

def main():
    parser = argparse.ArgumentParser(description='Process documents using Feynman Technique')
    parser.add_argument('document', help='Path to document to process')
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--format', choices=['json', 'markdown'], default='markdown')
    parser.add_argument('--bmad-path', default='_bmad', help='Path to BMAD installation')
    
    args = parser.parse_args()
    
    # Initialize processor
    processor = FeynmanProcessor(bmad_path=args.bmad_path)
    
    # Set output path
    if not args.output:
        input_path = Path(args.document)
        args.output = f"reports/feynman_{input_path.stem}.{args.format}"
    
    # Process document
    results = processor.process_document(args.document, args.output)
    
    print(f"📄 Results saved to: {args.output}")

if __name__ == '__main__':
    main()
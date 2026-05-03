#!/usr/bin/env python3
"""
WhatsApp Integration for Document Workflows
Uses WhatsApp Business API (no nanoclaw dependency)
"""

import requests
import json
import os
from typing import Dict, List, Optional
from pathlib import Path

class WhatsAppNotifier:
    """
    Lightweight WhatsApp integration inspired by nanoclaw's 
    multi-channel approach but using direct API calls
    """
    
    def __init__(self, phone_number_id: str = None, access_token: str = None):
        self.phone_number_id = phone_number_id or os.getenv('WHATSAPP_PHONE_NUMBER_ID')
        self.access_token = access_token or os.getenv('WHATSAPP_ACCESS_TOKEN')
        self.base_url = f"https://graph.facebook.com/v18.0/{self.phone_number_id}/messages"
        
    def send_text(self, to: str, message: str) -> Dict:
        """Send text message via WhatsApp Business API"""
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'messaging_product': 'whatsapp',
            'to': to,
            'type': 'text',
            'text': {'body': message}
        }
        
        response = requests.post(self.base_url, headers=headers, json=data)
        return response.json()
    
    def send_document_summary(self, to: str, document_path: str, summary: Dict) -> Dict:
        """Send formatted document processing summary"""
        
        # Format summary message
        message = f"""📄 Document Processed: {Path(document_path).name}

🧠 Feynman Analysis Complete:
• Concepts extracted: {len(summary.get('concepts', []))}
• Explanations generated: {len(summary.get('explanations', {}))}
• Gaps identified: {len(summary.get('gap_analysis', {}).get('gaps_found', []))}
• Status: {summary.get('status', 'Unknown')}

📊 Quality Score: {summary.get('gap_analysis', {}).get('clarity_score', 'N/A')}/10

React with ✅ to approve or 📝 to request changes."""
        
        return self.send_text(to, message)
    
    def send_concept_explanation(self, to: str, concept: str, explanation: Dict) -> Dict:
        """Send formatted concept explanation"""
        
        message = f"""💡 Concept: {concept}

🎯 Simple Explanation:
{explanation.get('simple_explanation', 'No explanation available')}

🔗 Analogy:
{explanation.get('analogy', 'No analogy provided')}

📝 Example:
{explanation.get('example', 'No example provided')}

❓ Why This Matters:
{explanation.get('why_matters', 'Importance not specified')}"""
        
        return self.send_text(to, message)
    
    def send_processing_status(self, to: str, status: Dict) -> Dict:
        """Send pipeline processing status"""
        
        message = f"""⚙️ PUO-AI Pipeline Status

📊 Current Operations:
• Lexicon entries: {status.get('lexicon_count', 'Unknown')}
• Pending injections: {status.get('pending_injections', 0)}
• Last enrichment: {status.get('last_enrichment', 'Never')}

🔄 Recent Activity:
{chr(10).join(status.get('recent_activity', ['No recent activity']))}

🧪 Test Status: {'✅ All passing' if status.get('tests_passing') else '❌ Some failing'}

Type 'status details' for full report."""
        
        return self.send_text(to, message)

class WhatsAppCommandProcessor:
    """
    Process WhatsApp commands for document workflows
    Inspired by nanoclaw's command pattern
    """
    
    def __init__(self, notifier: WhatsAppNotifier):
        self.notifier = notifier
        self.commands = {
            'process': self.cmd_process_document,
            'explain': self.cmd_explain_concept,
            'status': self.cmd_get_status,
            'inject': self.cmd_inject_entries,
            'validate': self.cmd_validate_lexicon,
            'backup': self.cmd_create_backup,
            'help': self.cmd_help
        }
    
    def process_message(self, from_number: str, message: str) -> Dict:
        """Process incoming WhatsApp message and execute commands"""
        
        # Simple command parsing (improve as needed)
        parts = message.strip().split()
        if not parts:
            return self.cmd_help(from_number, [])
            
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        if command in self.commands:
            return self.commands[command](from_number, args)
        else:
            return self.notifier.send_text(from_number, 
                f"❓ Unknown command: {command}\nType 'help' for available commands.")
    
    def cmd_process_document(self, from_number: str, args: List[str]) -> Dict:
        """Process: process <document_path>"""
        if not args:
            return self.notifier.send_text(from_number, 
                "Usage: process <document_path>\nExample: process sources/pdfs/mabille.pdf")
        
        document_path = args[0]
        
        # Trigger Feynman processing (integrate with your pipeline)
        self.notifier.send_text(from_number, f"🚀 Starting Feynman processing for: {document_path}")
        
        # In real implementation, call your feynman_pipeline.py
        # result = subprocess.run(['python3', 'feynman_pipeline.py', document_path])
        
        # Mock result for demo
        mock_summary = {
            'concepts': ['morphology', 'noun_classes'],
            'explanations': {'morphology': 'word structure'},
            'gap_analysis': {'gaps_found': ['needs_examples'], 'clarity_score': 8},
            'status': 'completed'
        }
        
        return self.notifier.send_document_summary(from_number, document_path, mock_summary)
    
    def cmd_explain_concept(self, from_number: str, args: List[str]) -> Dict:
        """Explain: explain <concept>"""
        if not args:
            return self.notifier.send_text(from_number, 
                "Usage: explain <concept>\nExample: explain morphology")
        
        concept = ' '.join(args)
        
        # Mock explanation (integrate with your lexicon)
        mock_explanation = {
            'simple_explanation': f'{concept} is like building blocks for words',
            'analogy': 'Think of words as LEGO constructions',
            'example': 'un-happy-ness = not + feeling good + thing',
            'why_matters': 'Helps you understand new words without a dictionary'
        }
        
        return self.notifier.send_concept_explanation(from_number, concept, mock_explanation)
    
    def cmd_get_status(self, from_number: str, args: List[str]) -> Dict:
        """Status: status [details]"""
        
        # Mock status (integrate with your actual pipeline)
        mock_status = {
            'lexicon_count': 1247,
            'pending_injections': 3,
            'last_enrichment': '2026-05-01 09:30',
            'recent_activity': [
                '✅ Processed Mabille pages 1-10',
                '📝 Added 23 new entries',
                '🔍 Validated schema compliance'
            ],
            'tests_passing': True
        }
        
        return self.notifier.send_processing_status(from_number, mock_status)
    
    def cmd_inject_entries(self, from_number: str, args: List[str]) -> Dict:
        """Inject: inject <staged_file>"""
        if not args:
            return self.notifier.send_text(from_number, 
                "Usage: inject <staged_file>\nExample: inject staged_casalis_a.json")
        
        staged_file = args[0]
        
        # In real implementation, call your injection script
        self.notifier.send_text(from_number, f"💉 Injecting entries from: {staged_file}")
        
        # Mock result
        return self.notifier.send_text(from_number, 
            f"✅ Successfully injected 15 entries from {staged_file}\n📊 Lexicon now contains 1262 entries")
    
    def cmd_validate_lexicon(self, from_number: str, args: List[str]) -> Dict:
        """Validate: validate [schema|all]"""
        
        validation_type = args[0] if args else 'schema'
        
        self.notifier.send_text(from_number, f"🧪 Running {validation_type} validation...")
        
        # Mock validation result
        return self.notifier.send_text(from_number, 
            "✅ Validation complete:\n• Schema: PASS\n• Integrity: PASS\n• Tests: 21/21 passing")
    
    def cmd_create_backup(self, from_number: str, args: List[str]) -> Dict:
        """Backup: backup [label]"""
        
        label = args[0] if args else 'manual'
        
        # In real implementation, call your backup script
        return self.notifier.send_text(from_number, 
            f"💾 Backup created: backup_{label}_{Path().name}_20260501_1430.tar.gz")
    
    def cmd_help(self, from_number: str, args: List[str]) -> Dict:
        """Help: help [command]"""
        
        help_text = """🤖 PUO-AI WhatsApp Commands:

📄 Document Processing:
• process <file> - Run Feynman analysis
• explain <concept> - Get simple explanation

📊 Status & Management:
• status - Show pipeline status
• validate - Run validation tests
• backup [label] - Create backup

💉 Data Operations:
• inject <file> - Inject staged entries

❓ Help:
• help - Show this message

Example: process mabille.pdf"""
        
        return self.notifier.send_text(from_number, help_text)

# Example usage
def main():
    """Example of how to use WhatsApp integration"""
    
    # Initialize notifier (requires WhatsApp Business API credentials)
    notifier = WhatsAppNotifier()
    processor = WhatsAppCommandProcessor(notifier)
    
    # Example: Process a command
    test_number = "+1234567890"  # Replace with actual number
    
    # Simulate received message
    processor.process_message(test_number, "status")
    processor.process_message(test_number, "explain morphology")
    processor.process_message(test_number, "process sources/pdfs/mabille.pdf")

if __name__ == '__main__':
    main()
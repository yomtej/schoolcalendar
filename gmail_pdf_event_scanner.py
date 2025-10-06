#!/usr/bin/env python3
"""
Gmail PDF Event Scanner for School Calendar
============================================

This script scans Gmail for school-related emails, downloads PDF attachments,
extracts text content, and uses AI to identify and parse calendar events.

Features:
- Connects to Gmail API to fetch school emails
- Downloads PDF attachments from emails
- Extracts text from PDFs
- Uses OpenAI API to intelligently parse events
- Updates the calendar with discovered events
- Maintains a history to avoid duplicate processing

Requirements:
- Gmail API access enabled
- OpenAI API key configured
- poppler-utils for PDF text extraction
"""

import json
import logging
import os
import sys
import re
import base64
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from openai import OpenAI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("/home/ubuntu/school-calendar-data/gmail_scanner.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("gmail_pdf_scanner")

# Configuration
SCRIPT_DIR = Path(__file__).parent
PDF_DOWNLOAD_DIR = SCRIPT_DIR / "downloaded_pdfs"
PROCESSED_EMAILS_FILE = SCRIPT_DIR / "processed_emails.json"
EXTRACTED_EVENTS_FILE = SCRIPT_DIR / "extracted_events.json"

# Create directories
PDF_DOWNLOAD_DIR.mkdir(exist_ok=True)

class GmailPDFScanner:
    """Scanner for Gmail emails with PDF attachments containing school events."""
    
    def __init__(self):
        """Initialize the Gmail PDF scanner."""
        self.openai_client = OpenAI()  # API key from environment
        self.processed_emails = self.load_processed_emails()
        self.extracted_events = self.load_extracted_events()
    
    def load_processed_emails(self):
        """Load the list of already processed email IDs."""
        if PROCESSED_EMAILS_FILE.exists():
            with open(PROCESSED_EMAILS_FILE, 'r') as f:
                return json.load(f)
        return []
    
    def save_processed_emails(self):
        """Save the list of processed email IDs."""
        with open(PROCESSED_EMAILS_FILE, 'w') as f:
            json.dump(self.processed_emails, f, indent=2)
    
    def load_extracted_events(self):
        """Load previously extracted events."""
        if EXTRACTED_EVENTS_FILE.exists():
            with open(EXTRACTED_EVENTS_FILE, 'r') as f:
                return json.load(f)
        return []
    
    def save_extracted_events(self):
        """Save extracted events to file."""
        with open(EXTRACTED_EVENTS_FILE, 'w') as f:
            json.dump(self.extracted_events, f, indent=2)
    
    def search_school_emails(self):
        """
        Search Gmail for school-related emails.
        
        This function should use the Gmail API tools when available.
        For now, it returns a placeholder structure.
        """
        # TODO: Replace with actual Gmail API call when available
        # Example search query:
        # from:@hampsteadhill.school OR subject:(curriculum OR calendar OR term OR dates)
        # has:attachment filename:pdf
        
        logger.info("Searching for school-related emails with PDF attachments...")
        
        # Placeholder - in production, this would use Gmail API
        return []
    
    def download_pdf_attachment(self, email_id, attachment_id, filename):
        """
        Download a PDF attachment from an email.
        
        Args:
            email_id: Gmail message ID
            attachment_id: Attachment ID
            filename: Name to save the file as
        
        Returns:
            Path to downloaded PDF file
        """
        # TODO: Implement actual Gmail attachment download
        # For now, return None
        logger.info(f"Would download attachment: {filename} from email {email_id}")
        return None
    
    def extract_text_from_pdf(self, pdf_path):
        """
        Extract text content from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
        
        Returns:
            Extracted text content
        """
        try:
            # Use pdftotext from poppler-utils
            result = subprocess.run(
                ['pdftotext', '-layout', str(pdf_path), '-'],
                capture_output=True,
                text=True,
                check=True
            )
            text = result.stdout
            logger.info(f"Extracted {len(text)} characters from {pdf_path.name}")
            return text
        except subprocess.CalledProcessError as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return None
        except FileNotFoundError:
            logger.error("pdftotext not found. Install with: sudo apt-get install poppler-utils")
            return None
    
    def parse_events_with_ai(self, pdf_text, pdf_filename):
        """
        Use OpenAI API to intelligently parse events from PDF text.
        
        Args:
            pdf_text: Extracted text from PDF
            pdf_filename: Name of the PDF file for context
        
        Returns:
            List of parsed events in standard format
        """
        logger.info(f"Parsing events from {pdf_filename} using AI...")
        
        prompt = f"""You are analyzing a school calendar document. Extract ALL calendar events, dates, and important school activities.

Document name: {pdf_filename}
Document content:
{pdf_text[:8000]}  # Limit to avoid token limits

Please extract ALL events and return them as a JSON array with this exact structure:
[
  {{
    "date": <day number>,
    "month": <month number 1-12>,
    "year": <year>,
    "title": "<event title>",
    "time": "<time or 'All Day'>",
    "description": "<detailed description>",
    "location": "<location or 'School'>",
    "type": "<one of: Assembly, Celebration, Activity, Special Day, Academic, School Trip, Closure, Holiday, Special Week, Term End, Exhibition>",
    "children": ["Leo", "Novah"]  // or just ["Leo"] if Year 2 specific
  }}
]

Important instructions:
1. Extract EVERY date mentioned (September, October, November, December events)
2. Include special days like "Odd Socks Day", "Anti-Bullying Week", "Red White and Blue Day"
3. Include school closures, holidays, half terms
4. Include class assemblies, parent meetings, trips
5. Include term start/end dates
6. Include PD days and school closures
7. For date ranges (e.g., "10th-14th Anti-Bullying Week"), create events for start and end
8. If year is not mentioned, assume 2025
9. Return ONLY the JSON array, no other text

Extract all events now:"""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": "You are a precise calendar event extractor. Return only valid JSON arrays."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=4000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Extract JSON from response (handle markdown code blocks)
            if content.startswith("```"):
                content = re.sub(r'```json\s*|\s*```', '', content)
            
            events = json.loads(content)
            logger.info(f"Successfully parsed {len(events)} events from {pdf_filename}")
            return events
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            logger.error(f"Response was: {content[:500]}")
            return []
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            return []
    
    def merge_events_with_existing(self, new_events):
        """
        Merge newly extracted events with existing events, avoiding duplicates.
        
        Args:
            new_events: List of newly extracted events
        
        Returns:
            Updated list of all events
        """
        # Load current events from update_calendar_data.py
        existing_events = self.extracted_events.copy()
        
        # Create a set of existing event signatures for duplicate detection
        existing_signatures = set()
        for event in existing_events:
            sig = f"{event['date']}-{event['month']}-{event['year']}-{event['title']}"
            existing_signatures.add(sig)
        
        # Add new events that don't already exist
        added_count = 0
        for event in new_events:
            sig = f"{event['date']}-{event['month']}-{event['year']}-{event['title']}"
            if sig not in existing_signatures:
                existing_events.append(event)
                existing_signatures.add(sig)
                added_count += 1
                logger.info(f"Added new event: {event['title']} on {event['month']}/{event['date']}/{event['year']}")
        
        logger.info(f"Added {added_count} new events, {len(new_events) - added_count} were duplicates")
        
        # Sort events by date
        existing_events.sort(key=lambda e: (e['year'], e['month'], e['date']))
        
        return existing_events
    
    def update_calendar_script(self, all_events):
        """
        Update the update_calendar_data.py script with the complete event list.
        
        Args:
            all_events: Complete list of events to include
        """
        script_path = SCRIPT_DIR / "update_calendar_data.py"
        
        try:
            with open(script_path, 'r') as f:
                content = f.read()
            
            # Find the get_events function and replace the events list
            # This is a simplified approach - in production, use AST manipulation
            pattern = r'(def get_events\(\):.*?events = \[)(.*?)(\]\s+return events)'
            
            # Format events as Python code
            events_code = ""
            for event in all_events:
                events_code += "        {\n"
                events_code += f'            "date": {event["date"]},\n'
                events_code += f'            "month": {event["month"]},\n'
                events_code += f'            "year": {event["year"]},\n'
                events_code += f'            "title": "{event["title"]}",\n'
                events_code += f'            "time": "{event["time"]}",\n'
                events_code += f'            "description": "{event["description"]}",\n'
                events_code += f'            "location": "{event["location"]}",\n'
                events_code += f'            "type": "{event["type"]}",\n'
                events_code += f'            "children": {json.dumps(event["children"])}\n'
                events_code += "        },\n"
            
            # Remove trailing comma
            events_code = events_code.rstrip(',\n') + '\n'
            
            # Replace in content
            new_content = re.sub(
                pattern,
                r'\1\n' + events_code + r'    \3',
                content,
                flags=re.DOTALL
            )
            
            # Write back
            with open(script_path, 'w') as f:
                f.write(new_content)
            
            logger.info(f"Updated {script_path} with {len(all_events)} events")
            
        except Exception as e:
            logger.error(f"Error updating calendar script: {e}")
    
    def scan_and_process(self):
        """
        Main function to scan emails, process PDFs, and update calendar.
        """
        logger.info("Starting Gmail PDF event scanner...")
        
        # Search for school emails
        emails = self.search_school_emails()
        
        if not emails:
            logger.info("No new emails found with PDF attachments")
            return
        
        new_events_found = False
        
        for email in emails:
            email_id = email.get('id')
            
            # Skip if already processed
            if email_id in self.processed_emails:
                continue
            
            logger.info(f"Processing email: {email.get('subject', 'No subject')}")
            
            # Process each PDF attachment
            for attachment in email.get('attachments', []):
                if not attachment['filename'].lower().endswith('.pdf'):
                    continue
                
                # Download PDF
                pdf_path = self.download_pdf_attachment(
                    email_id,
                    attachment['id'],
                    attachment['filename']
                )
                
                if not pdf_path or not pdf_path.exists():
                    continue
                
                # Extract text
                pdf_text = self.extract_text_from_pdf(pdf_path)
                
                if not pdf_text:
                    continue
                
                # Parse events with AI
                events = self.parse_events_with_ai(pdf_text, attachment['filename'])
                
                if events:
                    # Merge with existing events
                    self.extracted_events = self.merge_events_with_existing(events)
                    new_events_found = True
            
            # Mark email as processed
            self.processed_emails.append(email_id)
        
        # Save state
        self.save_processed_emails()
        
        if new_events_found:
            self.save_extracted_events()
            
            # Update the calendar script
            self.update_calendar_script(self.extracted_events)
            
            logger.info("Calendar updated with newly discovered events")
        else:
            logger.info("No new events discovered")

def main():
    """Main entry point."""
    try:
        scanner = GmailPDFScanner()
        scanner.scan_and_process()
        return True
    except Exception as e:
        logger.error(f"Fatal error in Gmail PDF scanner: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

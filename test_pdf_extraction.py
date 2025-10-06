#!/usr/bin/env python3
"""
Test PDF Event Extraction with AI
==================================

This script tests the AI-powered event extraction from the Year 2 Autumn Term PDF.
"""

import json
import subprocess
import sys
from openai import OpenAI

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF."""
    result = subprocess.run(
        ['pdftotext', '-layout', pdf_path, '-'],
        capture_output=True,
        text=True,
        check=True
    )
    return result.stdout

def extract_events_with_ai(pdf_text):
    """Use AI to extract all events from PDF text."""
    
    client = OpenAI()  # Uses OPENAI_API_KEY from environment
    
    prompt = f"""You are analyzing a school calendar document for Year 2 students at Hampstead Hill School. Extract ALL calendar events, dates, and important school activities.

Document content:
{pdf_text}

Please extract ALL events and return them as a JSON array with this exact structure:
[
  {{
    "date": <day number>,
    "month": <month number 1-12>,
    "year": 2025,
    "title": "<event title>",
    "time": "<time or 'All Day'>",
    "description": "<detailed description>",
    "location": "<location or 'School'>",
    "type": "<one of: Assembly, Celebration, Activity, Special Day, Academic, School Trip, Closure, Holiday, Special Week, Term End, Exhibition>",
    "children": ["Leo", "Novah"]
  }}
]

Important instructions:
1. Extract EVERY date mentioned in "Dates for your diary" section
2. Include ALL September, October, November, December events
3. Include special days like "Odd Socks Day", "Anti-Bullying Week", "Red White and Blue Day"
4. Include school closures, holidays, half terms, PD days
5. Include class assemblies (Maple, Chestnut, Pine, Poplar) - these are Year 2 specific so only Leo attends
6. Include parent meetings, exhibitions, parties
7. Include term start/end dates
8. For date ranges (e.g., "10th-14th Anti-Bullying Week"), create separate events for start and end dates
9. For "Week beginning 8th" create an event for that date
10. Year is 2025 for all events
11. Use "Leo" only for Year 2 specific events (class assemblies), use ["Leo", "Novah"] for whole school events
12. Return ONLY the JSON array, no other text or explanation

Extract all events now:"""

    print("Calling OpenAI API to extract events...")
    
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You are a precise calendar event extractor. Return only valid JSON arrays with no additional text."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,
        max_tokens=4000
    )
    
    content = response.choices[0].message.content.strip()
    
    # Remove markdown code blocks if present
    if content.startswith("```"):
        import re
        content = re.sub(r'```json\s*|\s*```', '', content).strip()
    
    events = json.loads(content)
    return events

def main():
    """Main function."""
    pdf_path = "/home/ubuntu/upload/Year2AutumnTerm.pdf"
    
    print(f"Extracting text from {pdf_path}...")
    pdf_text = extract_text_from_pdf(pdf_path)
    print(f"Extracted {len(pdf_text)} characters")
    
    print("\nExtracting events with AI...")
    events = extract_events_with_ai(pdf_text)
    
    print(f"\n✅ Successfully extracted {len(events)} events!\n")
    
    # Group by month
    by_month = {}
    for event in events:
        month = event['month']
        if month not in by_month:
            by_month[month] = []
        by_month[month].append(event)
    
    # Display results
    month_names = {9: "September", 10: "October", 11: "November", 12: "December"}
    
    for month_num in sorted(by_month.keys()):
        month_name = month_names.get(month_num, f"Month {month_num}")
        print(f"\n{month_name} 2025:")
        print("=" * 60)
        for event in sorted(by_month[month_num], key=lambda e: e['date']):
            children_str = ", ".join(event['children'])
            print(f"  {event['date']:2d}/{month_num:02d}: {event['title']}")
            print(f"           Time: {event['time']}")
            print(f"           Type: {event['type']}")
            print(f"           Children: {children_str}")
            print()
    
    # Save to file
    output_file = "/home/ubuntu/school-calendar-data/ai_extracted_events.json"
    with open(output_file, 'w') as f:
        json.dump(events, f, indent=2)
    
    print(f"\n✅ Events saved to: {output_file}")
    print(f"\nTotal events extracted: {len(events)}")
    
    return events

if __name__ == "__main__":
    try:
        events = main()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

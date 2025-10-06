#!/usr/bin/env python3
"""
Merge AI-Extracted Events with Calendar
========================================

This script merges AI-extracted events from PDFs with the existing calendar,
avoiding duplicates and updating the update_calendar_data.py script.
"""

import json
import re
from pathlib import Path

def load_ai_events():
    """Load AI-extracted events."""
    with open('/home/ubuntu/school-calendar-data/ai_extracted_events.json', 'r') as f:
        return json.load(f)

def merge_events(ai_events):
    """
    Merge AI events with existing events in update_calendar_data.py.
    
    Strategy:
    - Use AI-extracted events as the source of truth
    - These are more complete and accurate than hardcoded events
    - Replace the entire events list with AI-extracted events
    """
    
    # Sort events by date
    ai_events.sort(key=lambda e: (e['year'], e['month'], e['date']))
    
    print(f"Merging {len(ai_events)} AI-extracted events...")
    
    # Read the current script
    script_path = Path('/home/ubuntu/school-calendar-data/update_calendar_data.py')
    with open(script_path, 'r') as f:
        content = f.read()
    
    # Generate Python code for events
    events_code = ""
    for event in ai_events:
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
    
    # Remove trailing comma and newline
    events_code = events_code.rstrip(',\n')
    
    # Find and replace the events list in get_events function
    # Pattern: from "events = [" to the closing "]" before "return events"
    pattern = r'(def get_events\(\):.*?events = \[)(.*?)(\n    \]\s+return events)'
    
    replacement = r'\1\n' + events_code + r'\n    \3'
    
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    if new_content == content:
        print("❌ Warning: Could not find events list pattern in script")
        return False
    
    # Write back
    with open(script_path, 'w') as f:
        f.write(new_content)
    
    print(f"✅ Successfully updated {script_path} with {len(ai_events)} events")
    return True

def main():
    """Main function."""
    print("Loading AI-extracted events...")
    ai_events = load_ai_events()
    
    print(f"\nFound {len(ai_events)} AI-extracted events:")
    
    # Group by month for display
    by_month = {}
    for event in ai_events:
        month = event['month']
        if month not in by_month:
            by_month[month] = []
        by_month[month].append(event)
    
    month_names = {9: "September", 10: "October", 11: "November", 12: "December"}
    for month_num in sorted(by_month.keys()):
        month_name = month_names.get(month_num, f"Month {month_num}")
        print(f"  {month_name}: {len(by_month[month_num])} events")
    
    print("\nMerging with calendar...")
    success = merge_events(ai_events)
    
    if success:
        print("\n✅ Calendar successfully updated with AI-extracted events!")
        print("\nNext steps:")
        print("1. Run: cd /home/ubuntu/school-calendar-data && python3 update_calendar_data.py")
        print("2. The updated calendar will be pushed to GitHub automatically")
    else:
        print("\n❌ Failed to merge events")
        return False
    
    return True

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)

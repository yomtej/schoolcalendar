#!/usr/bin/env python3
"""
Event Verification Script
=========================

This script verifies that all 22 events (including November and December)
are present in both the local file and on GitHub.

It will alert if events are missing and can automatically restore them.
"""

import json
import subprocess
import sys
from datetime import datetime

EXPECTED_EVENT_COUNT = 22
EXPECTED_MONTHS = {9: 8, 10: 9, 11: 3, 12: 2}

def check_local_events():
    """Check events in local file."""
    try:
        with open('/home/ubuntu/school-calendar-data/school_calendar_data.json', 'r') as f:
            data = json.load(f)
        
        events = data['events']
        by_month = {}
        for e in events:
            by_month.setdefault(e['month'], []).append(e)
        
        print(f"📁 LOCAL FILE: {len(events)} events")
        for month in sorted(by_month.keys()):
            print(f"   Month {month}: {len(by_month[month])} events")
        
        if len(events) != EXPECTED_EVENT_COUNT:
            print(f"❌ ERROR: Expected {EXPECTED_EVENT_COUNT} events, found {len(events)}")
            return False
        
        for month, expected_count in EXPECTED_MONTHS.items():
            actual_count = len(by_month.get(month, []))
            if actual_count != expected_count:
                print(f"❌ ERROR: Month {month} expected {expected_count} events, found {actual_count}")
                return False
        
        print("✅ Local file is correct\n")
        return True
        
    except Exception as e:
        print(f"❌ ERROR reading local file: {e}")
        return False

def check_github_events():
    """Check events on GitHub."""
    try:
        result = subprocess.run(
            ['curl', '-s', f'https://raw.githubusercontent.com/yomtej/schoolcalendar/refs/heads/main/school_calendar_data.json?t={datetime.now().timestamp()}'],
            capture_output=True,
            text=True,
            check=True
        )
        
        data = json.loads(result.stdout)
        events = data['events']
        by_month = {}
        for e in events:
            by_month.setdefault(e['month'], []).append(e)
        
        print(f"🌐 GITHUB: {len(events)} events")
        for month in sorted(by_month.keys()):
            print(f"   Month {month}: {len(by_month[month])} events")
        
        if len(events) != EXPECTED_EVENT_COUNT:
            print(f"❌ ERROR: Expected {EXPECTED_EVENT_COUNT} events, found {len(events)}")
            print(f"⚠️  GitHub has WRONG data!")
            return False
        
        for month, expected_count in EXPECTED_MONTHS.items():
            actual_count = len(by_month.get(month, []))
            if actual_count != expected_count:
                print(f"❌ ERROR: Month {month} expected {expected_count} events, found {actual_count}")
                return False
        
        print("✅ GitHub is correct\n")
        return True
        
    except Exception as e:
        print(f"❌ ERROR checking GitHub: {e}")
        return False

def fix_github():
    """Force push correct data to GitHub."""
    print("\n🔧 FIXING: Regenerating and pushing correct data...")
    
    try:
        # Run update script
        subprocess.run(
            ['python3', '/home/ubuntu/school-calendar-data/update_calendar_data.py'],
            cwd='/home/ubuntu/school-calendar-data',
            check=True
        )
        print("✅ Successfully pushed correct data to GitHub")
        return True
    except Exception as e:
        print(f"❌ ERROR fixing GitHub: {e}")
        return False

def main():
    """Main verification function."""
    print("="* 60)
    print("SCHOOL CALENDAR EVENT VERIFICATION")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="* 60)
    print()
    
    local_ok = check_local_events()
    github_ok = check_github_events()
    
    if local_ok and github_ok:
        print("✅ ALL CHECKS PASSED - System is healthy")
        return 0
    
    if local_ok and not github_ok:
        print("⚠️  LOCAL is correct but GITHUB is wrong")
        print("   This means an external process is pushing old data")
        
        if '--fix' in sys.argv:
            fix_github()
        else:
            print("\n   Run with --fix to automatically restore GitHub")
        return 1
    
    if not local_ok:
        print("❌ LOCAL FILE is corrupted!")
        print("   The update_calendar_data.py script may have been modified")
        print("   Need to restore AI-extracted events")
        return 2
    
    return 1

if __name__ == "__main__":
    sys.exit(main())

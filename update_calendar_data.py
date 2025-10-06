#!/usr/bin/env python3

import json
import logging
import os
import sys
import datetime
from datetime import date, timedelta
import random
import subprocess
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("/home/ubuntu/school-calendar-data/update.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("school_calendar_updater")

def get_current_date():
    """Get the current date for the application."""
    return datetime.datetime.now()

def format_date(date_obj):
    """Format a date as 'Day, Month Day' (e.g., 'Monday, October 6')."""
    return date_obj.strftime("%A, %B ") + str(date_obj.day)

def get_weather_forecast(date_obj):
    """Generate a weather forecast for the given date."""
    # Simplified weather generation for demonstration
    temp = random.randint(12, 18)
    descriptions = [
        "Pleasant day - normal layers should be fine. Light jacket optional.",
        "Slightly chilly - bring a jacket.",
        "Warm day expected - light clothing appropriate.",
        "Rain expected - bring raincoat and umbrella.",
        "Cloudy but dry - standard uniform is fine."
    ]
    return {
        "temp": f"{temp}°C",
        "description": random.choice(descriptions)
    }

def get_pickup_time(child_name, day_of_week, has_after_school_club, leo_pickup_override=None):
    """Get the pickup time for a child based on their schedule.
    
    Args:
        child_name: Name of the child (Leo or Novah)
        day_of_week: Day of the week (1=Monday, 7=Sunday)
        has_after_school_club: Whether the child has an after-school club
        leo_pickup_override: Optional override for Leo's pickup time (used for Novah sync)
    
    Returns:
        Pickup time as a string
    """
    if child_name == "Leo":
        if has_after_school_club:
            return "5:30 PM"
        return "3:40 PM"
    elif child_name == "Novah":
        # Novah's pickup time matches Leo's by default
        # This can be overridden when explicitly mentioned in emails
        if leo_pickup_override:
            return leo_pickup_override
        # If no override, use Leo's pickup time (which is passed as leo_pickup_override)
        # For now, we'll calculate Leo's time here to sync
        leo_has_club = has_after_school_club  # This will be Leo's club status
        if leo_has_club:
            return "5:30 PM"
        return "3:40 PM"
    return "3:30 PM"  # Default

def get_gate(child_name):
    """Get the pickup gate for a child."""
    if child_name == "Leo":
        return "West Gate"
    elif child_name == "Novah":
        return "Meadow Gate"
    return "Main Gate"  # Default

def get_uniform(child_name, day_of_week):
    """Get the uniform type for a child based on the day of the week."""
    if child_name == "Leo":
        # Tuesday is Zumba day, Wednesday is PE day
        if day_of_week == 1:  # Monday - Swimming
            return {"uniform": "School Uniform", "uniformType": "Uniform"}
        elif day_of_week == 2:  # Tuesday - Zumba
            return {"uniform": "Sports Wear", "uniformType": "Sports"}
        elif day_of_week == 3:  # Wednesday - PE
            return {"uniform": "Sports Wear", "uniformType": "Sports"}
        else:
            return {"uniform": "School Uniform", "uniformType": "Uniform"}
    elif child_name == "Novah":
        # Forest School on Thursday
        if day_of_week == 4:  # Thursday
            return {"uniform": "Forest School Kit", "uniformType": "Forest"}
        else:
            return {"uniform": "School Uniform", "uniformType": "Uniform"}
    return {"uniform": "School Uniform", "uniformType": "Uniform"}  # Default

def has_after_school_club(child_name, day_of_week):
    """Check if a child has an after-school club on a given day."""
    if child_name == "Leo":
        # Leo has clubs on Monday, Tuesday, Wednesday, Thursday
        if day_of_week in [1, 2, 3, 4]:
            return True
    return False

def get_child_activities(child_name):
    """Get the activities for a child."""
    activities = []
    
    if child_name == "Leo":
        activities = [
            {
                "day": "Monday",
                "activities": [
                    {
                        "title": "Swimming",
                        "time": "10:30-11:30",
                        "teacher": "Mr. Roberts"
                    },
                    {
                        "title": "Chess Club",
                        "time": "15:45-16:45",
                        "teacher": "Mr. Johnson"
                    }
                ]
            },
            {
                "day": "Tuesday",
                "activities": [
                    {
                        "title": "Zumba",
                        "time": "10:30-11:30",
                        "teacher": "PE Staff"
                    },
                    {
                        "title": "Gymnastics",
                        "time": "15:45-16:45",
                        "teacher": "Miss Sarah"
                    }
                ]
            },
            {
                "day": "Wednesday",
                "activities": [
                    {
                        "title": "PE",
                        "time": "10:30-11:30",
                        "teacher": "PE Staff"
                    },
                    {
                        "title": "STEM Club",
                        "time": "15:45-16:45",
                        "teacher": "Mrs. Chen"
                    }
                ]
            },
            {
                "day": "Thursday",
                "activities": [
                    {
                        "title": "Drama Club",
                        "time": "15:45-16:45",
                        "teacher": "Ms. Williams"
                    }
                ]
            },
            {
                "day": "Friday",
                "activities": []
            }
        ]
    elif child_name == "Novah":
        activities = [
            {
                "day": "Monday",
                "activities": []
            },
            {
                "day": "Tuesday",
                "activities": [
                    {
                        "title": "Music & Movement",
                        "time": "10:30-11:00",
                        "teacher": "Mrs. Davies"
                    }
                ]
            },
            {
                "day": "Wednesday",
                "activities": []
            },
            {
                "day": "Thursday",
                "activities": [
                    {
                        "title": "Forest School",
                        "time": "9:00-11:00",
                        "teacher": "Miss Emma"
                    }
                ]
            },
            {
                "day": "Friday",
                "activities": []
            }
        ]
    
    return activities

def get_events():
    """Get all events for the current term."""
    events = [
        {
            "date": 3,
            "month": 10,
            "year": 2025,
            "title": "Poplar Class Assembly",
            "time": "9:00-9:30am",
            "description": "Year 2 Poplar Class Assembly. Parents welcome to attend.",
            "location": "School Hall",
            "type": "Assembly",
            "children": ["Leo"]
        },
        {
            "date": 4,
            "month": 10,
            "year": 2025,
            "title": "HHS 75th Birthday",
            "time": "All Day",
            "description": "Celebrating Hampstead Hill School's 75th birthday.",
            "location": "School",
            "type": "Celebration",
            "children": ["Leo", "Novah"]
        },
        {
            "date": 7,
            "month": 10,
            "year": 2025,
            "title": "Swimming Lessons Begin",
            "time": "10:30-11:30am",
            "description": "First swimming lesson. Bring swimsuit, towel, and swimming cap.",
            "location": "Local Pool",
            "type": "Activity",
            "children": ["Leo"]
        },
        {
            "date": 10,
            "month": 10,
            "year": 2025,
            "title": "Red, White and Blue Day",
            "time": "All Day",
            "description": "Special themed day. Children can wear red, white, and blue clothes.",
            "location": "School",
            "type": "Special Day",
            "children": ["Leo", "Novah"]
        },
        {
            "date": 10,
            "month": 10,
            "year": 2025,
            "title": "Parent Consultations Day 1",
            "time": "15:30-19:00",
            "description": "15-minute consultation slots with teachers.",
            "location": "School Classrooms",
            "type": "Academic",
            "children": ["Leo", "Novah"]
        },
        {
            "date": 11,
            "month": 10,
            "year": 2025,
            "title": "Parent Consultations Day 2",
            "time": "9:00-12:00",
            "description": "15-minute consultation slots with teachers.",
            "location": "School Classrooms",
            "type": "Academic",
            "children": ["Leo", "Novah"]
        },
        {
            "date": 15,
            "month": 10,
            "year": 2025,
            "title": "Science Museum Trip",
            "time": "9:30am-3:00pm",
            "description": "School trip to Science Museum. Packed lunch required.",
            "location": "Science Museum",
            "type": "School Trip",
            "children": ["Leo"]
        },
        {
            "date": 17,
            "month": 10,
            "year": 2025,
            "title": "PD Day - School Closed",
            "time": "All Day",
            "description": "School closed for Professional Development Day.",
            "location": "School",
            "type": "Closure",
            "children": ["Leo", "Novah"]
        },
        {
            "date": 20,
            "month": 10,
            "year": 2025,
            "title": "Half Term Begins",
            "time": "All Day",
            "description": "School closed for half term holiday.",
            "location": "School",
            "type": "Holiday",
            "children": ["Leo", "Novah"]
        },
        {
            "date": 24,
            "month": 10,
            "year": 2025,
            "title": "Half Term Ends",
            "time": "All Day",
            "description": "Last day of half term holiday. School resumes on Monday, October 27th.",
            "location": "School",
            "type": "Holiday",
            "children": ["Leo", "Novah"]
        },
        {
            "date": 31,
            "month": 10,
            "year": 2025,
            "title": "Black History Month Exhibition",
            "time": "During School",
            "description": "Exhibition showcasing student work from Black History Month activities.",
            "location": "School Hall",
            "type": "Exhibition",
            "children": ["Leo", "Novah"]
        },
        {
            "date": 10,
            "month": 11,
            "year": 2025,
            "title": "Anti-Bullying Week Begins",
            "time": "All Day",
            "description": "Anti-Bullying Week runs from November 10th to 14th.",
            "location": "School",
            "type": "Special Week",
            "children": ["Leo", "Novah"]
        },
        {
            "date": 10,
            "month": 11,
            "year": 2025,
            "title": "Odd Socks Day",
            "time": "All Day",
            "description": "Wear odd socks to celebrate uniqueness and raise awareness for Anti-Bullying Week.",
            "location": "School",
            "type": "Special Day",
            "children": ["Leo", "Novah"]
        },
        {
            "date": 14,
            "month": 11,
            "year": 2025,
            "title": "Anti-Bullying Week Ends",
            "time": "All Day",
            "description": "Last day of Anti-Bullying Week.",
            "location": "School",
            "type": "Special Week",
            "children": ["Leo", "Novah"]
        },
        {
            "date": 12,
            "month": 12,
            "year": 2025,
            "title": "Christmas Party",
            "time": "During School",
            "description": "School Christmas party celebration.",
            "location": "School",
            "type": "Celebration",
            "children": ["Leo", "Novah"]
        },
        {
            "date": 12,
            "month": 12,
            "year": 2025,
            "title": "Last Day of Autumn Term",
            "time": "All Day",
            "description": "Last day of Autumn Term. School closes for Christmas holidays.",
            "location": "School",
            "type": "Term End",
            "children": ["Leo", "Novah"]
        }
    ]
    
    return events

def get_notices():
    """Get all notices."""
    notices = [
        {
            "id": "science-museum-trip",
            "title": "Science Museum Trip Permission",
            "priority": "high",
            "deadline": "October 10th",
            "description": "Permission slip needed for Science Museum trip on October 15th.",
            "children": ["Leo"],
            "actionButton": {
                "text": "Complete Form",
                "url": "https://forms.hampsteadhill.school/permission"
            }
        },
        {
            "id": "parent-consultation-booking",
            "title": "Parent Consultation Booking",
            "priority": "high",
            "deadline": "October 5th",
            "description": "Book your 15-minute consultation slot with your child's teacher for October 10th or 11th.",
            "children": ["Leo", "Novah"],
            "actionButton": {
                "text": "Book Now",
                "url": "https://booking.hampsteadhill.school/consultations"
            }
        },
        {
            "id": "half-term-reminder",
            "title": "Half Term Holiday",
            "priority": "medium",
            "deadline": "October 20th",
            "description": "School will be closed for half term from October 20th to October 24th. School resumes on October 27th.",
            "children": ["Leo", "Novah"]
        },
        {
            "id": "swimming-kit-reminder",
            "title": "Swimming Kit Reminder",
            "priority": "medium",
            "deadline": "October 7th",
            "description": "Remember to bring swimming kit every Monday: swimsuit, towel, and swimming cap.",
            "children": ["Leo"]
        },
        {
            "id": "school-closure",
            "title": "School Closed - Staff Training Day",
            "priority": "high",
            "deadline": "October 17th",
            "description": "School will be closed on Friday, October 17th for staff training.",
            "children": ["Leo", "Novah"]
        },
        {
            "id": "class-assembly",
            "title": "Poplar Class Assembly",
            "priority": "high",
            "deadline": "October 3rd",
            "description": "Poplar Class Assembly on Friday, October 3rd from 9:00am to 9:30am. Parents welcome to attend.",
            "children": ["Leo"]
        },
        {
            "id": "pe-days",
            "title": "PE & Zumba Days",
            "priority": "medium",
            "deadline": "Ongoing",
            "description": "PE takes place on Wednesdays and Zumba on Tuesdays. Please ensure your child has appropriate PE kit on these days.",
            "children": ["Leo"]
        },
        {
            "id": "forest-school-reschedule",
            "title": "Forest School Schedule Change",
            "priority": "medium",
            "deadline": "Next Week",
            "description": "Forest School moved to Thursday. Bring outdoor clothing.",
            "children": ["Novah"]
        }
    ]
    
    return notices

def create_calendar_days(events, current_month, current_year):
    """Create the calendar days structure with events."""
    # Get the number of days in the month
    if current_month in [4, 6, 9, 11]:
        days_in_month = 30
    elif current_month == 2:
        if current_year % 4 == 0 and (current_year % 100 != 0 or current_year % 400 == 0):
            days_in_month = 29
        else:
            days_in_month = 28
    else:
        days_in_month = 31
    
    # Create the days array
    days = []
    for day in range(1, days_in_month + 1):
        day_events = []
        for event in events:
            if event["date"] == day and event["month"] == current_month and event["year"] == current_year:
                day_events.append({
                    "title": event["title"],
                    "children": event["children"]
                })
        
        days.append({
            "date": day,
            "events": day_events
        })
    
    return days

def create_json_structure():
    """Create the complete JSON structure for the school calendar app."""
    current_date = get_current_date()
    tomorrow_date = current_date + timedelta(days=1)
    
    # Get events and notices
    events = get_events()
    notices = get_notices()
    
    # Check if Leo has after-school clubs today and tomorrow
    leo_has_club_today = has_after_school_club("Leo", current_date.weekday() + 1)
    leo_has_club_tomorrow = has_after_school_club("Leo", tomorrow_date.weekday() + 1)
    
    # Create the JSON structure
    data = {
        "meta": {
            "generated": current_date.isoformat(),
            "version": "1.0"
        },
        "schoolInfo": {
            "name": "Hampstead Hill School",
            "children": [
                {
                    "name": "Leo",
                    "year": "Year 2",
                    "class": "Poplar"
                },
                {
                    "name": "Novah",
                    "year": "Early Years",
                    "class": "Butterflies"
                }
            ]
        },
        "today": {
            "date": format_date(current_date),
            "year": current_date.year,
            "weather": get_weather_forecast(current_date),
            "children": {
                "Leo": {
                    "year": "Year 2",
                    **get_uniform("Leo", current_date.weekday() + 1),
                    "pickup": get_pickup_time("Leo", current_date.weekday() + 1, leo_has_club_today),
                    "gate": get_gate("Leo")
                },
                "Novah": {
                    "year": "Early Years",
                    **get_uniform("Novah", current_date.weekday() + 1),
                    "pickup": get_pickup_time("Novah", current_date.weekday() + 1, leo_has_club_today),
                    "gate": get_gate("Novah")
                }
            }
        },
        "tomorrow": {
            "date": format_date(tomorrow_date),
            "weather": get_weather_forecast(tomorrow_date),
            "children": {
                "Leo": {
                    "year": "Year 2",
                    **get_uniform("Leo", tomorrow_date.weekday() + 1),
                    "pickup": get_pickup_time("Leo", tomorrow_date.weekday() + 1, leo_has_club_tomorrow),
                    "gate": get_gate("Leo")
                },
                "Novah": {
                    "year": "Early Years",
                    **get_uniform("Novah", tomorrow_date.weekday() + 1),
                    "pickup": get_pickup_time("Novah", tomorrow_date.weekday() + 1, leo_has_club_tomorrow),
                    "gate": get_gate("Novah")
                }
            }
        },
        "events": events,
        "activities": {
            "Leo": get_child_activities("Leo"),
            "Novah": get_child_activities("Novah")
        },
        "notices": notices,
        "calendar": {
            "month": current_date.month,
            "year": current_date.year,
            "days": create_calendar_days(events, current_date.month, current_date.year)
        },
        "settings": {
            "notificationCount": len(notices),
            "currentTab": "Today",
            "filterSetting": "All"
        }
    }
    
    return data

def validate_json_structure(data):
    """Validate the JSON structure."""
    # Check required top-level keys
    required_keys = ["meta", "schoolInfo", "today", "tomorrow", "events", "activities", "notices", "calendar", "settings"]
    for key in required_keys:
        if key not in data:
            logger.error(f"Missing required key: {key}")
            return False
    
    # Check children names
    for child in data["schoolInfo"]["children"]:
        if child["name"] not in ["Leo", "Novah"]:
            logger.error(f"Invalid child name: {child['name']}")
            return False
    
    # Check today and tomorrow sections
    for section in ["today", "tomorrow"]:
        if "children" not in data[section]:
            logger.error(f"Missing children in {section} section")
            return False
        for child_name in ["Leo", "Novah"]:
            if child_name not in data[section]["children"]:
                logger.error(f"Missing child {child_name} in {section} section")
                return False
    
    # Check events
    for event in data["events"]:
        required_event_keys = ["date", "month", "year", "title", "children"]
        for key in required_event_keys:
            if key not in event:
                logger.error(f"Missing required key {key} in event: {event['title'] if 'title' in event else 'unknown'}")
                return False
    
    # Check notices
    for notice in data["notices"]:
        required_notice_keys = ["id", "title", "priority", "description", "children"]
        for key in required_notice_keys:
            if key not in notice:
                logger.error(f"Missing required key {key} in notice: {notice['title'] if 'title' in notice else 'unknown'}")
                return False
    
    # Check calendar
    if "month" not in data["calendar"] or "year" not in data["calendar"] or "days" not in data["calendar"]:
        logger.error("Missing required keys in calendar section")
        return False
    
    logger.info("JSON structure validation passed")
    return True

def save_json_to_file(data, filename):
    """Save the JSON data to a file."""
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Successfully saved JSON data to {filename}")
        return True
    except Exception as e:
        logger.error(f"Error saving JSON data to {filename}: {e}")
        return False

def update_readme(data):
    """Update the README.md file with the latest update timestamp."""
    try:
        readme_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md")
        with open(readme_path, 'r') as f:
            content = f.read()
        
        # Update the last updated timestamp
        current_date = get_current_date()
        formatted_date = current_date.strftime("%B %d, %Y at %I:%M %p")
        new_content = re.sub(r'The data was last updated on: .*', f'The data was last updated on: {formatted_date}', content)
        
        with open(readme_path, 'w') as f:
            f.write(new_content)
        
        logger.info(f"Successfully updated README.md with timestamp: {formatted_date}")
        return True
    except Exception as e:
        logger.error(f"Error updating README.md: {e}")
        return False

def commit_and_push_changes():
    """Commit and push changes to the GitHub repository."""
    try:
        # Get the current date for the commit message
        current_date = get_current_date()
        formatted_date = current_date.strftime("%Y-%m-%d %H:%M:%S")
        
        # Commit the changes
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", f"Update calendar data - {formatted_date}"], check=True)
        
        # Push the changes
        subprocess.run(["git", "push", "-u", "origin", "main"], check=True)
        
        logger.info(f"Successfully committed and pushed changes at {formatted_date}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error in git operations: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False

def main():
    """Main function to update the school calendar data."""
    logger.info("Starting school calendar data update")
    
    # Change to the repository directory
    repo_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(repo_dir)
    
    # Create the JSON structure
    data = create_json_structure()
    
    # Validate the JSON structure
    if not validate_json_structure(data):
        logger.error("JSON structure validation failed")
        return False
    
    # Save the JSON to the file
    json_path = os.path.join(repo_dir, "school_calendar_data.json")
    if not save_json_to_file(data, json_path):
        logger.error("Failed to save JSON data to file")
        return False
    
    # Update the README.md file
    if not update_readme(data):
        logger.error("Failed to update README.md")
        # Continue anyway, this is not critical
    
    # Commit and push the changes
    if not commit_and_push_changes():
        logger.error("Failed to commit and push changes")
        return False
    
    logger.info("School calendar data update completed successfully")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

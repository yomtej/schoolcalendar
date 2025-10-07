# School Calendar Data

This repository contains the JSON data for the Hampstead Hill School Calendar application.

## Files

- `school_calendar_data.json` - The main data file containing all calendar information
- `README.md` - This documentation file

## Data Structure

The JSON data includes:

1. **School Information** - Basic details about Hampstead Hill School and the children
2. **Today & Tomorrow** - Complete daily information with weather and pickup details
3. **Events** - All school events, including past events from the current term
4. **Activities** - Regular activities and after-school clubs for each child
5. **Notices** - Important announcements and deadlines
6. **Calendar** - Monthly calendar with events marked on specific days

## Automated Updates

This repository is automatically updated twice daily:
- Morning update: 6:00 AM
- Evening update: 6:00 PM

## Integration

To use this data in your application:

1. Fetch the raw JSON data from: `https://raw.githubusercontent.com/yourusername/school-calendar-data/main/school_calendar_data.json`
2. Parse the JSON data in your application
3. Render the UI components based on the data

## Last Updated

The data was last updated on: October 07, 2025 at 08:19 AM

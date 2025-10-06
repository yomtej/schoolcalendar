#!/bin/bash

# This script schedules the update_calendar_data.py script to run twice daily

# Check if crontab is available
if ! command -v crontab &> /dev/null; then
    echo "crontab is not available. Please install it first."
    exit 1
fi

# Get the absolute path to the update script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UPDATE_SCRIPT="$SCRIPT_DIR/update_calendar_data.py"

# Create a temporary file for the crontab
TEMP_CRONTAB=$(mktemp)

# Export the current crontab
crontab -l > "$TEMP_CRONTAB" 2>/dev/null || echo "" > "$TEMP_CRONTAB"

# Check if the update script is already scheduled
if grep -q "$UPDATE_SCRIPT" "$TEMP_CRONTAB"; then
    echo "The update script is already scheduled. Removing the existing schedule."
    grep -v "$UPDATE_SCRIPT" "$TEMP_CRONTAB" > "${TEMP_CRONTAB}.new"
    mv "${TEMP_CRONTAB}.new" "$TEMP_CRONTAB"
fi

# Add the new schedule (6:00 AM and 6:00 PM)
echo "0 6,18 * * * $UPDATE_SCRIPT >> $SCRIPT_DIR/cron.log 2>&1" >> "$TEMP_CRONTAB"

# Install the new crontab
crontab "$TEMP_CRONTAB"

# Clean up
rm "$TEMP_CRONTAB"

echo "The update script has been scheduled to run at 6:00 AM and 6:00 PM daily."
echo "You can check the cron.log file in the repository directory for execution logs."

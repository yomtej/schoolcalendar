#!/bin/bash

# This script creates a GitHub repository and pushes the local repository to it

# Check if the GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo "GitHub CLI is not installed. Please install it first."
    exit 1
fi

# Check if the user is authenticated with GitHub
if ! gh auth status &> /dev/null; then
    echo "You are not authenticated with GitHub. Please run 'gh auth login' first."
    exit 1
fi

# Create the GitHub repository
echo "Creating GitHub repository..."
gh repo create school-calendar-data --public --description "JSON data for the Hampstead Hill School Calendar application" --source=. --push

echo "GitHub repository created and local repository pushed."
echo "You can now access the JSON data at: https://raw.githubusercontent.com/YOUR_USERNAME/school-calendar-data/main/school_calendar_data.json"
echo "Replace YOUR_USERNAME with your GitHub username."

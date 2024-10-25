#!/bin/bash

# Arguments
LIST_NAME=${1:-"Groceries"}
OUTPUT_PATH=${2:-"/path/to/grocery_data.csv"}
MODE=${3:-"simple"}

# Run AppleScript to extract data
osascript extract_reminders.scpt "$LIST_NAME" "$OUTPUT_PATH"
echo "Data extracted from Reminders app"

# Run Python script for analysis in specified mode
python3 analyze_grocery_categories.py --mode "$MODE" --input "$OUTPUT_PATH"

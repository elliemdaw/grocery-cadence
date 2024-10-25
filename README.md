# grocery-cadence
Use scripts and LLMs to analyze grocery purchases

# Grocery Purchase Pattern Analyzer

Things have been busy enough lately that I found myself wishing I had grocery auto-ordering set up. I wasn't sure on what cadences I buy things, but I have been keeping my grocery list in Apple Reminders for years. I add items there, then mark them Complete when I purchase the item.

This repo contains scripts to analyze grocery purchasing patterns from a structured csv with items and purchase date. It also has a script to extract this info from a Reminders list in the Apple's Reminders app. The analysis groups grocery items by similarity and calculates the cadence with which items are bought to recommend reorder schedules.

## Setup and Requirements

1. **AppleScript**: Extracts completed items from the specified Reminders list (Mac only).
2. **Bash Script**: Runs AppleScript (extract from specified Reminders list name, save to csv, run analysis)
3. **Python Script**: Analyzes data, provides item grouping and cadence analysis.
4. **Ollama**: Used for the complex mode in item grouping (requires [Gemma 2b model](https://ollama.com)).

### Install

```bash
git clone https://github.com/elliemdaw/grocery-cadence.git
cd grocery-cadence
```
(or fork a copy into your own repos)

### Usage

#### Setup
Highly recommend using a python virtual environment (for all python things :) ). After you've created one and started it...
`pip install requirements.txt`
`ollama serve`
`ollama run gemma2:2b`

In the project folder:
`chmod +x extract_and_analyze.sh`

If you're using the Apple Script, make sure your permissions are good to go:
System Preferences > Security & Privacy > Automation
make sure that iterminal/IDE is allowed access to the Reminders app.

#### Extract data and analyze in Simple or Complex mode

```bash
# Run extraction and analysis in simple mode
./extract_and_analyze.sh "<name of Reminders list>" "/path/to/grocery_data.csv" "simple"

# Run in complex mode (requires Ollama)
./extract_and_analyze.sh "<name of Reminders list>" "/path/to/grocery_data.csv" "complex"
```

#### Just use the analysis script

Use this if you aren't on a Mac or already have your grocery data.

The analysis script expects a csv with one header row and the two columns: item, purchase datetime "%Y-%m-%dT%H:%M:%S"

```bash
# Simple Mode
python3 analyze_grocery_categories.py --mode simple --input "/path/to/grocery_data.csv"

# Complex Mode
python3 analyze_grocery_categories.py --mode complex --input "/path/to/grocery_data.csv"
```

## Assumptions and Limitations

- On my machine, the complex method takes about 20 seconds to run (just using the python script)
- The Apple Script is **extremely** slow, to speed it up it grabs reminders for the prior 365 days
- Bash script calls the Apple Script, so therefore the bash script won't work on other platforms.
- Python script assumes a csv with one header row and two data columns (in order): item, purchase date formatted as "%Y-%m-%dT%H:%M:%S"
- The complex grouping requires Gemma2 to return JSON (I haven't had issues so far... *knock on wood*)
- This runs locally using Ollama, it isn't sending your grocery data to a cloud LLM

## Additional improvements TODO

- Better parsing in case of invalid JSON from LLM
- Configurability of model
- Source grocery data from elsewhere
- Speed up the Apple Script...
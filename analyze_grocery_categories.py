import argparse
import csv
from collections import defaultdict
from fuzzywuzzy import fuzz
from tabulate import tabulate
import datetime
import ollama
import matplotlib.pyplot as plt
import textwrap

# Set up command-line arguments
parser = argparse.ArgumentParser(description="Analyze grocery purchase patterns")
parser.add_argument("--mode", choices=["simple", "complex"], default="simple", help="Grouping mode. Simple uses fuzzy matching, complex uses Ollama to classify into groups.")
parser.add_argument("--input", default="grocery_data.csv", help="Path to grocery data CSV file")
args = parser.parse_args()

def wrap_text(text, width=120):
    return "\n".join(textwrap.wrap(text, width=width))

# Normalizes item names to handle minor variations (e.g., "bananas" vs "banana")
def normalize_item(item):
    if isinstance(item, tuple):
        item = item[0]
    return item.lower().rstrip('s')

def simple_grouping(items, threshold=80):
    groups = defaultdict(list)
    for item in items:
        item_name = item[0] if isinstance(item, tuple) else item
        matched = False
        for group_name in groups:
            if fuzz.ratio(normalize_item(item_name), group_name) > threshold:
                groups[group_name].append(item)
                matched = True
                break
        if not matched:
            groups[normalize_item(item_name)].append(item)
    return groups

def complex_grouping(items, groups=[]):
    unique_items = list(set([normalize_item(item[0]) for item in items]))
    prompt = f"""
    Categorize the following food items into specific, usage-based groups. 
    Create categories that group very similar items or items that would be used similarly in cooking or meal preparation. 
    If you are provided with category names below, use those. Otherwise, use your judgement to categorize. Avoid overly broad categories like 'produce' or 'protein'.

    Food items: {', '.join(unique_items)}
    Category names: {', '.join(groups)}

    Return your response in JSON format with the category name as a key and the list of items as the value. For example: {{"fresh fruit": ["apples", "bananas"], "frozen fruit": ["frozen strawberries", "frozen blueberries"]}}
    Only output JSON. Do not include any other text in your response. Just the JSON content.
    """
    
    try:
        response = ollama.generate(model="gemma2:2b", prompt=prompt)
    except Exception as e:
        print(f"Error generating ollama response: {e}")
        return defaultdict(list)
    
    print(f"Ollama response: {response['response']}")

    # Attempt to parse the response as JSON
    import json
    try:
        groups = json.loads(response['response'])
    except json.JSONDecodeError:
        print("Failed to decode JSON response; returning empty groups.")
        return defaultdict(list)

    # Map JSON categories to the original item list
    mapped_groups = defaultdict(list)
    for category, items_list in groups.items():
        for item in items_list:
            for original_item in items:
                if normalize_item(original_item[0]) == normalize_item(item):
                    mapped_groups[category].append(original_item)
    
    return mapped_groups

def group_similar_items(items, groups=[], method="simple"):
    if method == "simple":
        return simple_grouping(items)
    elif method == "complex":
        return complex_grouping(items, groups)
    else:
        raise ValueError("Method must be 'simple' or 'complex'")

# Analyzes item purchase cadence and frequency
def analyze_cadence(item_groups):
    cadence_results = []
    for group_name, items in item_groups.items():
        dates = sorted(set([datetime.datetime.strptime(item[1], "%Y-%m-%dT%H:%M:%S") for item in items]))
        if len(dates) > 1:
            intervals = [(dates[i+1] - dates[i]).days for i in range(len(dates)-1)]
            avg_interval = sum(intervals) / len(intervals)
            cadence_results.append((group_name, avg_interval, len(items)))
        else:
            cadence_results.append((group_name, 'Insufficient data', len(items)))
    return cadence_results

def suggest_recurring_orders(cadence_results):
    suggestions = []
    for item, cadence, frequency in cadence_results:
        if isinstance(cadence, (int, float)):
            if cadence <= 7:
                suggestions.append((item, "weekly"))
            elif cadence <= 14:
                suggestions.append((item, "bi-weekly"))
            elif cadence <= 30:
                suggestions.append((item, "monthly"))
            else:
                suggestions.append((item, f"every {int(cadence)} days"))
        else:
            suggestions.append((item, "insufficient data"))
    return suggestions

# Plots purchase frequency for each item
def plot_purchase_frequency(cadence_results):
    items, frequencies = zip(*[(item, freq) for item, _, freq in cadence_results if isinstance(freq, int)])
    plt.figure(figsize=(12, 6))
    plt.bar(items, frequencies)
    plt.title('Purchase Frequency of Grocery Items')
    plt.xlabel('Items')
    plt.ylabel('Number of Purchases')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('purchase_frequency.png')

# Main execution
grocery_data = []
with open(args.input, 'r') as f:
    reader = csv.reader(f)
    next(reader)  # Skip header
    grocery_data = [(row[0], row[1]) for row in reader]

# get custom groups from the user for complex mode
groups = input("What categories are you looking for? Use comma-separation. (optional, you can just press Enter): ").split(",") if args.mode == "complex" else []

item_groups = group_similar_items(grocery_data, groups, method=args.mode)
grouped_items_table = [
    (category, wrap_text(", ".join([item[0] for item in items])))
    for category, items in item_groups.items()
]
print("\nItem Categories:")
print(tabulate(grouped_items_table, headers=["Category", "Items"], tablefmt="grid"))

cadence_results = analyze_cadence(item_groups)
suggestions = suggest_recurring_orders(cadence_results)

# Print suggestions in a table format
suggestions_table = [(item, suggestion) for item, suggestion in suggestions if suggestion != "insufficient data"]
print("\nSuggested Reorder Timeline:")
print(tabulate(suggestions_table, headers=["Item", "Suggested Frequency"], tablefmt="grid"))

# Only plot if there is data
if cadence_results:
    plot_purchase_frequency(cadence_results)
    print("\nPurchase frequency plot saved as 'purchase_frequency.png'")
else:
    print("No cadence results to plot.")
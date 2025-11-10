#!/usr/bin/env python3
"""
Generate article cleanup rules based on always.csv patterns.

This script analyzes always.csv to find patterns where "Azure AI X" becomes just "X"
and generates corresponding "an X" -> "a X" cleanup rules.
"""

import os
import pandas as pd
from utils import generate_article_cleanup_rules

def main():
    debug_mode = os.getenv('DEBUG', '').lower() == 'true'
    
    # Generate article cleanup rules
    cleanup_rules = generate_article_cleanup_rules('patterns/always.csv', debug_mode)
    
    if not cleanup_rules:
        print("No article cleanup rules to generate")
        return
    
    # Load existing cleanup.csv
    cleanup_csv_path = 'patterns/cleanup.csv'
    existing_rules = []
    
    if os.path.exists(cleanup_csv_path):
        df = pd.read_csv(cleanup_csv_path)
        existing_rules = list(zip(df['search'], df['replace']))
        if debug_mode:
            print(f"Loaded {len(existing_rules)} existing cleanup rules")
    
    # Convert to sets for comparison
    existing_set = set(existing_rules)
    new_rules_set = set(cleanup_rules)
    
    # Find rules that need to be added
    rules_to_add = new_rules_set - existing_set
    
    if not rules_to_add:
        print("All article cleanup rules already exist in cleanup.csv")
        return
    
    print(f"Adding {len(rules_to_add)} new article cleanup rules:")
    
    # Combine existing and new rules
    all_rules = list(existing_set) + list(rules_to_add)
    
    # Create new DataFrame and save
    new_df = pd.DataFrame(all_rules, columns=['search', 'replace'])
    
    # Sort alphabetically by search term for consistency
    new_df = new_df.sort_values('search')
    
    # Save to CSV
    new_df.to_csv(cleanup_csv_path, index=False)
    
    print(f"Updated {cleanup_csv_path} with {len(all_rules)} total cleanup rules")
    
    # Show what was added
    if debug_mode:
        for search, replace in sorted(rules_to_add):
            print(f"  Added: '{search}' -> '{replace}'")

if __name__ == "__main__":
    main()
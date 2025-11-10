## Run this script to replace "Azure AI Foundry" terms in .yml/.yaml files
# This script goes through all .yml/.yaml files in sub-directories from the specified directory.
# It replaces "Azure AI Foundry" with "Microsoft Foundry" everywhere (no first mention logic).
# No "formerly" context preservation - all matches are replaced.
#
# Files used:
# - patterns/special.csv: Special patterns with exact replacements (optional)
# - patterns/always.csv: Compound phrases that always get specific replacements (optional)  
# - patterns/cleanup.csv: Final cleanup replacements applied after all other changes (optional)
#
# Environment variables:
# - DIRECTORY_PATH: Directory to process (required)
# - DEBUG: Set to 'true' to enable debug output (optional)  
import os
from dotenv import load_dotenv
from tqdm import tqdm
from utils import load_csv_replacements, protect_never_terms, restore_never_terms

# Load environment variables from .env file
load_dotenv()

# Get configuration from environment variables
path = os.getenv('DIRECTORY_PATH')
debug_mode = os.getenv('DEBUG', 'false').lower() in ('true', '1', 'yes')

if not path:
    print("Error: DIRECTORY_PATH not found in .env file")
    exit(1)

# Check if the path exists
if not os.path.exists(path):
    print(f"Error: Path does not exist: {path}")
    exit(1)
else:
    print(f"Processing directory: {path}")

# Load replacement patterns from CSV files
compound_replacements = load_csv_replacements('patterns/always.csv', 'compound replacements', debug_mode=debug_mode)
cleanup_replacements = load_csv_replacements('patterns/cleanup.csv', 'cleanup replacements', debug_mode=debug_mode)

# Load never-replace terms from never.csv
never_terms = []
if os.path.exists('patterns/never.csv'):
    import pandas as pd
    never_df = pd.read_csv('patterns/never.csv')
    never_terms = never_df['search'].tolist()
    if debug_mode:
        print(f"Loaded {len(never_terms)} never-replace terms from patterns/never.csv")
elif debug_mode:
    print("No patterns/never.csv found, no terms will be protected")

# Build list of YAML files to process
print("Scanning directory...")
files_to_process = []
for root, dirs, files in os.walk(path):
    for file in files:
        if file.endswith(('.yml', '.yaml')):
            files_to_process.append(os.path.join(root, file))

print(f"Found {len(files_to_process)} YAML files to process")

# Process files with progress bar
file_count = 0
with tqdm(files_to_process, desc="Processing files", unit="file") as pbar:
    for file_path in pbar:
        file_count += 1
        
        # Read the file
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        # Protect never-replace terms first
        content, never_replacements = protect_never_terms(content, never_terms, debug_mode)
        
        original_content = content
        
        # Apply compound phrases from always.csv
        for search_term, replace_term in compound_replacements.items():
            if search_term in content:
                old_content = content
                content = content.replace(search_term, replace_term)
                if debug_mode and content != old_content:
                    count = old_content.count(search_term)
                    print(f"  Modified {file_path}: {count} occurrence(s) '{search_term}' → '{replace_term}'")
        
        # Replace all "Azure AI Foundry" with "Microsoft Foundry" (no first mention logic)
        azure_ai_foundry_term = "Azure AI Foundry"
        if azure_ai_foundry_term in content:
            old_content = content
            content = content.replace(azure_ai_foundry_term, "Microsoft Foundry")
            if debug_mode and content != old_content:
                count = old_content.count(azure_ai_foundry_term)
                print(f"  Modified {file_path}: {count} occurrence(s) '{azure_ai_foundry_term}' → 'Microsoft Foundry'")
        
        # Apply cleanup replacements last (after all other changes)
        for search_term, replace_term in cleanup_replacements.items():
            if search_term in content:
                old_content = content
                content = content.replace(search_term, replace_term)
                if debug_mode and content != old_content:
                    count = old_content.count(search_term)
                    print(f"  Cleanup {file_path}: {count} occurrence(s) '{search_term}' → '{replace_term}'")
        
        # Restore never-replace terms
        content = restore_never_terms(content, never_replacements)
        
        # Write the file back only if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

print(f'✓ Completed! Total YAML files processed: {file_count}')
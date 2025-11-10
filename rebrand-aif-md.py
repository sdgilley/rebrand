## Run this script to replace "Azure AI Foundry" terms in .md files
# This script goes through all .md files in sub-directories from the specified directory.
# It replaces "Azure AI Foundry" with:
# - "Microsoft Foundry" in metadata sections and first occurrence in body
# - "Foundry" for subsequent occurrences in body
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
from utils import load_csv_replacements, safe_replace, protect_never_terms, restore_never_terms

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

# search through the directory and replace "Azure AI Foundry" terms only

# Load compound replacements from always.csv
compound_replacements = load_csv_replacements('patterns/always.csv', 'compound replacements', debug_mode=debug_mode)

# Load cleanup replacements from cleanup.csv (applied last)
cleanup_replacements = load_csv_replacements('patterns/cleanup.csv', 'cleanup replacements', debug_mode=debug_mode)

# Load never-replace terms from never.csv
never_df = None
never_terms = []
if os.path.exists('patterns/never.csv'):
    import pandas as pd
    never_df = pd.read_csv('patterns/never.csv')
    never_terms = never_df['search'].tolist()
    if debug_mode:
        print(f"Loaded {len(never_terms)} never-replace terms from patterns/never.csv")
elif debug_mode:
    print("No patterns/never.csv found, no terms will be protected")

# Build list of files to process first
print("Scanning directory...")
files_to_process = []
for root, dirs, files in os.walk(path):
    for file in files:
        if "new-name.md" in file: # special case: skip the new-name file which announces the change.
            continue
        if file.endswith('.md'):
            files_to_process.append(os.path.join(root, file))

print(f"Found {len(files_to_process)} files to process")

# Process files with progress bar
file_count = 0
with tqdm(files_to_process, desc="Processing files", unit="file") as pbar:
    for file_path in pbar:
        file_count += 1
        
        # read the file
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        # Protect never-replace terms first
        content, never_replacements = protect_never_terms(content, never_terms, debug_mode)
        
        # Special handling for "Azure AI Foundry" in .md files
        azure_ai_foundry_term = "Azure AI Foundry"
        original_content = content
        
        # Apply compound phrases from always.csv
        # These don't count as "first occurrence" - they get their specific replacements
        compound_changes = 0
        for search_term, replace_term in compound_replacements.items():
            if search_term in content:
                old_content = content
                content = safe_replace(content, search_term, replace_term, debug_mode=debug_mode)
                if content != old_content:
                    compound_changes += 1
                    if debug_mode:
                        count = old_content.count(search_term)
                        print(f"  Modified {file_path}: {count} occurrence(s) '{search_term}' → '{replace_term}'")
        
        if azure_ai_foundry_term in content:
            # In .md files, handle metadata and body separately
            # Split content into metadata (front matter) and body
            if content.startswith('---'):
                # Find the end of front matter
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    # parts[0] is empty, parts[1] is metadata, parts[2] is body
                    metadata = parts[1]
                    body = parts[2]
                    
                    # Replace ALL "Azure AI Foundry" in metadata with "Microsoft Foundry"
                    metadata = metadata.replace(azure_ai_foundry_term, "Microsoft Foundry")
                    
                    # Replace first occurrence in body with "Microsoft Foundry", rest with "Foundry"
                    if azure_ai_foundry_term in body:
                        body = safe_replace(body, azure_ai_foundry_term, "Microsoft Foundry", max_replacements=1, debug_mode=debug_mode)
                        body = safe_replace(body, azure_ai_foundry_term, "Foundry", debug_mode=debug_mode)
                    
                    # Reconstruct content
                    content = f"---{metadata}---{body}"
                    
                    # Debug output if enabled and changes were made
                    if debug_mode and content != original_content:
                        metadata_count = parts[1].count(azure_ai_foundry_term)
                        body_count = parts[2].count(azure_ai_foundry_term)
                        print(f"  Modified {file_path}: {metadata_count} in metadata, {body_count} in body")
                else:
                    # No proper front matter, treat as body only
                    content = safe_replace(content, azure_ai_foundry_term, "Microsoft Foundry", max_replacements=1, debug_mode=debug_mode)
                    content = safe_replace(content, azure_ai_foundry_term, "Foundry", debug_mode=debug_mode)
                    if debug_mode and content != original_content:
                        print(f"  Modified {file_path}: malformed front matter")
            else:
                # No front matter, treat as body only
                content = safe_replace(content, azure_ai_foundry_term, "Microsoft Foundry", max_replacements=1, debug_mode=debug_mode)
                content = safe_replace(content, azure_ai_foundry_term, "Foundry", debug_mode=debug_mode)
                if debug_mode and content != original_content:
                    print(f"  Modified {file_path}: no front matter")
        
        # Apply cleanup replacements last (after all other changes)
        cleanup_changes = 0
        for search_term, replace_term in cleanup_replacements.items():
            if search_term in content:
                old_content = content
                content = content.replace(search_term, replace_term)
                if content != old_content:
                    cleanup_changes += 1
                    if debug_mode:
                        count = old_content.count(search_term)
                        print(f"  Cleanup {file_path}: {count} occurrence(s) '{search_term}' → '{replace_term}'")
        
        # Restore never-replace terms
        content = restore_never_terms(content, never_replacements)
        
        # write the file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

print(f'✓ Completed! Total files processed: {file_count}')
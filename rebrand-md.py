## Run this script to replace terms in .md files with first mention logic
# This script goes through all .md files in sub-directories from the specified directory.
# It uses first mention differentiation for all patterns in first_mention.csv:
# - All metadata and title occurrences get first replacement term
# - First occurrence in body gets first replacement term  
# - Subsequent occurrences in body get second replacement term
#
# Files used:
# - patterns/first_mention.csv: First mention differentiation (term,first_replace,subsequent_replace)
# - patterns/always.csv: Compound phrases that always get specific replacements (optional)
# - patterns/cleanup.csv: Final cleanup replacements applied after all other changes (optional)
# - patterns/skip_folders.csv: Folder names to skip during directory traversal (optional)
#
# Environment variables:
# - DIRECTORY_PATH: Directory to process (required)
# - DEBUG: Set to 'true' to enable debug output (optional)  
import os
from dotenv import load_dotenv
from tqdm import tqdm
from utils import load_csv_replacements, safe_replace, protect_never_terms, restore_never_terms, first_mention_replace_in_body, load_first_mention_csv

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

# Load replacement patterns from CSV files
first_mention_replacements = load_first_mention_csv('patterns/first_mention.csv', debug_mode=debug_mode)
compound_replacements = load_csv_replacements('patterns/always.csv', 'compound replacements', debug_mode=debug_mode)
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

# Load skip folders from skip_folders.csv
skip_folders = []
if os.path.exists('patterns/skip_folders.csv'):
    skip_df = pd.read_csv('patterns/skip_folders.csv')
    skip_folders = skip_df['folder_name'].tolist()
    if debug_mode:
        print(f"Loaded {len(skip_folders)} folders to skip from patterns/skip_folders.csv")
elif debug_mode:
    print("No patterns/skip_folders.csv found, no folders will be skipped")

# Build list of files to process first
print("Scanning directory...")
files_to_process = []
for root, dirs, files in os.walk(path):
    # Skip directories that are in the skip list
    original_dirs = dirs[:]  # Make a copy to see what was skipped
    dirs[:] = [d for d in dirs if d not in skip_folders]
    
    # Print skipped directories
    skipped_dirs = [d for d in original_dirs if d in skip_folders]
    for skipped_dir in skipped_dirs:
        full_skipped_path = os.path.join(root, skipped_dir)
        print(f"Skipped: {full_skipped_path}")
    
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
        
        original_content = content
        
        # Apply first mention replacements (metadata + title + body first mention logic)
        for term, first_replace, subsequent_replace in first_mention_replacements:
            if term in content:
                old_content = content
                content = first_mention_replace_in_body(content, term, first_replace, subsequent_replace, debug_mode)
                if debug_mode and content != old_content:
                    print(f"  Applied first mention rule for '{term}' in {file_path}")
        
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
## Run this script to fix bookmarks and cleanup replacements in .md files
# This script goes through all .md files in sub-directories from the specified directory.
# It only applies cleanup replacements from cleanup.csv - typically bookmark fixes.
# Unlike the main rebrand script, this does NOT skip any folders.
#
# Files used:
# - patterns/cleanup.csv: Cleanup replacements (typically bookmark fixes)
# - patterns/never.csv: Terms to protect from replacement (optional)
#
# Environment variables:
# - DIRECTORY_PATH: Directory to process (required)
# - DEBUG: Set to 'true' to enable debug output (optional)  

import os
import codecs
from dotenv import load_dotenv
from tqdm import tqdm
from utils import load_csv_replacements, protect_never_terms, restore_never_terms, word_boundary_replace

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
    print(f"Processing directory for bookmark cleanup: {path}")

# Load cleanup replacements from CSV file
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

# Build list of files to process first (NO FOLDER SKIPPING)
print("Scanning directory (processing ALL folders)...")
files_to_process = []
for root, dirs, files in os.walk(path):
    # NO folder skipping - process everything
    for file in files:
        if "new-name.md" in file: # special case: skip the new-name file which announces the change.
            continue
        if file.endswith('.md'):
            files_to_process.append(os.path.join(root, file))

print(f"Found {len(files_to_process)} files to process")

# Process files with progress bar
file_count = 0
total_changes = 0
with tqdm(files_to_process, desc="Processing files for cleanup", unit="file") as pbar:
    for file_path in pbar:
        file_count += 1
        
        # Read the file in binary mode to make the following steps possible:
        # - Detect a byte-order mark (BOM) if one is present.
        # - Preserve the original line-ending characters.
        with open(file_path, 'rb') as f:
            raw = f.read()
        
        # Check for a BOM.
        has_utf8_bom = raw.startswith(codecs.BOM_UTF8)
        
        # Decode the file to text.
        content = raw.decode('utf-8-sig')
        
        # Protect never-replace terms first
        content, never_replacements = protect_never_terms(content, never_terms, debug_mode)
        
        original_content = content
        
        # Apply cleanup replacements (typically bookmark fixes)
        cleanup_changes = 0
        for search_term, replace_term in cleanup_replacements.items():
            if search_term in content:
                old_content = content
                # Use word-boundary replace to avoid partial word matches.
                content = word_boundary_replace(content, search_term, replace_term, debug_mode)
                if content != old_content:
                    cleanup_changes += 1
                    if debug_mode:
                        count = old_content.count(search_term)
                        print(f"  Cleanup {file_path}: {count} occurrence(s) '{search_term}' → '{replace_term}'")
        
        # Restore never-replace terms
        content = restore_never_terms(content, never_replacements)
        
        # Only write if there were changes
        if content != original_content:
            total_changes += 1
            # Encode the file back to UTF-8 bytes.
            outContentWithBOMPreserved = content.encode('utf-8')
            
            # If the file originally had a BOM, add one back in.
            if has_utf8_bom:
                outContentWithBOMPreserved = codecs.BOM_UTF8 + outContentWithBOMPreserved
            
            # Write the modified content to the file.
            with open(file_path, 'wb') as f:
                f.write(outContentWithBOMPreserved)

print(f'✓ Completed! Total files processed: {file_count}')
print(f'✓ Files modified: {total_changes}')
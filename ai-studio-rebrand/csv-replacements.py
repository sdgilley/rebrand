## Run this script to make CSV-based replacements in .md files
# This script goes through all .md files in sub-directories from the specified directory.
# It applies all replacements from the CSV file EXCEPT "Azure AI Foundry" 
# (which should be handled by rebrand-aif-md.py)
#
# Environment variables:
# - DIRECTORY_PATH: Directory to process (required)
# - REPLACEMENTS_FILE: CSV file with replacements (default: microsoft.csv)
# - DEBUG: Set to 'true' to enable debug output (optional)

import os
import pandas as pd
from dotenv import load_dotenv
from tqdm import tqdm

# Load environment variables from .env file
load_dotenv()

# Get configuration from environment variables
path = os.getenv('DIRECTORY_PATH')
replacements_file = os.getenv('REPLACEMENTS_FILE', 'microsoft.csv')
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

# Read replacements from CSV file
if not os.path.exists(replacements_file):
    print(f"Error: Replacements file does not exist: {replacements_file}")
    exit(1)

replacements = pd.read_csv(replacements_file).to_dict('records')
print(f"Using replacements file: {replacements_file}")

# Filter out "Azure AI Foundry" replacement if it exists
original_count = len(replacements)
replacements = [r for r in replacements if r['search'] != 'Azure AI Foundry']
filtered_count = len(replacements)

if original_count != filtered_count:
    print(f"Filtered out {original_count - filtered_count} 'Azure AI Foundry' replacement(s)")
print(f"Loaded {filtered_count} replacement rules")

# Build list of files to process first
print("Scanning directory...")
files_to_process = []
for root, dirs, files in os.walk(path):
    for file in files:
        if "new-name.md" in file:  # special case for ai-studio: skip the new-name file
            continue
        if file.endswith('.md'):
            files_to_process.append(os.path.join(root, file))

print(f"Found {len(files_to_process)} files to process")

# Process files with progress bar
file_count = 0
modified_files = 0

with tqdm(files_to_process, desc="Processing files", unit="file") as pbar:
    for file_path in pbar:
        file_count += 1
        
        # Read the file
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                original_content = f.read()
        except UnicodeDecodeError:
            if debug_mode:
                print(f"  Skipped {file_path}: encoding error")
            continue
        
        content = original_content
        replacements_made = 0
        
        # Apply all CSV replacements
        for replacement in replacements:
            old_content = content
            content = content.replace(replacement['search'], replacement['replace'])
            if content != old_content:
                replacements_made += 1
        
        # Write the file if changes were made
        if content != original_content:
            modified_files += 1
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            if debug_mode:
                print(f"  Modified {file_path}: {replacements_made} replacement(s) applied")

print(f'✓ Completed! Total files processed: {file_count}, Files modified: {modified_files}')
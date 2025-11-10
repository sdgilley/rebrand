## Run this script to make replacements in your local repository
# This script goes through all sub-directories from the specified directory.
# use this script separately for ai-studio, ai-services, and machine-learning directories
# each of these directories has a large number of replacements, and should be done in 
# separate PRs to avoid merge conflicts
# use replacements-other.py which combines all other directories in the repo.  
import os
import pandas as pd
from dotenv import load_dotenv
from tqdm import tqdm

# Load environment variables from .env file
load_dotenv()

# Get configuration from environment variables
path = os.getenv('DIRECTORY_PATH')
replacements_file = os.getenv('REPLACEMENTS_FILE', 'microsoft.csv')  # default to microsoft.csv if not set

if not path:
    print("Error: DIRECTORY_PATH not found in .env file")
    exit(1)

# Check if the path exists
if not os.path.exists(path):
    print(f"Error: Path does not exist: {path}")
    exit(1)
else:
    print(f"Processing directory: {path}")

# search through the directory and replace terms
# read replacements from csv file:
if not os.path.exists(replacements_file):
    print(f"Error: Replacements file does not exist: {replacements_file}")
    exit(1)

replacements = pd.read_csv(replacements_file).to_dict('records')
print(f"Using replacements file: {replacements_file}")
print(f"Loaded {len(replacements)} replacement rules")
# ml replacements does NOT have studio UI replaced with AI Foundry portal!  All other directories do.
# if "articles/machine-learning" in path:
#     # remove the studio UI replacement
#     replacements = [replacement for replacement in replacements if replacement['search'] != 'Studio UI']
#     replacements = [replacement for replacement in replacements if replacement['search'] != 'studio UI']

# Build list of files to process first
print("Scanning directory...")
files_to_process = []
for root, dirs, files in os.walk(path):
    for file in files:
        if "new-name.md" in file: # special case for ai-studio: skip the new-name file which is supposed to contain AI Studio!
            continue
        if file.endswith('.md') or file.endswith('.yml'):
            files_to_process.append(os.path.join(root, file))

print(f"Found {len(files_to_process)} files to process")

# Process files with progress bar
file_count = 0
with tqdm(files_to_process, desc="Processing files", unit="file") as pbar:
    for file_path in pbar:
        file_count += 1
        
        # read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        # replace terms
        for replacement in replacements:
            content = content.replace(replacement['search'], replacement['replace'])
        # write the file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

print(f'✓ Completed! Total files processed: {file_count}')
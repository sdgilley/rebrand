## Run this script to make replacements in your local repository
# This script goes through all sub-directories from the specified directory.
# use this script separately for ai-studio, ai-services, and machine-learning directories
# each of these directories has a large number of replacements, and should be done in 
# separate PRs to avoid merge conflicts
# use replacements-other.py which combines all other directories in the repo.  
import os
import pandas as pd

# Specify you path for the directory
# make sure you have checked out the branch you want to use for the replacements
path = 'C:/GitPrivate/azure-ai-docs-pr2/articles/ai-studio/' # machine-learning dir

# search through the directory and replace terms
# read replacements from csv file:
replacements = pd.read_csv('replacements.csv').to_dict('records') # machine-learning dir
# ml replacements does NOT have studio UI replaced with AI Foundry portal!  All other directories do.
if "articles/machine-learning" in path:
    # remove the studio UI replacement
    replacements = [replacement for replacement in replacements if replacement['search'] != 'Studio UI']
    replacements = [replacement for replacement in replacements if replacement['search'] != 'studio UI']

# loop through all directories in the path, 
# and all files in the directories
for root, dirs, files in os.walk(path):
    for file in files:
        if "new-name.md" in file: # special case for ai-studio: skip the new-name file which is supposed to contain AI Studio!
            continue
        if file.endswith('.md')  or file.endswith('.yml'):
            # read the file
            with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                content = f.read()
            # replace terms
            for replacement in replacements:
                content = content.replace(replacement['search'], replacement['replace'])
            # write the file
            with open(os.path.join(root, file), 'w', encoding='utf-8') as f:
                f.write(content)
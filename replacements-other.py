## Run this script to make replacements in your local repository
# This script goes through all sub-directories from the specified directory.

import os
import pandas as pd

# Specify you path for the directory
# make sure you have checked out the branch you want to use for the replacements
path = 'C:/GitPrivate/azure-ai-docs-pr2/articles/'

# search through the directory and replace terms
# read replacements from csv file:
# replacements = pd.read_csv('ml-replacements.csv').to_dict('records') # machine-learning dir
replacements = pd.read_csv('replacements.csv').to_dict('records') # all other dirs

# loop through all directories in the path, 
# and all files in the directories
for root, dirs, files in os.walk(path):
    # skip the ai-services, ai-studio, and machine-learning directories:
    if 'ai-services' in root or 'ai-studio' in root or 'machine-learning' in root:
        continue
    for file in files:
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
import re
import os

# Specify you path for the directory
# make sure you have checked out the branch you want to use for the replacements
path = 'C:/GitPrivate/azure-ai-docs-pr2/articles/' 

# Define the pattern to find "AI Foundry" not preceded by "Azure"
pattern = re.compile(r'(?<!Azure )AI Foundry')

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
            content = pattern.sub('Azure AI Foundry', content)
            # write the file
            with open(os.path.join(root, file), 'w', encoding='utf-8') as f:
                f.write(content)
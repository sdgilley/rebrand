# rebrand

Helpful script for rebranding

## Prerequisites

To run the script, you need to have Python installed on your machine. You can download it from [here](https://www.python.org/downloads/).

You'll also need to install `pandas` library. You can do this by running the following command in your terminal:

```bash
pip install pandas
``` 

## Run the script to replace terms

Edit the `replacements.py` script to provide the location of the local directory which contains the files you want to rebrand.  The script will search for all files in the directory and its subdirectories.

The script will search and replace terms in the order they appear in the `replacements.csv` file. 

The way to use this script is as follows:

1. Create a new branch from upstream main.
1. Run the script to rebrand files in the appropriate directory.
1. Check the diffs to see if you get what you expect, and that unintended changes are not made.
1. If you find instance where you need to add more to the list:
    1. Add the new term to the `replacements.csv` file.
    1. Select all changes in your branch and discard them, so you can start with a clean branch.
    1. Run the script again.
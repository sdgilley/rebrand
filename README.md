# Azure AI Foundry Rebranding Scripts

Specialized scripts for replacing terminology across markdown and YAML files, with intelligent **first mention differentiation** and context preservation.

![Rebrand Tool](media/replace.png)

## Prerequisites

- Python 3.7+ installed on your machine. You can download it from the [official Python website](https://www.python.org/downloads/).

<details>
<summary><h2>Setup</h2></summary>

1. **Clone this repository** and navigate to the project directory:

   ```bash
   cd rebrand
   ```

1. **Create a virtual environment** (recommended):

   ```bash
   python -m venv venv
   ```

1. **Activate the virtual environment**:
   - On Windows (PowerShell): `.\venv\Scripts\Activate.ps1`
   - On Windows (Command Prompt): `.\venv\Scripts\activate.bat`
   - On macOS/Linux: `source venv/bin/activate`

1. **Install required packages**:

   ```bash
   pip install -r requirements.txt
   ```

</details>

## Configuration

**Edit the `.env` file** to specify the directory to process:

```env
# Directory path to process
DIRECTORY_PATH=C:\path\to\your\target\directory
```

## Edit patterns

The scripts use CSV configuration files in the `patterns/` folder:

- `never.csv` - Terms that should never be changed
- `always.csv` - Terms that are always replaced
- `first_mention.csv` - First mention differentiation rules (term,first_replace,subsequent_replace)
- `cleanup.csv` - Final cleanup replacements applied last.  Add bookmark replacements in here as well as common misspelling or punctuation you want to fix.
- `skip_folders.csv` - Folder names to skip during directory traversal (used by `rebrand-md.py` and `rebrand-yml.py`, but NOT by `fix-bookmarks.py`)

⚠️ When you modify either `first_mention.sv` or `always.csv` - run `generate_article_cleanup.py` afterwards to take care of variations of AN Azure that should now ready A XXX. These will be added to the `cleanup.csv` file.
> ⚠️⚠️Make sure you REVIEW the new `cleanup.csv file` to verify that the new replacements are correct.

## Usage

1. **Create a new branch** in your fork of azure-ai-docs-pr, based on your release branch.

1. **Run the appropriate script** from this repo:

   ```bash
   # For markdown files (with folder skipping)
   python rebrand-md.py
   
   # For YAML files  (with folder skipping)
   python rebrand-yml.py
   
   # For extra bookmark cleanup (processes ALL folders)
   # only needed if warnings appear in files outside the folders you rebranded. 
   # files inside will already have the bookmarks replaced. 
   python fix-bookmarks.py
   ```


1. **Review the changes**:
   - Check git diffs in your fork to verify expected changes
   - Ensure historical contexts are preserved
   - Verify never-replace terms remain unchanged

1. If you find more terms you want to add to one of the files, just select all and discard changes in your fork to start again.

## What it doesn't do

If you only use the scripts on a sub-folder, make sure you also check these files outside that folder:

- Zone pivots
- docFx.json - check here for things like the titleSuffix

<details>
<summary><h2>How It Works</h2></summary>

### Markdown Files (`rebrand-md.py`)

This script implements replacement logic for `.md` files with **first mention differentiation**:

1. **First Mention Logic for ALL patterns** from `first_mention.csv`:
   - **Metadata & Titles**: All occurrences → First replacement term
   - **Body**: First occurrence → First replacement term, Subsequent → Second replacement term
   - **Example**: "Azure AI Foundry" → "Microsoft Foundry" (first), then "Foundry" (subsequent)

1. **Context Preservation**: Preserves historical references with "formerly", "previously", "originally"

1. **Directory Skipping**: Uses `patterns/skip_folders.csv` to skip specified folders during processing (e.g., `content-safety`, `anomaly-detector`)

1. **Files Used**:
   - `patterns/first_mention.csv` - First mention differentiation rules (term,first_replace,subsequent_replace)
   - `patterns/never.csv` - Protected terms that should never change
   - `patterns/always.csv` - Compound phrases and special replacements
   - `patterns/cleanup.csv` - Final cleanup replacements
   - `patterns/skip_folders.csv` - Folder names to skip during directory traversal

1. **Processing Order**:
   - Load and protect never-replace terms
   - Apply first mention logic from `first_mention.csv`
   - Apply compound phrases from `always.csv`
   - Apply final cleanup from `cleanup.csv`
   - Restore protected terms

1. **Smart Section Detection**:
   - Detects YAML front matter automatically
   - Identifies title headings (# heading)
   - Applies appropriate rules to each section

### YAML Files (`rebrand-yml.py`)

This script applies **uniform replacement** to `.yml/.yaml` files using terms from `first_mention.csv`:

1. **Uniform Replacement for ALL patterns** from `first_mention.csv`:
   - ALL occurrences → First replacement term (no differentiation)
   - **Example**: "Azure AI Foundry" → "Microsoft Foundry" (all occurrences)
   - **Example**: "Azure AI Speech" → "Speech in Foundry Tools" (all occurrences)

1. **Context Preservation**: Preserves historical references with "formerly", "previously", "originally"

1. **Directory Skipping**: Uses `patterns/skip_folders.csv` to skip specified folders during processing

1. **Files Used**:
   - `patterns/first_mention.csv` - Terms with uniform replacement (uses first_replace column)
   - `patterns/never.csv` - Protected terms that should never change
   - `patterns/always.csv` - Compound phrases and special replacements
   - `patterns/cleanup.csv` - Final cleanup replacements
   - `patterns/skip_folders.csv` - Folder names to skip during directory traversal
   - `patterns/skip_folders.csv` - Folder names to skip during directory traversal (used by `rebrand-md.py` and `rebrand-yml.py`, but NOT by `fix-bookmarks.py`)

1. **Processing Order**:
   - Load and protect never-replace terms
   - Apply uniform replacements from `first_mention.csv` (using first_replace)
   - Apply compound phrases from `always.csv`
   - Apply cleanup from `cleanup.csv`
   - Restore protected terms

### Bookmark Cleanup (`fix-bookmarks.py`)

This script applies **only cleanup replacements** to fix bookmarks and links across ALL directories:

1. **Cleanup-Only Processing**:
   - Processes ALL folders (no directory skipping)
   - Only applies replacements from `cleanup.csv`
   - Ideal for fixing bookmarks in files that are normally skipped

1. **Use Cases**:
   - Fix bookmark references in skipped directories (e.g., content-safety)
   - Apply cleanup patterns without other replacements
   - Safe to run multiple times (cleanup patterns are typically harmless)

1. **Files Used**:
   - `patterns/cleanup.csv` - Cleanup replacements (typically bookmark fixes)
   - `patterns/never.csv` - Protected terms that should never change

1. **Processing Order**:
   - Load and protect never-replace terms
   - Apply cleanup replacements from `cleanup.csv`
   - Restore protected terms
   - Report number of files modified

</details>


<details>
<summary><h2>Files</h2></summary>

### Core Scripts

- `rebrand-md.py` - Main script for markdown files with first mention logic
- `rebrand-yml.py` - Script for YAML files with uniform replacement
- `fix-bookmarks.py` - Bookmark cleanup script (processes ALL folders)
- `utils.py` - Shared utility functions for all scripts

### Configuration Files

- `.env` - Directory path configuration
- `patterns/first_mention.csv` - First mention differentiation rules
- `patterns/always.csv` - Compound phrases and special formatting replacements
- `patterns/cleanup.csv` - Final cleanup replacements
- `patterns/never.csv` - Protected terms that should never change

### Dependencies

- `requirements.txt` - Python package dependencies

</details>
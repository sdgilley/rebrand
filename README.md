# rebrand

Helpful script for rebranding text across multiple files in a directory.

## Prerequisites

- Python 3.7+ installed on your machine. You can download it from the [official Python website](https://www.python.org/downloads/).

## Setup

1. **Clone this repository** and navigate to the project directory:

   ```bash
   cd rebrand
   ```

2. **Create a virtual environment** (recommended):

   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - On Windows (PowerShell): `.\venv\Scripts\Activate.ps1`
   - On Windows (Command Prompt): `.\venv\Scripts\activate.bat`
   - On macOS/Linux: `source venv/bin/activate`

4. **Install required packages**:

   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. **Edit the `.env` file** to specify your configuration:

   ```env
   # Directory path to process
   DIRECTORY_PATH=C:\path\to\your\target\directory
   
   # CSV file containing search and replace terms
   REPLACEMENTS_FILE=microsoft.csv
   ```

2. **Edit your CSV file** (e.g., `microsoft.csv`) with search and replace terms:

   ```csv
   search,replace
   Azure AI Foundry,Microsoft Foundry
   old-term,new-term
   ```

## Usage

1. **Create a new branch** from upstream main in your target repository:

   ```bash
   git checkout -b rebrand-updates
   ```

2. **Run the script**:

   ```bash
   python replacements.py
   ```
   
   The script will:
   - Process all `.md` and `.yml` files in the specified directory
   - Show progress and total files processed
   - Make replacements based on your CSV file

3. **Review the changes**:
   - Check the diffs to verify expected changes
   - Ensure no unintended changes were made

4. **If you need to add more replacements**:
   - Add new terms to your CSV file
   - Discard all changes in your branch to start clean
   - Run the script again

## Files

- `replacements.py` - Main script for processing files
- `.env` - Configuration file for paths and settings
- `requirements.txt` - Python package dependencies
- `microsoft.csv` - Example CSV file with replacement rules
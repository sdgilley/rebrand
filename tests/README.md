# Test Scripts

This directory contains test scripts and test data for the rebrand project.

## Files

### `test_safe_replace.py`
Test script for the `safe_replace` function that demonstrates how it preserves "formerly" contexts while making replacements elsewhere.

**Usage:**
```bash
cd c:\git\rebrand
.\venv\Scripts\python.exe tests\test_safe_replace.py
```

**Expected output:**
- Shows original text with multiple "Azure AI Services" references
- Demonstrates that references in "formerly/previously/originally" contexts are preserved
- Shows that regular references are replaced with "Foundry Tools"

### `test_yaml_replacements.py`
Test script for YAML file replacement functionality that demonstrates how the YAML script works differently from markdown.

**Usage:**
```bash
cd c:\git\rebrand
.\venv\Scripts\python.exe tests\test_yaml_replacements.py
```

**Expected output:**
- Shows original YAML content with multiple "Azure AI Foundry" references
- Demonstrates that ALL references are replaced with "Microsoft Foundry" (no "formerly" preservation)
- Shows the simulated result of running the YAML replacement script

### `test-yaml-replacements.yml` 
Test YAML file containing various "Azure AI Foundry" references for testing the YAML replacement logic.

**Contents:**
- Multiple "Azure AI Foundry" mentions in different YAML contexts (all should be replaced)
- Comments about "formerly" contexts (should also be replaced, unlike in markdown)
- Various YAML structures: metadata, config, resources, steps

### `test-formerly.md`
Test markdown file containing various "formerly" context examples for testing the markdown replacement logic.

**Contents:**
- Regular "Azure AI Services" mentions (should be replaced)
- Parenthetical "formerly referred to as Azure AI Services" (should be preserved)
- Parenthetical "previously called Azure AI Services" (should be preserved)  
- Parenthetical "originally known as Azure AI Services" (should be preserved)

## Running Tests

To run the tests, make sure you're in the root directory and use the virtual environment:

```bash
cd c:\git\rebrand
.\venv\Scripts\python.exe tests\test_safe_replace.py
```
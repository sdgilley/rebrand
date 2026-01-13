#!/usr/bin/env python3
## Run this script to rebrand both .md and .yml files
# This script runs both rebrand-md.py and rebrand-yml.py functions
# to perform a complete rebranding of Markdown and YAML files.
#
# Environment variables required:
# - DIRECTORY_PATH: Directory to process (required)
# - DEBUG: Set to 'true' to enable debug output (optional)
#
# Usage:
#   python rebrand-all.py
#
# Or with environment variables:
#   DIRECTORY_PATH=/path/to/docs DEBUG=true python rebrand-all.py

import sys
import os
from dotenv import load_dotenv
from rebrand_md import rebrand_markdown_files
from rebrand_yml import rebrand_yaml_files

# Load environment variables from .env file
load_dotenv()

# Get configuration from environment variables
path = os.getenv('DIRECTORY_PATH')
debug_mode = os.getenv('DEBUG', 'false').lower() in ('true', '1', 'yes')

if not path:
    print("Error: DIRECTORY_PATH not found in .env file")
    sys.exit(1)

# Check if the path exists
if not os.path.exists(path):
    print(f"Error: Path does not exist: {path}")
    sys.exit(1)

print(f"Starting complete rebranding process for: {path}")
print("=" * 60)

# Run rebrand markdown files
print("\n[1/2] Processing Markdown files (.md)...")
print("-" * 60)
md_count = rebrand_markdown_files(path=path, debug_mode=debug_mode)

# Run rebrand yaml files
print("\n[2/2] Processing YAML files (.yml/.yaml)...")
print("-" * 60)
yml_count = rebrand_yaml_files(path=path, debug_mode=debug_mode)

print("\n" + "=" * 60)
print(f"✓ Rebranding process completed successfully!")
print(f"  - Markdown files processed: {md_count}")
print(f"  - YAML files processed: {yml_count}")


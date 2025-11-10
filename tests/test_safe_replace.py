#!/usr/bin/env python3
"""Test script for the safe_replace function"""

import sys
import os

# Add parent directory to path to import utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import safe_replace

# Test wrapper function
def test_safe_replace_with_output(text, search_term, replace_term, max_replacements=None):
    """Wrapper that calls safe_replace and shows debug output."""
    result = safe_replace(text, search_term, replace_term, max_replacements, debug_mode=True)
    return result

# Test cases
test_text = """Azure AI Services is a great platform.

But note that (formerly referred to as Azure AI Services resources) are still supported.

Azure AI Services provides many capabilities.

More content about (previously called Azure AI Services) here.

Additional Azure AI Services features.

And (originally known as Azure AI Services platform) documentation.

Final Azure AI Services mention."""

print("Original text:")
print(test_text)
print("\n" + "="*50 + "\n")

# Test safe_replace
result = test_safe_replace_with_output(test_text, "Azure AI Services", "Foundry Tools")

print("After safe_replace:")
print(result)
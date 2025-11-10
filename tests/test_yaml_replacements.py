#!/usr/bin/env python3
"""Test script for YAML file replacements"""

import sys
import os
import shutil

# Add parent directory to path to import utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_yaml_replacements():
    """Test the YAML replacement functionality"""
    
    # Create a copy of the test file to work with
    test_file_original = "tests/test-yaml-replacements.yml" 
    test_file_copy = "tests/test-yaml-copy.yml"
    
    # Read original content
    with open(test_file_original, 'r') as f:
        original_content = f.read()
    
    print("Original YAML content:")
    print("=" * 50)
    print(original_content)
    print("=" * 50)
    
    # Create a copy to test on
    shutil.copy2(test_file_original, test_file_copy)
    
    print("\nSimulating YAML replacements...")
    print("This would replace:")
    print("- All 'Azure AI Foundry' → 'Microsoft Foundry'")
    print("- Apply special patterns, compound phrases, and cleanup")
    print("- No 'formerly' context preservation (unlike markdown)")
    
    # Simulate the replacements that would happen
    modified_content = original_content
    
    # Simple replacement simulation (the actual script would use CSV patterns)
    azure_ai_foundry_count = modified_content.count("Azure AI Foundry")
    modified_content = modified_content.replace("Azure AI Foundry", "Microsoft Foundry")
    
    print(f"\nWould replace {azure_ai_foundry_count} occurrences of 'Azure AI Foundry'")
    print("\nModified content would be:")
    print("=" * 50) 
    print(modified_content)
    print("=" * 50)
    
    # Clean up the copy
    if os.path.exists(test_file_copy):
        os.remove(test_file_copy)
    
    print(f"\n✓ Test completed! Found {azure_ai_foundry_count} replacements in YAML file")

if __name__ == "__main__":
    test_yaml_replacements()
#!/usr/bin/env python3
"""Test script for never.csv protection functionality"""

import sys
import os

# Add parent directory to path to import utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import protect_never_terms, restore_never_terms

def test_never_protection():
    """Test the never-replace protection functionality"""
    
    # Sample content with terms that should be protected
    test_content = """
This content mentions Azure AI Services (legacy) which should be protected.

But regular Azure AI Services should be replaced.

The API endpoint https://azure.microsoft.com/services/cognitive-services/ should not change.

However, other Azure AI Services references should be updated.

Code like Microsoft.CognitiveServices and azure-ai-services-python should remain unchanged.

Regular mentions of Azure AI Services should still be replaced though.
"""
    
    # Terms to protect (from never.csv)
    never_terms = [
        "Azure AI Services (legacy)",
        "https://azure.microsoft.com/services/cognitive-services/",
        "Microsoft.CognitiveServices", 
        "azure-ai-services-python"
    ]
    
    print("Original content:")
    print("=" * 60)
    print(test_content)
    print("=" * 60)
    
    # Step 1: Protect never-replace terms
    protected_content, replacements_map = protect_never_terms(test_content, never_terms, debug_mode=True)
    
    print("\nAfter protecting never-replace terms:")
    print("=" * 60)
    print(protected_content)
    print("=" * 60)
    print(f"Replacements map: {replacements_map}")
    
    # Step 2: Simulate normal replacement (this would happen in the main script)
    processed_content = protected_content.replace("Azure AI Services", "Foundry Tools")
    
    print("\nAfter simulated replacements:")
    print("=" * 60)
    print(processed_content)
    print("=" * 60)
    
    # Step 3: Restore never-replace terms
    final_content = restore_never_terms(processed_content, replacements_map)
    
    print("\nFinal content (never-terms restored):")
    print("=" * 60)
    print(final_content)
    print("=" * 60)
    
    # Verify protection worked
    protected_terms_preserved = all(term in final_content for term in never_terms)
    regular_terms_replaced = "Foundry Tools" in final_content
    
    print(f"✓ Protected terms preserved: {protected_terms_preserved}")
    print(f"✓ Regular terms replaced: {regular_terms_replaced}")
    
    if protected_terms_preserved and regular_terms_replaced:
        print("\n🎉 Never.csv protection test PASSED!")
    else:
        print("\n❌ Never.csv protection test FAILED!")

if __name__ == "__main__":
    test_never_protection()
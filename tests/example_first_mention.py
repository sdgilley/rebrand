#!/usr/bin/env python3
"""
Example script showing how to use the first mention differentiation functionality.

This script demonstrates:
1. How to load first mention rules from a CSV file
2. How to apply first mention replacements to text
3. Integration with existing protection mechanisms
"""

import os
from utils import (
    load_first_mention_csv, 
    first_mention_replace,
    protect_never_terms,
    restore_never_terms
)

def process_text_with_first_mentions(text, first_mention_rules, never_terms=None, debug_mode=False):
    """Process text applying first mention differentiation.
    
    Args:
        text: The text to process
        first_mention_rules: List of (term, first_replace, subsequent_replace) tuples
        never_terms: Optional list of terms to protect from replacement
        debug_mode: Whether to print debug information
    
    Returns:
        str: Processed text with first mention differentiation applied
    """
    # Protect never-replace terms first if provided
    never_replacements = {}
    if never_terms:
        text, never_replacements = protect_never_terms(text, never_terms, debug_mode)
    
    original_text = text
    
    # Apply first mention replacements
    for term, first_replace, subsequent_replace in first_mention_rules:
        if term in text:
            old_text = text
            text = first_mention_replace(text, term, first_replace, subsequent_replace, debug_mode)
            if debug_mode and text != old_text:
                print(f"Applied first mention rule for '{term}'")
    
    # Restore never-replace terms
    if never_replacements:
        text = restore_never_terms(text, never_replacements)
    
    return text

# Example usage
if __name__ == "__main__":
    # Load first mention rules
    first_mention_rules = load_first_mention_csv('patterns/first_mention.csv', debug_mode=True)
    
    # Example text
    sample_text = """
    Welcome to Azure AI Foundry! This guide will help you get started with Azure AI Foundry.
    
    Azure AI Foundry provides powerful AI capabilities. You can use Azure AI Foundry to build 
    intelligent applications. The Azure AI Foundry portal makes it easy to manage your projects.
    
    Azure OpenAI is another service. You can integrate Azure OpenAI with your applications.
    Later, you might want to explore more Azure OpenAI features.
    """
    
    print("Original text:")
    print(sample_text)
    print("\n" + "="*50 + "\n")
    
    # Process with first mention differentiation
    processed_text = process_text_with_first_mentions(
        sample_text, 
        first_mention_rules, 
        debug_mode=True
    )
    
    print("Processed text:")
    print(processed_text)
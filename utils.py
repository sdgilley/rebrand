"""
Utility functions for the rebrand script.
"""
import os
import pandas as pd
import re

def load_csv_replacements(csv_file, description, required=False, debug_mode=False):
    """Load replacements from a CSV file with search,replace columns.
    
    Args:
        csv_file: Path to the CSV file
        description: Description for debug/error messages
        required: If True, exit if file not found. If False, return empty dict.
        debug_mode: Whether to print debug information
    
    Returns:
        dict: Dictionary of search->replace mappings
    """
    replacements = {}
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
        replacements = dict(zip(df['search'], df['replace']))
        if debug_mode:
            print(f"Loaded {len(replacements)} {description} from {csv_file}")
    else:
        if required:
            print(f"Error: {csv_file} not found")
            exit(1)
        elif debug_mode:
            print(f"No {csv_file} found, no {description} will be applied")
    
    return replacements

def protect_never_terms(text, never_terms, debug_mode=False):
    """Temporarily replace terms that should never be changed with placeholders.
    
    Args:
        text: The text to protect
        never_terms: List of terms that should never be changed
        debug_mode: Whether to print debug information
    
    Returns:
        tuple: (protected_text, replacements_map) where replacements_map can restore originals
    """
    replacements_map = {}
    protected_text = text
    
    for i, term in enumerate(never_terms):
        if term in protected_text:
            placeholder = f"__NEVER_REPLACE_{i}__"
            replacements_map[placeholder] = term
            protected_text = protected_text.replace(term, placeholder)
            if debug_mode:
                count = text.count(term)
                print(f"    Protected {count} occurrence(s) of '{term}' from replacement")
    
    return protected_text, replacements_map

def restore_never_terms(text, replacements_map):
    """Restore the original never-replace terms from placeholders.
    
    Args:
        text: The text with placeholders
        replacements_map: Map of placeholder -> original term
    
    Returns:
        str: Text with original terms restored
    """
    result = text
    for placeholder, original_term in replacements_map.items():
        result = result.replace(placeholder, original_term)
    return result

def safe_replace(text, search_term, replace_term, max_replacements=None, debug_mode=False):
    """Replace text while preserving occurrences in 'formerly' contexts.
    
    Args:
        text: The text to search in
        search_term: The term to search for
        replace_term: The replacement term
        max_replacements: Maximum number of replacements (None for all)
        debug_mode: Whether to print debug information
    
    Returns:
        str: Text with replacements made, except in 'formerly' contexts
    """
    # Pattern to match "formerly/previously/originally" contexts
    # Matches: (formerly ... search_term ...) or (previously ... search_term ...)
    formerly_pattern = r'\([^)]*(?:formerly|previously|originally)[^)]*' + re.escape(search_term) + r'[^)]*\)'
    
    # Find all "formerly" contexts to preserve
    formerly_matches = list(re.finditer(formerly_pattern, text, re.IGNORECASE))
    
    if not formerly_matches:
        # No "formerly" contexts, do normal replacement
        if max_replacements:
            return text.replace(search_term, replace_term, max_replacements)
        else:
            return text.replace(search_term, replace_term)
    
    # There are "formerly" contexts - need to be careful
    # Find all occurrences of search_term, process from end to beginning
    all_matches = list(re.finditer(re.escape(search_term), text))
    all_matches.reverse()  # Process from end to preserve positions
    
    result = text
    replacements_made = 0
    preserved_count = 0
    
    for match in all_matches:
        start, end = match.span()
        
        # Check if this occurrence is inside a "formerly" context
        in_formerly_context = any(
            formerly_match.start() <= start < formerly_match.end()
            for formerly_match in formerly_matches
        )
        
        if in_formerly_context:
            preserved_count += 1
        else:
            # Safe to replace this occurrence
            if max_replacements is None or replacements_made < max_replacements:
                result = result[:start] + replace_term + result[end:]
                replacements_made += 1
    
    if debug_mode and preserved_count > 0:
        print(f"    Preserved {preserved_count} '{search_term}' in 'formerly' contexts")
    
    return result

def generate_article_cleanup_rules(always_csv_path, debug_mode=False):
    """Generate 'an X' -> 'a X' cleanup rules from always.csv patterns.
    
    Finds patterns in always.csv where "Azure AI X" becomes just "X" and generates
    article cleanup rules for "an X" -> "a X" variations.
    
    Args:
        always_csv_path: Path to the always.csv file
        debug_mode: Whether to print debug information
    
    Returns:
        list: List of (search, replace) tuples for article cleanup
    """
    if not os.path.exists(always_csv_path):
        if debug_mode:
            print(f"Warning: {always_csv_path} not found")
        return []
    
    df = pd.read_csv(always_csv_path)
    cleanup_rules = []
    
    # Find patterns where "Azure AI X" becomes just "X" (single word)
    for _, row in df.iterrows():
        search_term = row['search']
        replace_term = row['replace']
        
        # Skip if not an Azure AI pattern
        if not search_term.startswith('Azure AI '):
            continue
            
        # Extract the service name after "Azure AI "
        service_name = search_term[9:]  # Remove "Azure AI " prefix
        
        # Check if replacement is just the service name (single word, no spaces)
        # This indicates "Azure AI X" -> "X" pattern
        if replace_term == service_name and ' ' not in service_name:
            # Generate article cleanup variations
            variations = [
                (f"an {service_name}", f"a {service_name}"),
                (f"An {service_name}", f"A {service_name}"),
                (f"an [{service_name}", f"a [{service_name}"),
                (f"An [{service_name}", f"A [{service_name}"),
            ]
            
            cleanup_rules.extend(variations)
            
            if debug_mode:
                print(f"Generated article cleanup rules for: {service_name}")
    
    return cleanup_rules
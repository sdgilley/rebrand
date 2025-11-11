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

def first_mention_replace_in_body(text, search_term, first_replace, subsequent_replace, debug_mode=False):
    """Replace occurrences with metadata/title getting first_replace, body getting first mention logic.
    
    Args:
        text: The full markdown text to search in
        search_term: The term to search for
        first_replace: Replacement for metadata, title, and first occurrence in body
        subsequent_replace: Replacement for subsequent occurrences in body only
        debug_mode: Whether to print debug information
    
    Returns:
        str: Text with metadata and title using first_replace, body using first mention logic,
             except occurrences in 'formerly' contexts which are preserved
    """
    import re
    
    # Split content into metadata, title, and body sections
    metadata = ""
    title_section = ""
    body_content = text
    
    # Handle YAML front matter
    if text.startswith('---'):
        parts = text.split('---', 2)
        if len(parts) >= 3:
            metadata_content = parts[1]
            body_content = parts[2]
            
            # Replace ALL occurrences in metadata with first_replace
            metadata_content = metadata_content.replace(search_term, first_replace)
            metadata = f"---{metadata_content}---"
    
    # Find the title (first # heading) in the body content
    title_match = re.match(r'^(\s*#[^#\n]*\n)', body_content, re.MULTILINE)
    if title_match:
        title_section = title_match.group(1)
        actual_body = body_content[len(title_section):]
        
        # Replace ALL occurrences in title with first_replace
        title_section = title_section.replace(search_term, first_replace)
    else:
        actual_body = body_content
    
    # Apply first mention logic only to the actual body (after metadata and title)
    processed_body = first_mention_replace(actual_body, search_term, first_replace, subsequent_replace, debug_mode)
    
    # Reconstruct the full text
    result = metadata + title_section + processed_body
    
    if debug_mode:
        metadata_changes = text.count(search_term) - (title_section + processed_body).count(search_term) if metadata else 0
        title_changes = title_section.count(first_replace) if title_section else 0
        if metadata_changes > 0:
            print(f"    Metadata: {metadata_changes} '{search_term}' → '{first_replace}'")
        if title_changes > 0:
            print(f"    Title: {title_changes} '{search_term}' → '{first_replace}'")
        if processed_body != actual_body:
            print(f"    Body: Applied first mention logic")
    
    return result

def first_mention_replace(text, search_term, first_replace, subsequent_replace, debug_mode=False):
    """Replace the first occurrence of a term differently from subsequent occurrences.
    Preserves occurrences in 'formerly' contexts (does not replace them).
    
    Args:
        text: The text to search in
        search_term: The term to search for
        first_replace: Replacement for the first occurrence
        subsequent_replace: Replacement for subsequent occurrences
        debug_mode: Whether to print debug information
    
    Returns:
        str: Text with first occurrence replaced with first_replace, others with subsequent_replace,
             except occurrences in 'formerly' contexts which are preserved
    """
    import re
    
    # Pattern to match "formerly/previously/originally" contexts
    # Matches: (formerly ... search_term ...) or (previously ... search_term ...)
    formerly_pattern = r'\([^)]*(?:formerly|previously|originally)[^)]*' + re.escape(search_term) + r'[^)]*\)'
    
    # Find all "formerly" contexts to preserve
    formerly_matches = list(re.finditer(formerly_pattern, text, re.IGNORECASE))
    
    # Find all occurrences of the search term
    all_matches = list(re.finditer(re.escape(search_term), text))
    
    if not all_matches:
        return text
    
    # Filter out matches that are inside "formerly" contexts
    safe_matches = []
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
            safe_matches.append(match)
    
    if not safe_matches:
        if debug_mode and preserved_count > 0:
            print(f"    Preserved all {preserved_count} '{search_term}' in 'formerly' contexts")
        return text
    
    # Process safe matches from end to beginning to preserve positions
    result = text
    for i, match in enumerate(reversed(safe_matches)):
        start, end = match.span()
        # The first occurrence is the last one we process (index len-1 when reversed)
        is_first = (len(safe_matches) - 1 - i) == 0
        
        replacement = first_replace if is_first else subsequent_replace
        result = result[:start] + replacement + result[end:]
    
    if debug_mode:
        first_count = 1 if safe_matches else 0
        subsequent_count = len(safe_matches) - 1 if len(safe_matches) > 1 else 0
        if first_count > 0:
            print(f"    First mention: '{search_term}' → '{first_replace}'")
        if subsequent_count > 0:
            print(f"    Subsequent {subsequent_count} mentions: '{search_term}' → '{subsequent_replace}'")
        if preserved_count > 0:
            print(f"    Preserved {preserved_count} '{search_term}' in 'formerly' contexts")
    
    return result

def load_first_mention_csv(csv_file, debug_mode=False):
    """Load first mention replacements from a CSV file with term,first_replace,subsequent_replace columns.
    
    Args:
        csv_file: Path to the CSV file
        debug_mode: Whether to print debug information
    
    Returns:
        list: List of (term, first_replace, subsequent_replace) tuples
    """
    replacements = []
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
        for _, row in df.iterrows():
            replacements.append((row['term'], row['first_replace'], row['subsequent_replace']))
        if debug_mode:
            print(f"Loaded {len(replacements)} first mention rules from {csv_file}")
    else:
        if debug_mode:
            print(f"No {csv_file} found, no first mention replacements will be applied")
    
    return replacements

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
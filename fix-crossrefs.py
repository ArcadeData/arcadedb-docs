#!/usr/bin/env python3
"""
Script to fix cross-references in ArcadeDB documentation files.
This script finds and replaces invalid cross-reference anchors with standardized ones.
"""

import os
import re
import glob
from pathlib import Path

# Define mapping of invalid references to their corrected versions
REFERENCE_MAPPING = {
    "iteratebucket": "iterate-bucket",
    "iteratetype": "iterate-type",
    "scanbucket": "scan-bucket",
    "scantype": "scan-type",
    "asyncCommandMap": "async-command-map",
    "asyncQueryMap": "async-query-map",
    "http-command": "http-executecommand"
}


def fix_cross_refs_in_file(file_path):
    """Fix cross-references in a given AsciiDoc file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Track if any changes were made
    changed = False

    # Fix anchor definitions [[badref]] -> [[badref]][[good-ref]]
    for bad_ref, good_ref in REFERENCE_MAPPING.items():
        # Skip if the good reference is already in the file
        if f"[[{good_ref}]]" in content:
            continue

        # Find anchor definitions
        anchor_pattern = rf'\[\[{bad_ref}\]\]'
        if re.search(anchor_pattern, content) and not re.search(rf'\[\[{good_ref}\]\]', content):
            content = re.sub(anchor_pattern, f'[[{bad_ref}]]\n[[{good_ref}]]', content)
            changed = True

    # Fix cross-references <<badref,text>> -> <<good-ref,text>>
    for bad_ref, good_ref in REFERENCE_MAPPING.items():
        # Find cross-references
        crossref_pattern = rf'<<{bad_ref}([,\s])'
        if re.search(crossref_pattern, content):
            content = re.sub(crossref_pattern, f'<<{good_ref}\\1', content)
            changed = True

    # Save changes if any were made
    if changed:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed cross-references in {file_path}")
    else:
        print(f"No changes needed in {file_path}")


def main():
    """Find and fix cross-references in all AsciiDoc files."""
    base_dir = Path(__file__).parent
    asciidoc_dir = base_dir / "src" / "main" / "asciidoc"

    # Get all .adoc files
    adoc_files = list(asciidoc_dir.glob("**/*.adoc"))
    print(f"Found {len(adoc_files)} AsciiDoc files")

    # Process each file
    fixed_count = 0
    for file_path in adoc_files:
        try:
            fix_cross_refs_in_file(file_path)
            fixed_count += 1
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    print(f"Processed {fixed_count} files")


if __name__ == "__main__":
    main()

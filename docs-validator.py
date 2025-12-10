#!/usr/bin/env python3
"""
ArcadeDB Documentation Validator

This script validates AsciiDoc documentation files for:
1. Proper anchor naming convention (lowercase with hyphens)
2. Valid cross-references (all referenced anchors exist)
3. Orphaned pages (pages not referenced by any other page)

Usage:
    python docs-validator.py [--fix]

Dependencies:
    - Python 3.6+
    - re, os, sys modules (standard library)
"""

import os
import re
import sys
import argparse
from collections import defaultdict
from pathlib import Path


class DocsValidator:
    def __init__(self, docs_dir='src/main/asciidoc'):
        self.docs_dir = docs_dir
        self.files = []
        self.anchors = {}  # anchor_id -> file_path
        self.references = defaultdict(list)  # anchor_id -> [(source_file, line_number)]
        self.issues_found = False

        # Regular expressions for finding anchors and cross-references
        self.anchor_regex = re.compile(r'\[\[([\w\-_]+)\]\]')
        self.xref_regex = re.compile(r'<<([^>,]+)(?:,[^>]*)?>>')
        self.filename_regex = re.compile(r'^[a-z0-9\-]+\.adoc$')

    def find_files(self):
        """Find all AsciiDoc files in the documentation directory."""
        print(f"Scanning directory: {self.docs_dir}")

        for root, _, files in os.walk(self.docs_dir):
            for file in files:
                if file.endswith('.adoc'):
                    file_path = os.path.join(root, file)
                    self.files.append(file_path)

        print(f"Found {len(self.files)} AsciiDoc files")

    def validate_filename(self, file_path):
        """Validate that the filename follows the lowercase-with-hyphens convention."""
        filename = os.path.basename(file_path)
        if not self.filename_regex.match(filename):
            print(f"ERROR: Invalid filename format: {filename}")
            print(f"       Filenames should be lowercase with hyphens")
            self.issues_found = True
            return False
        return True

    def extract_anchors_and_references(self):
        """Extract all anchors and cross-references from the files."""
        for file_path in self.files:
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    content = f.read()

                    # Extract anchors
                    for match in self.anchor_regex.finditer(content):
                        anchor_id = match.group(1)
                        self.anchors[anchor_id] = file_path

                    # Extract cross-references
                    for line_num, line in enumerate(content.splitlines(), 1):
                        for match in self.xref_regex.finditer(line):
                            ref_id = match.group(1)
                            self.references[ref_id].append((file_path, line_num))
                except Exception as e:
                    print(f"ERROR: Could not process file {file_path}: {str(e)}")
                    self.issues_found = True

    def validate_anchor_naming(self):
        """Validate that all anchors follow the lowercase-with-hyphens convention."""
        print("\nValidating anchor naming convention...")
        valid_anchor_regex = re.compile(r'^[a-z0-9\-]+$')

        issues = 0
        invalid_anchors = []

        for anchor_id, file_path in sorted(self.anchors.items()):
            if not valid_anchor_regex.match(anchor_id):
                rel_path = os.path.relpath(file_path, self.docs_dir)
                invalid_anchors.append((anchor_id, rel_path))
                issues += 1
                self.issues_found = True

        if issues == 0:
            print("✅ All anchors follow the convention")
        else:
            print(f"❌ Found {issues} anchors with naming issues")
            print("\nTop 10 examples of invalid anchor IDs:")
            for i, (anchor_id, rel_path) in enumerate(invalid_anchors[:10]):
                print(f"  {i+1}. '{anchor_id}' in {rel_path}")

            if issues > 10:
                print(f"  ... and {issues - 10} more")

    def validate_cross_references(self):
        """Validate that all cross-references point to existing anchors."""
        print("\nValidating cross-references...")

        issues = 0
        broken_refs = []

        for ref_id, references in sorted(self.references.items()):
            if ref_id not in self.anchors:
                for file_path, line_num in references:
                    rel_path = os.path.relpath(file_path, self.docs_dir)
                    broken_refs.append((ref_id, f"{rel_path}:{line_num}"))
                    issues += 1
                    self.issues_found = True

        if issues == 0:
            print("✅ All cross-references are valid")
        else:
            print(f"❌ Found {issues} broken cross-references")
            print("\nTop 10 examples of broken references:")
            for i, (ref_id, location) in enumerate(broken_refs[:10]):
                print(f"  {i+1}. '{ref_id}' in {location}")

            if issues > 10:
                print(f"  ... and {issues - 10} more")

    def find_orphaned_pages(self):
        """Find pages that are not referenced by any other page."""
        print("\nChecking for orphaned pages...")

        # Build a set of all referenced files
        referenced_files = set()
        for anchor_id, references in self.references.items():
            if anchor_id in self.anchors:
                referenced_files.add(self.anchors[anchor_id])

        # Check which files are not referenced
        orphaned_files = []
        for file_path in self.files:
            if file_path not in referenced_files and not self._is_index_file(file_path):
                rel_path = os.path.relpath(file_path, self.docs_dir)
                orphaned_files.append(rel_path)

        if orphaned_files:
            print(f"WARNING: Found {len(orphaned_files)} potentially orphaned files")
            print("\nTop 10 examples of orphaned files:")
            for i, file in enumerate(sorted(orphaned_files)[:10]):
                print(f"  {i+1}. {file}")

            if len(orphaned_files) > 10:
                print(f"  ... and {len(orphaned_files) - 10} more")
        else:
            print("✅ No orphaned pages found")

    def _is_index_file(self, file_path):
        """Check if the file is an index file (likely to be referenced externally)."""
        filename = os.path.basename(file_path)
        index_files = ['index.adoc', 'chapter.adoc', 'manual.adoc', 'content.adoc']
        return filename in index_files

    def run_validation(self):
        """Run the complete validation process."""
        self.find_files()

        # Check filenames
        invalid_filenames = 0
        for file_path in self.files:
            if not self.validate_filename(file_path):
                invalid_filenames += 1

        if invalid_filenames == 0:
            print("✅ All filenames follow the convention")
        else:
            print(f"❌ Found {invalid_filenames} files with naming issues")

        self.extract_anchors_and_references()
        self.validate_anchor_naming()
        self.validate_cross_references()
        self.find_orphaned_pages()

        print("\nSummary:")
        print(f"Total files checked: {len(self.files)}")
        print(f"Total anchors found: {len(self.anchors)}")
        print(f"Total references found: {len(self.references)}")

        if self.issues_found:
            print("\n❌ Documentation has issues that need to be fixed")
            print("\nRecommendations:")
            print("1. Standardize all anchor IDs to lowercase with hyphens")
            print("2. Update cross-references to match the standardized anchor IDs")
            print("3. Consider adding references to orphaned pages or removing them if no longer needed")
            return 1
        else:
            print("\n✅ Documentation passed all validation checks")
            return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Validate AsciiDoc documentation files')
    args = parser.parse_args()

    validator = DocsValidator()
    exit_code = validator.run_validation()
    sys.exit(exit_code)

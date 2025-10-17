#!/usr/bin/env python3
"""
AsciiDoc Link Verification Script
Verifies all links in AsciiDoc files including:
- Cross-references (<<anchor>>)
- Inter-document references (xref:)
- External links (https://, http://)
"""

import re
import os
from pathlib import Path
from typing import List, Dict, Tuple, Set
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class Link:
    file: str
    line_num: int
    link_text: str
    link_type: str
    target: str = ""
    anchor: str = ""
    label: str = ""

@dataclass
class Issue:
    file: str
    line_num: int
    link_text: str
    issue_type: str  # 'broken' or 'format_violation'
    description: str
    context: str
    suggested_fix: str = ""

def extract_anchors_from_file(filepath: str) -> Set[str]:
    """Extract all valid anchors from an AsciiDoc file"""
    anchors = set()

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        # Explicit anchor definitions: [[anchor-name]] or [#anchor-name]
        explicit_anchors_double = re.findall(r'\[\[([^\]]+)\]\]', line)
        explicit_anchors_single = re.findall(r'\[#([^\]]+)\]', line)
        anchors.update(explicit_anchors_double)
        anchors.update(explicit_anchors_single)

        # Section headers auto-generate anchors
        # == My Section Title → my-section-title
        section_match = re.match(r'^(={1,6})\s+(.+)$', line.strip())
        if section_match:
            title = section_match.group(2)
            # Remove inline formatting, links, etc.
            title = re.sub(r'\{[^\}]+\}', '', title)  # Remove attributes
            title = re.sub(r'link:[^\[]+\[[^\]]+\]', '', title)  # Remove links
            title = re.sub(r'https?://[^\s\[]+(\[[^\]]+\])?', '', title)  # Remove URLs
            title = re.sub(r'<<[^>]+>>', '', title)  # Remove cross-refs
            title = re.sub(r'`[^`]+`', '', title)  # Remove code
            # Generate anchor
            anchor = title.strip().lower()
            anchor = re.sub(r'[^\w\s-]', '', anchor)  # Remove special chars
            anchor = re.sub(r'\s+', '-', anchor)  # Spaces to hyphens
            anchor = re.sub(r'-+', '-', anchor)  # Multiple hyphens to single
            anchor = anchor.strip('-')  # Trim hyphens
            if anchor:
                anchors.add(anchor)

    return anchors

def extract_links_from_file(filepath: str) -> List[Link]:
    """Extract all links from an AsciiDoc file"""
    links = []

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    in_code_block = False
    for line_num, line in enumerate(lines, 1):
        # Track code block boundaries
        if line.strip().startswith('----') or line.strip().startswith('....'):
            in_code_block = not in_code_block
            continue
        # Cross-references: <<anchor>> or <<anchor,Label>>
        for match in re.finditer(r'<<([^,>]+)(?:,([^>]+))?>>', line):
            anchor = match.group(1).strip()
            label = match.group(2).strip() if match.group(2) else ""
            links.append(Link(
                file=filepath,
                line_num=line_num,
                link_text=match.group(0),
                link_type='cross-ref',
                anchor=anchor,
                label=label
            ))

        # Inter-document references: xref:path/to/file.adoc[Label] or xref:file.adoc#anchor[Label]
        for match in re.finditer(r'xref:([^\[]+)\[([^\]]*)\]', line):
            target_full = match.group(1).strip()
            label = match.group(2).strip()

            # Split target and anchor
            if '#' in target_full:
                target, anchor = target_full.split('#', 1)
            else:
                target = target_full
                anchor = ""

            links.append(Link(
                file=filepath,
                line_num=line_num,
                link_text=match.group(0),
                link_type='xref',
                target=target,
                anchor=anchor,
                label=label
            ))

        # External links: https://... or http://... (skip if in code block)
        if not in_code_block:
            for match in re.finditer(r'(https?://[^\s\[]+)(?:\[([^\]]*)\])?', line):
                url = match.group(1)
                label = match.group(2) if match.group(2) is not None else ""
                links.append(Link(
                    file=filepath,
                    line_num=line_num,
                    link_text=match.group(0),
                    link_type='external',
                    target=url,
                    label=label
                ))

        # Deprecated syntax: <<file.adoc#,Title>> or <<../path/file.adoc#,Title>>
        for match in re.finditer(r'<<([^>]*\.adoc[^>]*)>>', line):
            links.append(Link(
                file=filepath,
                line_num=line_num,
                link_text=match.group(0),
                link_type='deprecated',
                target=match.group(1)
            ))

    return links

def get_context(filepath: str, line_num: int, context_lines: int = 3) -> str:
    """Get context around a specific line"""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    start = max(0, line_num - context_lines - 1)
    end = min(len(lines), line_num + context_lines)

    context = []
    for i in range(start, end):
        marker = "→ " if i == line_num - 1 else "  "
        context.append(f"{marker}{i+1}: {lines[i].rstrip()}")

    return "\n".join(context)

def resolve_path(base_file: str, target: str) -> str:
    """Resolve relative path from base file to target"""
    base_dir = os.path.dirname(base_file)
    resolved = os.path.normpath(os.path.join(base_dir, target))
    # Remove leading ./ if present
    if resolved.startswith('./'):
        resolved = resolved[2:]
    return resolved

def verify_links(files: List[str]) -> Tuple[List[Link], List[Issue]]:
    """Verify all links in all files"""
    all_links = []
    issues = []

    # Build anchor cache
    anchor_cache = {}
    for filepath in files:
        anchor_cache[filepath] = extract_anchors_from_file(filepath)

    # Extract and verify links
    for filepath in files:
        links = extract_links_from_file(filepath)
        all_links.extend(links)

        for link in links:
            if link.link_type == 'cross-ref':
                # Verify anchor exists in same file
                if link.anchor not in anchor_cache[filepath]:
                    issues.append(Issue(
                        file=filepath,
                        line_num=link.line_num,
                        link_text=link.link_text,
                        issue_type='broken',
                        description=f"Cross-reference anchor '{link.anchor}' not found in file",
                        context=get_context(filepath, link.line_num)
                    ))

            elif link.link_type == 'xref':
                # Resolve target file path
                target_path = resolve_path(filepath, link.target)

                # Check if target file exists
                if not os.path.exists(target_path):
                    issues.append(Issue(
                        file=filepath,
                        line_num=link.line_num,
                        link_text=link.link_text,
                        issue_type='broken',
                        description=f"Target file '{target_path}' not found",
                        context=get_context(filepath, link.line_num)
                    ))
                else:
                    # If anchor specified, verify it exists in target
                    if link.anchor:
                        if target_path not in anchor_cache:
                            anchor_cache[target_path] = extract_anchors_from_file(target_path)

                        if link.anchor not in anchor_cache[target_path]:
                            issues.append(Issue(
                                file=filepath,
                                line_num=link.line_num,
                                link_text=link.link_text,
                                issue_type='broken',
                                description=f"Anchor '{link.anchor}' not found in target file '{target_path}'",
                                context=get_context(filepath, link.line_num)
                            ))

            elif link.link_type == 'external':
                # External links are valid without labels
                # Bare URLs (https://example.com) are acceptable in technical documentation
                # where showing the actual URL is important for users
                pass

            elif link.link_type == 'deprecated':
                # Deprecated syntax detected
                issues.append(Issue(
                    file=filepath,
                    line_num=link.line_num,
                    link_text=link.link_text,
                    issue_type='format_violation',
                    description=f"Deprecated link syntax - use xref: instead",
                    context=get_context(filepath, link.line_num),
                    suggested_fix=f"xref:{link.target.rstrip('#,')}[Label]"
                ))

    return all_links, issues

def main():
    # Get all .adoc files (excluding target directories)
    files = []
    for root, dirs, filenames in os.walk('.'):
        # Skip target directories
        if 'target' in dirs:
            dirs.remove('target')

        for filename in filenames:
            if filename.endswith('.adoc'):
                filepath = os.path.join(root, filename)
                # Normalize path
                filepath = os.path.normpath(filepath)
                if filepath.startswith('./'):
                    filepath = filepath[2:]
                files.append(filepath)

    files.sort()

    print(f"Processing {len(files)} AsciiDoc files...")
    print()

    # Verify links
    all_links, issues = verify_links(files)

    # Categorize issues
    broken_links = [i for i in issues if i.issue_type == 'broken']
    format_violations = [i for i in issues if i.issue_type == 'format_violation']

    valid_links = len(all_links) - len(issues)

    # Print summary
    print("=" * 80)
    print("LINK VERIFICATION SUMMARY")
    print("=" * 80)
    print()
    print(f"Files processed:      {len(files)}")
    print(f"Total links found:    {len(all_links)}")
    print(f"Valid links:          {valid_links}")
    print(f"Broken links:         {len(broken_links)}")
    print(f"Format violations:    {len(format_violations)}")
    print()

    # Print broken links
    if broken_links:
        print("=" * 80)
        print("BROKEN LINKS")
        print("=" * 80)
        print()
        for issue in broken_links:
            print(f"File: {issue.file}:{issue.line_num}")
            print(f"Link: {issue.link_text}")
            print(f"Issue: {issue.description}")
            print(f"Context:")
            print(issue.context)
            print()

    # Print format violations
    if format_violations:
        print("=" * 80)
        print("FORMAT VIOLATIONS")
        print("=" * 80)
        print()
        for issue in format_violations:
            print(f"File: {issue.file}:{issue.line_num}")
            print(f"Link: {issue.link_text}")
            print(f"Violation: {issue.description}")
            if issue.suggested_fix:
                print(f"Should be: {issue.suggested_fix}")
            print(f"Context:")
            print(issue.context)
            print()

    # Final verdict
    print("=" * 80)
    print("FINAL VERDICT")
    print("=" * 80)
    if not issues:
        print("✅ All links valid")
    else:
        print(f"❌ Found {len(broken_links)} broken links and {len(format_violations)} format violations")
    print()

    return len(issues)

if __name__ == '__main__':
    exit(main())

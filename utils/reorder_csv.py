#!/usr/bin/env python3
"""
Project AGAP: Data Reordering Utility
Synchronizes and alphabetizes agency records across CSV files.

Order Logic:
- Alphabetical by Acronym
- Except for 'DDS', which is kept at Row 69!
"""

import csv
import os
import argparse
import re
import sys
import secrets

def generate_guid():
    """Generates a random 8-character hex GUID for new entries."""
    return secrets.token_hex(4)

def generate_pronunciation(acronym):
    """Generates phonetic spacing for acronyms (e.g., 'WHO' -> 'W H O')."""
    # 1. Split mixed-case (e.g., PhilHealth -> Phil Health)
    spaced = re.sub(r'([a-z])([A-Z])', r'\1 \2', acronym)
    
    # 2. For each part, if all caps and length > 1, space the letters
    parts = spaced.split()
    pron_parts = []
    for p in parts:
        if p.isupper() and len(p) > 1:
            pron_parts.append(" ".join(list(p)))
        else:
            pron_parts.append(p)
    
    return " ".join(pron_parts)

def extract_acronym_from_filename(filename):
    """Extracts the acronym from a logo filename like 'agap-logo-[acronym].svg'."""
    base = os.path.basename(filename).replace('agap-logo-', '')
    return os.path.splitext(base)[0].lower()

def extract_logo_acronym(img_tag):
    """Extracts acronym from an HTML <img> tag's src attribute."""
    match = re.search(r'src="([^"]+)"', img_tag)
    if match:
        return extract_acronym_from_filename(match.group(1))
    return None

def process_reorder(agap_path, sources_path):
    if not os.path.exists(agap_path):
        print(f"Error: {agap_path} not found.")
        sys.exit(1)
    if not os.path.exists(sources_path):
        print(f"Error: {sources_path} not found.")
        sys.exit(1)

    # 1. READ AGAP.CSV
    with open(agap_path, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        agap_header = next(reader)
        agap_data = list(reader)

    # Check for Pronunciation column in header
    has_pronunciation = "Pronunciation" in agap_header
    if not has_pronunciation:
        # insert at index 2 (after Acronym)
        agap_header.insert(2, "Pronunciation")

    # Clean up malformed rows, auto-generate GUIDs and Pronunciation
    cleaned_agap = []
    for row in agap_data:
        if not row: continue
        
        # 1. GUID auto-generation
        if not row[0] or row[0].strip() == "":
            row[0] = generate_guid()

        # 2. Handle Pronunciation column insertion/sync
        if not has_pronunciation:
            # We need to insert a placeholder or the generated one
            acro = row[1]
            pron = generate_pronunciation(acro)
            row.insert(2, pron)
        else:
            # Sync existing Pronunciation if empty
            if not row[2] or row[2].strip() == "":
                row[2] = generate_pronunciation(row[1])

        # 3. Malformed row column cleanup
        if len(row) > len(agap_header):
            # assume Info is the last part
            new_row = row[:6] + [", ".join(row[6:])]
            cleaned_agap.append(new_row)
        else:
            cleaned_agap.append(row)

    dds_entry = next((row for row in cleaned_agap if row[1] == 'DDS'), None)
    others = [row for row in cleaned_agap if row[1] != 'DDS']

    # Sort others alphabetically by acronym (index 1)
    others.sort(key=lambda x: x[1].lower())

    target_index = 68
    if dds_entry:
        if len(others) >= target_index:
            others.insert(target_index, dds_entry)
            print(f"Successfully positioned DDS at Row 69.")
        else:
            others.append(dds_entry)
            print(f"Warning: Only {len(others)} entries found. DDS moved to end.")

    final_agap_data = others

    # 2. SYNC SOURCES.CSV
    with open(sources_path, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        sources_header = next(reader)
        sources_data = list(reader)

    # Map sources by acronym for O(1) lookup
    sources_map = {}
    for row in sources_data:
        if not row: continue
        target_file = row[0]
        acro = extract_acronym_from_filename(target_file)
        
        if len(row) > len(sources_header):
            url = ",".join(row[1:-2]).strip()
            normalized_row = [row[0], url, row[-2], row[-1]]
            sources_map[acro] = normalized_row
        else:
            sources_map[acro] = row

    final_sources_data = []
    seen_sources = set()

    for row in final_agap_data:
        # Extract acronym from logo field (at index 4 now after inserting Pronunciation at 2)
        logo_field = row[4] 
        acro = extract_logo_acronym(logo_field) or row[1].lower()
        if acro in sources_map:
            final_sources_data.append(sources_map[acro])
            seen_sources.add(acro)
        else:
            print(f"Warning: Logo source missing for '{acro}' ({row[1]})")

    # Add any orphans remaining in sources.csv
    for acro, row in sources_map.items():
        if acro not in seen_sources:
            final_sources_data.append(row)
            print(f"Note: Retained orphan source mapping for '{acro}'")

    # 3. ATOMIC WRITE
    for path, header, data in [(agap_path, agap_header, final_agap_data),
                                (sources_path, sources_header, final_sources_data)]:
        temp_path = f"{path}.tmp"
        with open(temp_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
            writer.writerow(header)
            writer.writerows(data)
        os.replace(temp_path, path)

    print("Success: CSV data synchronized, reordered, and normalized with pronunciation.")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.realpath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, ".."))

    parser = argparse.ArgumentParser(description="Reorder and sync project CSV data.")
    parser.add_argument("--agap", default=os.path.join(project_root, "src/data/agap.csv"), help="Path to agap.csv")
    parser.add_argument("--sources", default=os.path.join(project_root, "sources.csv"), help="Path to sources.csv")

    args = parser.parse_args()
    process_reorder(args.agap, args.sources)

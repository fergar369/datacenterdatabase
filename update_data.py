#!/usr/bin/env python3
"""
Standalone script to re-run data scraping and update the database

Usage:
    python update_data.py

Environment Variables:
    PJM_API_KEY - Optional API key for PJM data access

This script will:
1. Fetch latest ERCOT and PJM interconnection queue data
2. Apply aggressive filtering for data center projects
3. Update the SQLite database
4. Geocode new locations
5. Regenerate all output files
"""

import sys
import os
import subprocess

def main():
    print("="*70)
    print("DATA CENTER INTELLIGENCE DATABASE - UPDATE SCRIPT")
    print("="*70)
    print()

    # Step 1: Re-create database with latest data
    print("Step 1: Fetching latest data and creating database...")
    print("-" * 70)
    result = subprocess.run([sys.executable, 'create_datacenter_db.py'])
    if result.returncode != 0:
        print("ERROR: Database creation failed!")
        return 1

    # Step 2: Add geocoding
    print("\nStep 2: Adding geocoding coordinates...")
    print("-" * 70)
    result = subprocess.run([sys.executable, 'add_geocoding.py'])
    if result.returncode != 0:
        print("ERROR: Geocoding failed!")
        return 1

    # Step 3: Generate outputs
    print("\nStep 3: Generating visualization and reports...")
    print("-" * 70)
    result = subprocess.run([sys.executable, 'generate_outputs.py'])
    if result.returncode != 0:
        print("ERROR: Output generation failed!")
        return 1

    print("\n" + "="*70)
    print("DATABASE UPDATE COMPLETED SUCCESSFULLY!")
    print("="*70)
    print("\nUpdated files:")
    print("  • datacenter_intelligence.db   - SQLite database")
    print("  • datacenter_map.html          - Interactive map")
    print("  • summary_report.csv           - Data export")
    print("  • statistics_summary.txt       - Statistics report")
    print()
    print("Notes:")
    print("  - To fetch live PJM data, set PJM_API_KEY environment variable")
    print("  - ERCOT data is fetched automatically via gridstatus library")
    print("  - Sample data files (sample_*_queue.csv) are used as fallback")
    print()

    return 0

if __name__ == '__main__':
    sys.exit(main())

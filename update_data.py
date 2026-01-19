#!/usr/bin/env python3
"""
Standalone update script for Data Center Intelligence Database

Run this script to refresh data from ERCOT and PJM queues.
"""

import os
import sys
from datetime import datetime

# Import main script functionality
from main import main


def backup_database():
    """Create backup of existing database"""
    import config
    import shutil

    if os.path.exists(config.DB_NAME):
        backup_name = f"{config.DB_NAME}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(config.DB_NAME, backup_name)
        print(f"✓ Database backed up to: {backup_name}")
        return backup_name
    return None


def update():
    """Update database with latest data"""

    print("\n" + "="*70)
    print("DATA CENTER INTELLIGENCE DATABASE - UPDATE")
    print("="*70)
    print(f"\nUpdate started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Create backup
    print("\n1. Creating database backup...")
    backup_file = backup_database()

    # Run main scraping and processing
    print("\n2. Fetching and processing latest data...")
    try:
        main()
        print("\n✓ Update completed successfully!")

        if backup_file:
            print(f"\nNote: Backup saved at {backup_file}")
            print("      You can restore it if needed by renaming it to datacenter_intelligence.db")

    except Exception as e:
        print(f"\n✗ Update failed: {e}")
        import traceback
        traceback.print_exc()

        if backup_file:
            print(f"\n⚠ Database backup is available at: {backup_file}")

        sys.exit(1)


if __name__ == "__main__":
    update()

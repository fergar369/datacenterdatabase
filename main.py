#!/usr/bin/env python3
"""
Data Center Intelligence Database - Main Script

Scrapes ERCOT and PJM interconnection queues to identify data center projects.
"""

import sys
from datetime import datetime
from tqdm import tqdm

# Local imports
from database import DataCenterDB
from scraper_ercot import ERCOTScraper
from scraper_pjm import PJMScraper
from filters import is_data_center_project, standardize_status
from geocoding import Geocoder, get_county_centroid
from visualization import MapVisualizer
from reports import ReportGenerator, create_readme
import config


def main():
    """Main execution function"""

    print("\n" + "="*70)
    print("DATA CENTER INTELLIGENCE DATABASE - POC")
    print("="*70)
    print(f"\nStarted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Initialize database
    print("\n" + "="*60)
    print("1. Database Initialization")
    print("="*60)

    with DataCenterDB() as db:
        db.create_tables()

        # Scrape ERCOT data
        print("\n" + "="*60)
        print("2. Scraping ERCOT Data")
        print("="*60)

        ercot_scraper = ERCOTScraper()
        ercot_facilities = ercot_scraper.scrape()

        # Scrape PJM data
        print("\n" + "="*60)
        print("3. Scraping PJM Data")
        print("="*60)

        pjm_scraper = PJMScraper()
        pjm_facilities = pjm_scraper.scrape()

        # Combine all facilities
        all_facilities = ercot_facilities + pjm_facilities
        print(f"\n✓ Total facilities scraped: {len(all_facilities)}")

        # Apply aggressive filtering
        print("\n" + "="*60)
        print("4. Applying Aggressive Data Center Filtering")
        print("="*60)

        matched_facilities = []
        print(f"\nFiltering {len(all_facilities)} facilities...")

        for facility in tqdm(all_facilities, desc="Filtering"):
            is_match, reason = is_data_center_project(facility)

            if is_match:
                facility['match_reason'] = reason
                facility['status'] = standardize_status(facility.get('status'))
                matched_facilities.append(facility)

        print(f"\n✓ Matched {len(matched_facilities)} data center projects")
        print(f"  Match rate: {len(matched_facilities)/len(all_facilities)*100:.1f}%")

        # Update data source statistics
        ercot_matched = sum(1 for f in matched_facilities if f['data_source'] == 'ERCOT')
        pjm_matched = sum(1 for f in matched_facilities if f['data_source'] == 'PJM')

        db.update_data_source('ERCOT', config.ERCOT_QUEUE_URL,
                            len(ercot_facilities), ercot_matched)
        db.update_data_source('PJM', config.PJM_QUEUE_URL,
                            len(pjm_facilities), pjm_matched)

        # Geocode locations
        print("\n" + "="*60)
        print("5. Geocoding Locations")
        print("="*60)

        geocoder = Geocoder()
        print(f"\nGeocoding {len(matched_facilities)} facilities...")

        for facility in tqdm(matched_facilities, desc="Geocoding"):
            # Try using pre-defined centroids first
            county = facility.get('location_county')
            state = facility.get('location_state')

            if county and state:
                lat, lon = get_county_centroid(county, state)
                if lat and lon:
                    facility['latitude'] = lat
                    facility['longitude'] = lon
                    facility['geocoding_confidence'] = 'centroid'
                    continue

            # Otherwise use geocoder
            geocoder.geocode_facility(facility)

        geocoded_count = sum(1 for f in matched_facilities
                           if f.get('latitude') and f.get('longitude'))
        print(f"\n✓ Successfully geocoded {geocoded_count}/{len(matched_facilities)} facilities")

        # Store in database
        print("\n" + "="*60)
        print("6. Storing Data in Database")
        print("="*60)

        print(f"\nInserting {len(matched_facilities)} facilities...")

        for facility in tqdm(matched_facilities, desc="Inserting"):
            db.insert_facility(facility)

            # Update company stats
            if facility.get('operator_company'):
                db.update_company_stats(facility['operator_company'])

        print(f"\n✓ Database populated with {len(matched_facilities)} facilities")

        # Generate statistics
        stats = db.get_statistics()

        # Get all facilities for reporting
        all_db_facilities = db.get_all_facilities()

    # Create visualizations
    print("\n" + "="*60)
    print("7. Creating Interactive Map")
    print("="*60)

    visualizer = MapVisualizer()
    visualizer.create_map(all_db_facilities)

    # Generate reports
    print("\n" + "="*60)
    print("8. Generating Reports")
    print("="*60)

    reporter = ReportGenerator(all_db_facilities, stats)
    reporter.generate_all_reports()

    # Create README
    print("\n" + "="*60)
    print("9. Creating Documentation")
    print("="*60)

    create_readme()

    # Final summary
    print("\n" + "="*70)
    print("EXECUTION COMPLETE")
    print("="*70)
    print(f"\nFinished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nOutput files:")
    print(f"  • {config.DB_NAME} (SQLite database)")
    print(f"  • {config.OUTPUT_MAP} (interactive map)")
    print(f"  • {config.OUTPUT_CSV} (CSV export)")
    print(f"  • {config.OUTPUT_STATS} (statistics report)")
    print(f"  • README.md (documentation)")
    print("\n✓ All tasks completed successfully!\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

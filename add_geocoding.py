#!/usr/bin/env python3
"""
Add hardcoded geocoding coordinates for known cities (fallback for network restrictions)
"""

import sqlite3

# Hardcoded coordinates for known cities in our sample data
CITY_COORDINATES = {
    # Texas - ERCOT
    ('Austin', 'Travis', 'Texas'): (30.2672, -97.7431, 'high'),
    ('Houston', 'Harris', 'Texas'): (29.7604, -95.3698, 'high'),
    ('Dallas', 'Dallas', 'Texas'): (32.7767, -96.7970, 'high'),
    ('San Antonio', 'Bexar', 'Texas'): (29.4241, -98.4936, 'high'),
    ('Midland', 'Midland', 'Texas'): (31.9974, -102.0779, 'high'),
    ('Fort Worth', 'Tarrant', 'Texas'): (32.7555, -97.3308, 'high'),
    ('Richardson', 'Dallas', 'Texas'): (32.9483, -96.7299, 'high'),

    # Virginia - PJM
    ('Ashburn', 'Loudoun', 'Virginia'): (39.0438, -77.4874, 'high'),
    ('Sterling', 'Loudoun', 'Virginia'): (39.0062, -77.4286, 'high'),
    ('Reston', 'Fairfax', 'Virginia'): (38.9586, -77.3570, 'high'),

    # Pennsylvania - PJM
    ('Malvern', 'Chester', 'Pennsylvania'): (40.0362, -75.5138, 'high'),
    ('Pittsburgh', 'Allegheny', 'Pennsylvania'): (40.4406, -79.9959, 'high'),

    # Other PJM states
    ('Chicago', 'Cook', 'Illinois'): (41.8781, -87.6298, 'high'),
    ('Columbus', 'Franklin', 'Ohio'): (39.9612, -82.9988, 'high'),
    ('Clarksburg', 'Montgomery', 'Maryland'): (39.2382, -77.2678, 'high'),
    ('Jersey City', 'Bergen', 'New Jersey'): (40.7178, -74.0431, 'high'),
}

def update_geocoding():
    """Update database with hardcoded geocoding coordinates"""
    conn = sqlite3.connect('datacenter_intelligence.db')
    cursor = conn.cursor()

    # Get all facilities without coordinates
    cursor.execute('''
        SELECT id, location_city, location_county, location_state, project_name
        FROM facilities
        WHERE latitude IS NULL OR longitude IS NULL
    ''')

    facilities = cursor.fetchall()
    print(f"Found {len(facilities)} facilities without coordinates")

    updated_count = 0
    for facility_id, city, county, state, project_name in facilities:
        key = (city, county, state)
        if key in CITY_COORDINATES:
            lat, lon, confidence = CITY_COORDINATES[key]
            cursor.execute('''
                UPDATE facilities
                SET latitude = ?, longitude = ?, geocoding_confidence = ?
                WHERE id = ?
            ''', (lat, lon, confidence, facility_id))
            updated_count += 1
            print(f"✓ Geocoded: {project_name} -> ({lat}, {lon})")

    conn.commit()
    print(f"\nUpdated {updated_count} facilities with geocoding coordinates")

    # Show summary
    cursor.execute('SELECT COUNT(*) FROM facilities WHERE latitude IS NOT NULL')
    geocoded_count = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM facilities')
    total_count = cursor.fetchone()[0]

    print(f"\nGeocoding Summary:")
    print(f"  Total facilities: {total_count}")
    print(f"  Geocoded: {geocoded_count}")
    print(f"  Missing coordinates: {total_count - geocoded_count}")

    conn.close()

if __name__ == '__main__':
    update_geocoding()

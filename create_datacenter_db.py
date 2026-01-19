#!/usr/bin/env python3
"""
Data Center Intelligence Database POC
Scrapes ERCOT and PJM interconnection queues to identify data center projects
"""

import sqlite3
import pandas as pd
from datetime import datetime
import re
from typing import List, Dict, Tuple
import logging
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import time
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Aggressive filtering criteria
DATA_CENTER_KEYWORDS = [
    'data center', 'datacenter', 'data centre', 'compute', 'ai',
    'artificial intelligence', 'machine learning', 'hyperscale',
    'hyperscaler', 'colocation', 'colo', 'server farm', 'cloud',
    'digital infrastructure', 'edge computing', 'edge data',
    'crypto', 'cryptocurrency', 'bitcoin', 'blockchain', 'mining',
    'hpc', 'high performance computing'
]

TECHNICAL_KEYWORDS = [
    'cooling', 'crac', 'crah', 'ups', 'uninterruptible power',
    'backup generation', 'diesel generators', 'n+1', '2n redundancy'
]

DC_COMPANIES = [
    'aws', 'amazon', 'microsoft', 'azure', 'google', 'meta', 'facebook',
    'oracle', 'ibm', 'equinix', 'digital realty', 'cyrusone', 'qts',
    'coresite', 'switch', 'aligned', 'edgeconnex', 'databank',
    'flexential', 'vantage', 'iron mountain', 'nvidia', 'ntt',
    'cyxtera', 'tierpoint', 'stream', 'cologix'
]

class DataCenterDatabase:
    def __init__(self, db_path='datacenter_intelligence.db'):
        self.db_path = db_path
        self.conn = None
        self.geocoder = Nominatim(user_agent="datacenter_intelligence_poc")
        self.geocode_cache = {}

    def connect(self):
        """Connect to SQLite database"""
        self.conn = sqlite3.connect(self.db_path)
        logger.info(f"Connected to database: {self.db_path}")

    def create_schema(self):
        """Create database schema"""
        cursor = self.conn.cursor()

        # facilities table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS facilities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_name TEXT,
                operator_company TEXT,
                developer_company TEXT,
                location_state TEXT,
                location_county TEXT,
                location_city TEXT,
                latitude REAL,
                longitude REAL,
                capacity_mw REAL,
                status TEXT,
                expected_online_date TEXT,
                queue_position TEXT,
                interconnection_type TEXT,
                data_source TEXT,
                source_url TEXT,
                notes TEXT,
                date_scraped TEXT,
                matching_criteria TEXT,
                geocoding_confidence TEXT
            )
        ''')

        # companies table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT UNIQUE,
                company_type TEXT,
                facilities_count INTEGER DEFAULT 0
            )
        ''')

        # data_sources table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_name TEXT UNIQUE,
                source_url TEXT,
                last_updated TEXT,
                records_found INTEGER
            )
        ''')

        self.conn.commit()
        logger.info("Database schema created successfully")

    def check_datacenter_match(self, project_data: Dict) -> Tuple[bool, str]:
        """
        Apply aggressive filtering to identify data center projects
        Returns: (is_match, matching_criteria)
        """
        matching_reasons = []

        # Get searchable text fields
        text_fields = ' '.join([
            str(project_data.get('project_name', '')),
            str(project_data.get('operator_company', '')),
            str(project_data.get('developer_company', '')),
            str(project_data.get('notes', '')),
            str(project_data.get('interconnection_type', ''))
        ]).lower()

        # Check for data center keywords
        for keyword in DATA_CENTER_KEYWORDS:
            if keyword in text_fields:
                matching_reasons.append(f"keyword: {keyword}")

        # Check for known DC companies
        for company in DC_COMPANIES:
            if company in text_fields:
                matching_reasons.append(f"company: {company}")

        # Check for large load + technical keywords
        capacity_mw = project_data.get('capacity_mw', 0)
        try:
            capacity_mw = float(capacity_mw) if capacity_mw else 0
        except (ValueError, TypeError):
            capacity_mw = 0

        if capacity_mw > 10:
            for tech_keyword in TECHNICAL_KEYWORDS:
                if tech_keyword in text_fields:
                    matching_reasons.append(f"large load ({capacity_mw}MW) + tech: {tech_keyword}")

        # Check if it's explicitly a load interconnection
        if 'load' in text_fields.lower() and capacity_mw > 5:
            matching_reasons.append(f"load interconnection: {capacity_mw}MW")

        is_match = len(matching_reasons) > 0
        criteria = '; '.join(matching_reasons) if matching_reasons else 'no match'

        return is_match, criteria

    def geocode_location(self, city: str, county: str, state: str) -> Tuple[float, float, str]:
        """
        Geocode location to lat/long
        Returns: (latitude, longitude, confidence)
        """
        cache_key = f"{city}|{county}|{state}"

        if cache_key in self.geocode_cache:
            return self.geocode_cache[cache_key]

        # Try progressively broader searches
        search_queries = []

        if city and state:
            search_queries.append(f"{city}, {state}, USA")
        if county and state:
            search_queries.append(f"{county} County, {state}, USA")
        if state:
            search_queries.append(f"{state}, USA")

        for query in search_queries:
            try:
                time.sleep(1.1)  # Respect rate limits
                location = self.geocoder.geocode(query, timeout=10)
                if location:
                    confidence = 'high' if city else 'medium' if county else 'low'
                    result = (location.latitude, location.longitude, confidence)
                    self.geocode_cache[cache_key] = result
                    logger.info(f"Geocoded: {query} -> {location.latitude}, {location.longitude}")
                    return result
            except (GeocoderTimedOut, GeocoderServiceError) as e:
                logger.warning(f"Geocoding error for {query}: {e}")
                continue

        # Return None if geocoding failed
        logger.warning(f"Could not geocode: {cache_key}")
        return None, None, 'failed'

    def fetch_ercot_data(self) -> pd.DataFrame:
        """Fetch ERCOT interconnection queue data"""
        logger.info("Fetching ERCOT data...")

        try:
            # Try to load from sample data file (for demonstration)
            import os
            if os.path.exists('sample_ercot_queue.csv'):
                logger.info("Using sample ERCOT data from sample_ercot_queue.csv")
                queue_df = pd.read_csv('sample_ercot_queue.csv')
                logger.info(f"Loaded {len(queue_df)} ERCOT sample projects")
                return queue_df

            # If no sample data, try gridstatus API
            import gridstatus
            ercot = gridstatus.Ercot()

            # Get interconnection queue
            queue_df = ercot.get_interconnection_queue()
            logger.info(f"Retrieved {len(queue_df)} ERCOT queue projects from API")

            # Add source information
            queue_df['data_source'] = 'ERCOT'
            queue_df['source_url'] = 'https://www.ercot.com/gridinfo/generation'

            return queue_df

        except Exception as e:
            logger.error(f"Error fetching ERCOT data: {e}")
            logger.error(traceback.format_exc())
            return pd.DataFrame()

    def fetch_pjm_data(self) -> pd.DataFrame:
        """Fetch PJM interconnection queue data"""
        logger.info("Fetching PJM data...")

        try:
            import os

            # Try to load from sample data file (for demonstration)
            if os.path.exists('sample_pjm_queue.csv'):
                logger.info("Using sample PJM data from sample_pjm_queue.csv")
                queue_df = pd.read_csv('sample_pjm_queue.csv')
                logger.info(f"Loaded {len(queue_df)} PJM sample projects")
                return queue_df

            # If no sample data, try gridstatus API
            import gridstatus

            # Check if API key is available
            api_key = os.environ.get('PJM_API_KEY')
            if not api_key:
                logger.warning("PJM_API_KEY not set. Skipping PJM data (requires free account at pjm.com)")
                logger.warning("To enable PJM data: export PJM_API_KEY='your_key_here'")
                return pd.DataFrame()

            pjm = gridstatus.PJM(api_key=api_key)

            # Get interconnection queue
            queue_df = pjm.get_interconnection_queue()
            logger.info(f"Retrieved {len(queue_df)} PJM queue projects from API")

            # Add source information
            queue_df['data_source'] = 'PJM'
            queue_df['source_url'] = 'https://www.pjm.com/planning/services-requests/interconnection-queues'

            return queue_df

        except Exception as e:
            logger.error(f"Error fetching PJM data: {e}")
            logger.error(traceback.format_exc())
            return pd.DataFrame()

    def normalize_queue_data(self, df: pd.DataFrame, source: str) -> List[Dict]:
        """Normalize queue data to common schema"""
        normalized_records = []

        for idx, row in df.iterrows():
            try:
                # Extract and normalize fields based on source
                if source == 'ERCOT':
                    record = self._normalize_ercot_record(row)
                elif source == 'PJM':
                    record = self._normalize_pjm_record(row)
                else:
                    continue

                if record:
                    normalized_records.append(record)

            except Exception as e:
                logger.warning(f"Error normalizing record {idx}: {e}")
                continue

        logger.info(f"Normalized {len(normalized_records)} {source} records")
        return normalized_records

    def _normalize_ercot_record(self, row) -> Dict:
        """Normalize ERCOT-specific record"""
        return {
            'project_name': str(row.get('Project Name', row.get('project_name', ''))),
            'operator_company': str(row.get('Entity', row.get('entity', ''))),
            'developer_company': '',
            'location_state': 'Texas',
            'location_county': str(row.get('County', row.get('county', ''))),
            'location_city': str(row.get('City', row.get('city', ''))),
            'capacity_mw': row.get('Capacity (MW)', row.get('capacity_mw', 0)),
            'status': str(row.get('Status', row.get('status', 'Unknown'))),
            'expected_online_date': str(row.get('Proposed COD', row.get('proposed_cod', ''))),
            'queue_position': str(row.get('Queue ID', row.get('queue_id', ''))),
            'interconnection_type': str(row.get('Type', row.get('type', ''))),
            'data_source': 'ERCOT',
            'source_url': 'https://www.ercot.com/gridinfo/generation',
            'notes': '',
            'date_scraped': datetime.now().isoformat()
        }

    def _normalize_pjm_record(self, row) -> Dict:
        """Normalize PJM-specific record"""
        return {
            'project_name': str(row.get('Project Name', row.get('project_name', ''))),
            'operator_company': str(row.get('Owner', row.get('owner', ''))),
            'developer_company': '',
            'location_state': str(row.get('State', row.get('state', ''))),
            'location_county': str(row.get('County', row.get('county', ''))),
            'location_city': str(row.get('City', row.get('city', ''))),
            'capacity_mw': row.get('MW Capacity', row.get('mw_capacity', 0)),
            'status': str(row.get('Status', row.get('status', 'Unknown'))),
            'expected_online_date': str(row.get('In Service Date', row.get('in_service_date', ''))),
            'queue_position': str(row.get('Queue Position', row.get('queue_position', ''))),
            'interconnection_type': str(row.get('Interconnection Type', row.get('interconnection_type', ''))),
            'data_source': 'PJM',
            'source_url': 'https://www.pjm.com/planning/services-requests/interconnection-queues',
            'notes': '',
            'date_scraped': datetime.now().isoformat()
        }

    def insert_facility(self, record: Dict):
        """Insert facility record into database"""
        cursor = self.conn.cursor()

        cursor.execute('''
            INSERT INTO facilities (
                project_name, operator_company, developer_company,
                location_state, location_county, location_city,
                latitude, longitude, capacity_mw, status,
                expected_online_date, queue_position, interconnection_type,
                data_source, source_url, notes, date_scraped,
                matching_criteria, geocoding_confidence
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            record['project_name'],
            record['operator_company'],
            record['developer_company'],
            record['location_state'],
            record['location_county'],
            record['location_city'],
            record.get('latitude'),
            record.get('longitude'),
            record['capacity_mw'],
            record['status'],
            record['expected_online_date'],
            record['queue_position'],
            record['interconnection_type'],
            record['data_source'],
            record['source_url'],
            record['notes'],
            record['date_scraped'],
            record.get('matching_criteria', ''),
            record.get('geocoding_confidence', '')
        ))

        self.conn.commit()

    def update_companies_table(self):
        """Update companies table with unique companies and counts"""
        cursor = self.conn.cursor()

        # Get unique operators
        cursor.execute('''
            INSERT OR IGNORE INTO companies (company_name, company_type, facilities_count)
            SELECT DISTINCT operator_company, 'operator', 0
            FROM facilities
            WHERE operator_company IS NOT NULL AND operator_company != ''
        ''')

        # Update counts
        cursor.execute('''
            UPDATE companies
            SET facilities_count = (
                SELECT COUNT(*) FROM facilities
                WHERE facilities.operator_company = companies.company_name
            )
        ''')

        self.conn.commit()
        logger.info("Updated companies table")

    def update_data_sources_table(self):
        """Update data sources table with statistics"""
        cursor = self.conn.cursor()

        for source in ['ERCOT', 'PJM']:
            cursor.execute('''
                SELECT COUNT(*) FROM facilities WHERE data_source = ?
            ''', (source,))
            count = cursor.fetchone()[0]

            source_url = 'https://www.ercot.com/gridinfo/generation' if source == 'ERCOT' else 'https://www.pjm.com/planning/services-requests/interconnection-queues'

            cursor.execute('''
                INSERT OR REPLACE INTO data_sources (source_name, source_url, last_updated, records_found)
                VALUES (?, ?, ?, ?)
            ''', (source, source_url, datetime.now().isoformat(), count))

        self.conn.commit()
        logger.info("Updated data_sources table")

    def process_data_source(self, source_name: str):
        """Process a data source end-to-end"""
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing {source_name} data...")
        logger.info(f"{'='*60}\n")

        # Fetch data
        if source_name == 'ERCOT':
            df = self.fetch_ercot_data()
        elif source_name == 'PJM':
            df = self.fetch_pjm_data()
        else:
            logger.error(f"Unknown source: {source_name}")
            return

        if df.empty:
            logger.warning(f"No data retrieved from {source_name}")
            return

        # Normalize data
        records = self.normalize_queue_data(df, source_name)

        # Filter for data centers and insert
        dc_count = 0
        for record in records:
            is_match, criteria = self.check_datacenter_match(record)

            if is_match:
                record['matching_criteria'] = criteria

                # Geocode location
                lat, lon, confidence = self.geocode_location(
                    record['location_city'],
                    record['location_county'],
                    record['location_state']
                )
                record['latitude'] = lat
                record['longitude'] = lon
                record['geocoding_confidence'] = confidence

                # Insert into database
                self.insert_facility(record)
                dc_count += 1

                logger.info(f"✓ Found DC: {record['project_name']} ({record['capacity_mw']}MW) - {criteria}")

        logger.info(f"\n{source_name} Summary: Found {dc_count} data center projects out of {len(records)} total projects")

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")

def main():
    """Main execution function"""
    logger.info("="*60)
    logger.info("Data Center Intelligence Database POC")
    logger.info("="*60)

    db = DataCenterDatabase()

    try:
        # Initialize database
        db.connect()
        db.create_schema()

        # Process ERCOT data
        db.process_data_source('ERCOT')

        # Process PJM data
        db.process_data_source('PJM')

        # Update derived tables
        db.update_companies_table()
        db.update_data_sources_table()

        logger.info("\n" + "="*60)
        logger.info("Database creation completed successfully!")
        logger.info(f"Database saved to: {db.db_path}")
        logger.info("="*60)

    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        logger.error(traceback.format_exc())
    finally:
        db.close()

if __name__ == '__main__':
    main()

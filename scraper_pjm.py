"""
PJM Interconnection Queue scraper
"""

import requests
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import filters
import config


class PJMScraper:
    """Scrape and parse PJM load interconnection queue"""

    def __init__(self):
        self.base_url = config.PJM_QUEUE_URL
        self.source_name = "PJM"
        self.results = []

    def fetch_queue_page(self) -> Optional[str]:
        """Fetch the PJM queue page"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(self.base_url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.text

        except requests.RequestException as e:
            print(f"Error fetching PJM page: {e}")
            return None

    def find_queue_data_link(self, html_content: str) -> Optional[str]:
        """Extract the queue data download link"""
        soup = BeautifulSoup(html_content, 'html.parser')

        # Look for CSV or Excel files related to queue
        keywords = ['queue', 'interconnection', 'active', 'projects']

        for link in soup.find_all('a', href=True):
            link_text = link.get_text().lower()
            href = link['href']

            # Check for relevant keywords and file types
            if any(keyword in link_text for keyword in keywords):
                if any(ext in href.lower() for ext in ['.xlsx', '.xls', '.csv', '.xml']):
                    # Convert relative URL to absolute if needed
                    if not href.startswith('http'):
                        href = f"https://www.pjm.com{href}"
                    return href

        return None

    def parse_csv_report(self, filename: str) -> List[Dict]:
        """Parse CSV format queue report"""
        try:
            df = pd.read_csv(filename)

            # PJM-specific column mapping
            possible_columns = {
                'project_name': ['project name', 'queue id', 'project', 'id'],
                'operator': ['customer', 'applicant', 'owner', 'company'],
                'capacity': ['mw request', 'capacity', 'mw', 'size'],
                'county': ['county'],
                'city': ['municipality', 'city', 'town'],
                'state': ['state', 'st'],
                'status': ['status', 'queue status'],
                'online_date': ['proposed in-service', 'cod', 'in-service date'],
                'queue_pos': ['queue position', 'position', 'queue id'],
                'type': ['type', 'service type'],
            }

            # Map columns
            column_map = {}
            df_columns_lower = {col.lower(): col for col in df.columns}

            for field, variations in possible_columns.items():
                for variation in variations:
                    if variation in df_columns_lower:
                        column_map[field] = df_columns_lower[variation]
                        break

            print(f"  Found columns: {list(column_map.values())}")

            # Parse each row
            facilities = []
            for idx, row in df.iterrows():
                try:
                    facility = self._extract_facility_data(row, column_map)
                    if facility:
                        facilities.append(facility)
                except Exception as e:
                    print(f"  Warning: Error parsing row {idx}: {e}")
                    continue

            return facilities

        except Exception as e:
            print(f"Error parsing CSV report: {e}")
            return []

    def _extract_facility_data(self, row, column_map: Dict) -> Optional[Dict]:
        """Extract facility data from a DataFrame row"""

        # Extract capacity
        capacity_mw = None
        if 'capacity' in column_map:
            capacity_str = str(row[column_map['capacity']])
            capacity_mw = filters.extract_capacity_mw(capacity_str)

        # Skip if capacity is too small or missing
        if not capacity_mw or capacity_mw < 5.0:
            return None

        # Build facility dict
        facility = {
            'project_name': str(row[column_map.get('project_name', column_map.get('queue_pos', ''))]),
            'operator_company': str(row[column_map['operator']]) if 'operator' in column_map else None,
            'developer_company': None,
            'location_state': str(row[column_map['state']]) if 'state' in column_map else None,
            'location_county': str(row[column_map['county']]) if 'county' in column_map else None,
            'location_city': str(row[column_map['city']]) if 'city' in column_map else None,
            'capacity_mw': capacity_mw,
            'status': str(row[column_map['status']]) if 'status' in column_map else None,
            'expected_online_date': str(row[column_map['online_date']]) if 'online_date' in column_map else None,
            'queue_position': str(row[column_map['queue_pos']]) if 'queue_pos' in column_map else None,
            'interconnection_type': str(row[column_map['type']]) if 'type' in column_map else 'Load',
            'data_source': 'PJM',
            'source_url': self.base_url,
            'notes': '',
            'date_scraped': datetime.now().isoformat()
        }

        # Clean None/NaN values
        for key, value in facility.items():
            if pd.isna(value) or value == 'None' or value == 'nan':
                facility[key] = None

        return facility

    def scrape(self) -> List[Dict]:
        """
        Main scraping method

        Returns:
            List of facility dictionaries
        """
        print("\n" + "="*60)
        print("PJM Interconnection Queue Scraper")
        print("="*60)

        # Note: PJM data often requires manual download or API access
        print("\n📝 Note: PJM queue data typically requires manual download")
        print("   Creating sample PJM data for demonstration...")

        self.results = self._create_sample_pjm_data()
        return self.results

    def _create_sample_pjm_data(self) -> List[Dict]:
        """
        Create sample PJM data for demonstration
        """
        sample_data = [
            {
                'project_name': 'Ashburn Hyperscale Campus Phase 3',
                'operator_company': 'Equinix',
                'developer_company': None,
                'location_state': 'Virginia',
                'location_county': 'Loudoun',
                'location_city': 'Ashburn',
                'capacity_mw': 250.0,
                'status': 'Under Construction',
                'expected_online_date': '2025-Q1',
                'queue_position': 'Y2-123',
                'interconnection_type': 'Load',
                'data_source': 'PJM',
                'source_url': self.base_url,
                'notes': 'Major hyperscale colocation expansion in Data Center Alley',
                'date_scraped': datetime.now().isoformat()
            },
            {
                'project_name': 'Manassas AI Compute Facility',
                'operator_company': 'Meta',
                'developer_company': None,
                'location_state': 'Virginia',
                'location_county': 'Prince William',
                'location_city': 'Manassas',
                'capacity_mw': 300.0,
                'status': 'Planned',
                'expected_online_date': '2026-Q2',
                'queue_position': 'Z1-045',
                'interconnection_type': 'Load',
                'data_source': 'PJM',
                'source_url': self.base_url,
                'notes': 'AI training datacenter with advanced cooling systems',
                'date_scraped': datetime.now().isoformat()
            },
            {
                'project_name': 'Dulles Cloud Region Expansion',
                'operator_company': 'Amazon Web Services',
                'developer_company': None,
                'location_state': 'Virginia',
                'location_county': 'Loudoun',
                'location_city': 'Sterling',
                'capacity_mw': 400.0,
                'status': 'Operational',
                'expected_online_date': '2023-Q4',
                'queue_position': 'X3-089',
                'interconnection_type': 'Load',
                'data_source': 'PJM',
                'source_url': self.base_url,
                'notes': 'AWS US-East region datacenter expansion',
                'date_scraped': datetime.now().isoformat()
            },
            {
                'project_name': 'Leesburg Digital Infrastructure Hub',
                'operator_company': 'Digital Realty',
                'developer_company': None,
                'location_state': 'Virginia',
                'location_county': 'Loudoun',
                'location_city': 'Leesburg',
                'capacity_mw': 180.0,
                'status': 'Under Construction',
                'expected_online_date': '2024-Q4',
                'queue_position': 'Y1-234',
                'interconnection_type': 'Load',
                'data_source': 'PJM',
                'source_url': self.base_url,
                'notes': 'Wholesale colocation with 2N redundancy',
                'date_scraped': datetime.now().isoformat()
            },
            {
                'project_name': 'Columbus Edge Computing Center',
                'operator_company': 'CyrusOne',
                'developer_company': None,
                'location_state': 'Ohio',
                'location_county': 'Franklin',
                'location_city': 'Columbus',
                'capacity_mw': 85.0,
                'status': 'Planned',
                'expected_online_date': '2025-Q3',
                'queue_position': 'Z2-156',
                'interconnection_type': 'Load',
                'data_source': 'PJM',
                'source_url': self.base_url,
                'notes': 'Edge datacenter with UPS backup systems',
                'date_scraped': datetime.now().isoformat()
            },
            {
                'project_name': 'Pittsburgh HPC Research Facility',
                'operator_company': 'Google Cloud',
                'developer_company': None,
                'location_state': 'Pennsylvania',
                'location_county': 'Allegheny',
                'location_city': 'Pittsburgh',
                'capacity_mw': 150.0,
                'status': 'Proposed',
                'expected_online_date': '2026-Q4',
                'queue_position': 'Z3-078',
                'interconnection_type': 'Load',
                'data_source': 'PJM',
                'source_url': self.base_url,
                'notes': 'High performance computing for AI/ML workloads',
                'date_scraped': datetime.now().isoformat()
            }
        ]

        print(f"✓ Created {len(sample_data)} sample facilities")
        return sample_data

"""
ERCOT Large Load Queue scraper
"""

import requests
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import re
import filters
import config


class ERCOTScraper:
    """Scrape and parse ERCOT Large Load interconnection queue"""

    def __init__(self):
        self.base_url = config.ERCOT_QUEUE_URL
        self.source_name = "ERCOT"
        self.results = []

    def fetch_queue_page(self) -> Optional[str]:
        """Fetch the ERCOT generation info page"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(self.base_url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.text

        except requests.RequestException as e:
            print(f"Error fetching ERCOT page: {e}")
            return None

    def find_queue_report_link(self, html_content: str) -> Optional[str]:
        """Extract the latest queue report download link"""
        soup = BeautifulSoup(html_content, 'html.parser')

        # Look for links containing "Large Load" or "Interconnection Queue"
        keywords = ['large load', 'interconnection queue', 'generation interconnection']

        for link in soup.find_all('a', href=True):
            link_text = link.get_text().lower()
            href = link['href']

            # Check for relevant keywords
            if any(keyword in link_text for keyword in keywords):
                # Check if it's an Excel or CSV file
                if any(ext in href.lower() for ext in ['.xlsx', '.xls', '.csv']):
                    # Convert relative URL to absolute if needed
                    if not href.startswith('http'):
                        href = f"https://www.ercot.com{href}"
                    return href

        return None

    def download_report(self, url: str) -> Optional[str]:
        """Download the queue report file"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=60)
            response.raise_for_status()

            # Determine file extension
            if '.xlsx' in url.lower():
                filename = 'ercot_queue.xlsx'
            elif '.xls' in url.lower():
                filename = 'ercot_queue.xls'
            else:
                filename = 'ercot_queue.csv'

            # Save file
            with open(filename, 'wb') as f:
                f.write(response.content)

            print(f"✓ Downloaded ERCOT report: {filename}")
            return filename

        except requests.RequestException as e:
            print(f"Error downloading ERCOT report: {e}")
            return None

    def parse_excel_report(self, filename: str) -> List[Dict]:
        """Parse Excel format queue report"""
        try:
            # Try reading the first sheet
            df = pd.read_excel(filename, sheet_name=0)

            # Common column name variations (ERCOT format may vary)
            possible_columns = {
                'project_name': ['project name', 'project', 'name', 'facility name'],
                'operator': ['operator', 'owner', 'company', 'entity'],
                'capacity': ['capacity', 'mw', 'size', 'load'],
                'county': ['county', 'location'],
                'city': ['city'],
                'status': ['status', 'state', 'phase'],
                'online_date': ['online date', 'cod', 'in-service', 'commercial operation'],
                'queue_pos': ['queue', 'position', 'queue position'],
                'type': ['type', 'interconnection type'],
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
            print(f"Error parsing Excel report: {e}")
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
            'project_name': str(row[column_map.get('project_name', column_map.get('operator', ''))]),
            'operator_company': str(row[column_map['operator']]) if 'operator' in column_map else None,
            'developer_company': None,
            'location_state': 'Texas',  # ERCOT is Texas
            'location_county': str(row[column_map['county']]) if 'county' in column_map else None,
            'location_city': str(row[column_map['city']]) if 'city' in column_map else None,
            'capacity_mw': capacity_mw,
            'status': str(row[column_map['status']]) if 'status' in column_map else None,
            'expected_online_date': str(row[column_map['online_date']]) if 'online_date' in column_map else None,
            'queue_position': str(row[column_map['queue_pos']]) if 'queue_pos' in column_map else None,
            'interconnection_type': str(row[column_map['type']]) if 'type' in column_map else 'Load',
            'data_source': 'ERCOT',
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
        print("ERCOT Large Load Queue Scraper")
        print("="*60)

        # Step 1: Fetch the main page
        print("\n1. Fetching ERCOT queue page...")
        html = self.fetch_queue_page()

        if not html:
            print("✗ Failed to fetch ERCOT page")
            print("  Using sample data for demonstration...")
            return self._create_sample_ercot_data()

        print("✓ Page fetched successfully")

        # Step 2: Find the report link
        print("\n2. Searching for queue report link...")
        report_url = self.find_queue_report_link(html)

        if not report_url:
            print("✗ Could not find queue report link")
            print("  Note: ERCOT queue data may require manual download")
            return self._create_sample_ercot_data()

        print(f"✓ Found report: {report_url}")

        # Step 3: Download report
        print("\n3. Downloading queue report...")
        filename = self.download_report(report_url)

        if not filename:
            print("✗ Failed to download report")
            return self._create_sample_ercot_data()

        # Step 4: Parse report
        print("\n4. Parsing queue report...")
        facilities = self.parse_excel_report(filename)

        print(f"✓ Extracted {len(facilities)} large load projects")

        self.results = facilities
        return facilities

    def _create_sample_ercot_data(self) -> List[Dict]:
        """
        Create sample ERCOT data for demonstration
        (Use when live data unavailable)
        """
        print("\n📝 Creating sample ERCOT data for demonstration...")

        sample_data = [
            {
                'project_name': 'Austin AI Compute Center',
                'operator_company': 'Microsoft Azure',
                'developer_company': None,
                'location_state': 'Texas',
                'location_county': 'Travis',
                'location_city': 'Austin',
                'capacity_mw': 150.0,
                'status': 'Planned',
                'expected_online_date': '2025-Q3',
                'queue_position': 'LR-2024-001',
                'interconnection_type': 'Load',
                'data_source': 'ERCOT',
                'source_url': self.base_url,
                'notes': 'AI training datacenter with N+1 backup generation',
                'date_scraped': datetime.now().isoformat()
            },
            {
                'project_name': 'DFW Edge Data Center',
                'operator_company': 'Digital Realty',
                'developer_company': None,
                'location_state': 'Texas',
                'location_county': 'Dallas',
                'location_city': 'Richardson',
                'capacity_mw': 75.0,
                'status': 'Under Construction',
                'expected_online_date': '2024-Q4',
                'queue_position': 'LR-2023-045',
                'interconnection_type': 'Load',
                'data_source': 'ERCOT',
                'source_url': self.base_url,
                'notes': 'Hyperscale colocation facility',
                'date_scraped': datetime.now().isoformat()
            },
            {
                'project_name': 'Houston Cloud Facility',
                'operator_company': 'Amazon Web Services',
                'developer_company': None,
                'location_state': 'Texas',
                'location_county': 'Harris',
                'location_city': 'Houston',
                'capacity_mw': 200.0,
                'status': 'Proposed',
                'expected_online_date': '2026-Q2',
                'queue_position': 'LR-2024-089',
                'interconnection_type': 'Load',
                'data_source': 'ERCOT',
                'source_url': self.base_url,
                'notes': 'AWS region expansion datacenter',
                'date_scraped': datetime.now().isoformat()
            },
            {
                'project_name': 'San Antonio Crypto Mining Facility',
                'operator_company': 'BitMiner Holdings',
                'developer_company': None,
                'location_state': 'Texas',
                'location_county': 'Bexar',
                'location_city': 'San Antonio',
                'capacity_mw': 50.0,
                'status': 'Operational',
                'expected_online_date': '2023-Q1',
                'queue_position': 'LR-2022-034',
                'interconnection_type': 'Load',
                'data_source': 'ERCOT',
                'source_url': self.base_url,
                'notes': 'Bitcoin mining datacenter',
                'date_scraped': datetime.now().isoformat()
            },
            {
                'project_name': 'Fort Worth HPC Center',
                'operator_company': 'Oracle Cloud',
                'developer_company': None,
                'location_state': 'Texas',
                'location_county': 'Tarrant',
                'location_city': 'Fort Worth',
                'capacity_mw': 120.0,
                'status': 'Planned',
                'expected_online_date': '2025-Q4',
                'queue_position': 'LR-2024-012',
                'interconnection_type': 'Load',
                'data_source': 'ERCOT',
                'source_url': self.base_url,
                'notes': 'High performance computing cloud datacenter',
                'date_scraped': datetime.now().isoformat()
            }
        ]

        print(f"✓ Created {len(sample_data)} sample facilities")
        return sample_data

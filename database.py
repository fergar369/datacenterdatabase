"""
Database schema and operations for Data Center Intelligence Database
"""

import sqlite3
from datetime import datetime
from typing import Optional, Dict, List, Tuple
import config


class DataCenterDB:
    """Handle all database operations"""

    def __init__(self, db_name: str = config.DB_NAME):
        self.db_name = db_name
        self.conn = None
        self.cursor = None

    def connect(self):
        """Establish database connection"""
        self.conn = sqlite3.connect(self.db_name)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.commit()
            self.conn.close()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def create_tables(self):
        """Create database schema"""

        # Facilities table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS facilities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_name TEXT NOT NULL,
                operator_company TEXT,
                developer_company TEXT,
                location_state TEXT,
                location_county TEXT,
                location_city TEXT,
                latitude REAL,
                longitude REAL,
                geocoding_confidence TEXT,
                capacity_mw REAL,
                status TEXT,
                expected_online_date TEXT,
                queue_position TEXT,
                interconnection_type TEXT,
                data_source TEXT NOT NULL,
                source_url TEXT,
                notes TEXT,
                date_scraped TEXT NOT NULL,
                match_reason TEXT
            )
        """)

        # Companies table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT UNIQUE NOT NULL,
                company_type TEXT,
                facilities_count INTEGER DEFAULT 0,
                total_mw REAL DEFAULT 0.0
            )
        """)

        # Data sources table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS data_sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_name TEXT UNIQUE NOT NULL,
                source_url TEXT,
                last_updated TEXT,
                records_found INTEGER DEFAULT 0,
                records_matched INTEGER DEFAULT 0
            )
        """)

        # Create indexes
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_operator
            ON facilities(operator_company)
        """)

        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_status
            ON facilities(status)
        """)

        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_source
            ON facilities(data_source)
        """)

        self.conn.commit()
        print("✓ Database schema created successfully")

    def insert_facility(self, facility_data: Dict) -> int:
        """Insert a facility record"""

        query = """
            INSERT INTO facilities (
                project_name, operator_company, developer_company,
                location_state, location_county, location_city,
                latitude, longitude, geocoding_confidence,
                capacity_mw, status, expected_online_date,
                queue_position, interconnection_type,
                data_source, source_url, notes, date_scraped, match_reason
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        values = (
            facility_data.get('project_name'),
            facility_data.get('operator_company'),
            facility_data.get('developer_company'),
            facility_data.get('location_state'),
            facility_data.get('location_county'),
            facility_data.get('location_city'),
            facility_data.get('latitude'),
            facility_data.get('longitude'),
            facility_data.get('geocoding_confidence'),
            facility_data.get('capacity_mw'),
            facility_data.get('status'),
            facility_data.get('expected_online_date'),
            facility_data.get('queue_position'),
            facility_data.get('interconnection_type'),
            facility_data.get('data_source'),
            facility_data.get('source_url'),
            facility_data.get('notes'),
            facility_data.get('date_scraped', datetime.now().isoformat()),
            facility_data.get('match_reason')
        )

        self.cursor.execute(query, values)
        self.conn.commit()
        return self.cursor.lastrowid

    def update_company_stats(self, company_name: str, company_type: str = "operator"):
        """Update company statistics"""

        # Check if company exists
        self.cursor.execute(
            "SELECT id FROM companies WHERE company_name = ?",
            (company_name,)
        )

        if not self.cursor.fetchone():
            # Insert new company
            self.cursor.execute(
                "INSERT INTO companies (company_name, company_type) VALUES (?, ?)",
                (company_name, company_type)
            )

        # Update counts
        self.cursor.execute("""
            UPDATE companies
            SET facilities_count = (
                SELECT COUNT(*) FROM facilities
                WHERE operator_company = ?
            ),
            total_mw = (
                SELECT COALESCE(SUM(capacity_mw), 0) FROM facilities
                WHERE operator_company = ?
            )
            WHERE company_name = ?
        """, (company_name, company_name, company_name))

        self.conn.commit()

    def update_data_source(self, source_name: str, source_url: str,
                          records_found: int, records_matched: int):
        """Update data source statistics"""

        self.cursor.execute("""
            INSERT OR REPLACE INTO data_sources
            (source_name, source_url, last_updated, records_found, records_matched)
            VALUES (?, ?, ?, ?, ?)
        """, (source_name, source_url, datetime.now().isoformat(),
              records_found, records_matched))

        self.conn.commit()

    def get_all_facilities(self) -> List[Dict]:
        """Get all facilities as list of dictionaries"""
        self.cursor.execute("SELECT * FROM facilities")
        return [dict(row) for row in self.cursor.fetchall()]

    def get_statistics(self) -> Dict:
        """Get database statistics"""

        stats = {}

        # Total projects
        self.cursor.execute("SELECT COUNT(*) FROM facilities")
        stats['total_projects'] = self.cursor.fetchone()[0]

        # Total MW
        self.cursor.execute("SELECT COALESCE(SUM(capacity_mw), 0) FROM facilities")
        stats['total_mw'] = self.cursor.fetchone()[0]

        # By status
        self.cursor.execute("""
            SELECT status, COUNT(*), COALESCE(SUM(capacity_mw), 0)
            FROM facilities
            GROUP BY status
        """)
        stats['by_status'] = {row[0]: {'count': row[1], 'mw': row[2]}
                              for row in self.cursor.fetchall()}

        # By state
        self.cursor.execute("""
            SELECT location_state, COUNT(*), COALESCE(SUM(capacity_mw), 0)
            FROM facilities
            WHERE location_state IS NOT NULL
            GROUP BY location_state
            ORDER BY SUM(capacity_mw) DESC
        """)
        stats['by_state'] = {row[0]: {'count': row[1], 'mw': row[2]}
                             for row in self.cursor.fetchall()}

        # By source
        self.cursor.execute("""
            SELECT data_source, COUNT(*), COALESCE(SUM(capacity_mw), 0)
            FROM facilities
            GROUP BY data_source
        """)
        stats['by_source'] = {row[0]: {'count': row[1], 'mw': row[2]}
                              for row in self.cursor.fetchall()}

        # Top 10 operators
        self.cursor.execute("""
            SELECT operator_company, COUNT(*), COALESCE(SUM(capacity_mw), 0)
            FROM facilities
            WHERE operator_company IS NOT NULL
            GROUP BY operator_company
            ORDER BY SUM(capacity_mw) DESC
            LIMIT 10
        """)
        stats['top_operators'] = [(row[0], row[1], row[2])
                                  for row in self.cursor.fetchall()]

        return stats

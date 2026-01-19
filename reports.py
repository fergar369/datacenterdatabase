"""
Report generation for data center intelligence database
"""

import pandas as pd
from typing import List, Dict
import config


class ReportGenerator:
    """Generate summary reports and exports"""

    def __init__(self, facilities: List[Dict], stats: Dict):
        self.facilities = facilities
        self.stats = stats

    def generate_csv_export(self, output_file: str = config.OUTPUT_CSV):
        """Export all facilities to CSV"""

        if not self.facilities:
            print("⚠ No facilities to export")
            return

        # Convert to DataFrame
        df = pd.DataFrame(self.facilities)

        # Reorder columns for better readability
        column_order = [
            'project_name', 'operator_company', 'capacity_mw', 'status',
            'location_city', 'location_county', 'location_state',
            'expected_online_date', 'data_source', 'match_reason',
            'latitude', 'longitude', 'queue_position',
            'interconnection_type', 'source_url', 'date_scraped'
        ]

        # Only include columns that exist
        column_order = [col for col in column_order if col in df.columns]
        df = df[column_order]

        # Sort by capacity (descending)
        df = df.sort_values('capacity_mw', ascending=False)

        # Save to CSV
        df.to_csv(output_file, index=False)
        print(f"✓ CSV export saved: {output_file}")
        print(f"  Exported {len(df)} facilities")

    def generate_statistics_report(self, output_file: str = config.OUTPUT_STATS):
        """Generate text-based statistics report"""

        lines = []
        lines.append("="*70)
        lines.append("DATA CENTER INTELLIGENCE DATABASE - STATISTICS REPORT")
        lines.append("="*70)
        lines.append("")

        # Overall statistics
        lines.append("OVERALL STATISTICS")
        lines.append("-" * 70)
        lines.append(f"Total Projects Found: {self.stats.get('total_projects', 0)}")
        lines.append(f"Total MW Capacity: {self.stats.get('total_mw', 0):,.1f} MW")
        lines.append("")

        # By status
        if 'by_status' in self.stats and self.stats['by_status']:
            lines.append("BREAKDOWN BY STATUS")
            lines.append("-" * 70)
            for status, data in sorted(self.stats['by_status'].items()):
                lines.append(f"  {status:25} {data['count']:3} projects   {data['mw']:8,.1f} MW")
            lines.append("")

        # By state
        if 'by_state' in self.stats and self.stats['by_state']:
            lines.append("BREAKDOWN BY STATE")
            lines.append("-" * 70)
            for state, data in sorted(self.stats['by_state'].items(),
                                     key=lambda x: x[1]['mw'], reverse=True):
                lines.append(f"  {state:25} {data['count']:3} projects   {data['mw']:8,.1f} MW")
            lines.append("")

        # By source
        if 'by_source' in self.stats and self.stats['by_source']:
            lines.append("BREAKDOWN BY DATA SOURCE")
            lines.append("-" * 70)
            for source, data in self.stats['by_source'].items():
                lines.append(f"  {source:25} {data['count']:3} projects   {data['mw']:8,.1f} MW")
            lines.append("")

        # Top operators
        if 'top_operators' in self.stats and self.stats['top_operators']:
            lines.append("TOP 10 OPERATORS BY MW CAPACITY")
            lines.append("-" * 70)
            for i, (operator, count, mw) in enumerate(self.stats['top_operators'], 1):
                lines.append(f"  {i:2}. {operator:30} {count:3} projects   {mw:8,.1f} MW")
            lines.append("")

        lines.append("="*70)

        # Write to file
        report_text = "\n".join(lines)

        with open(output_file, 'w') as f:
            f.write(report_text)

        print(f"✓ Statistics report saved: {output_file}")

        # Also print to console
        print("\n" + report_text)

    def generate_all_reports(self):
        """Generate all reports"""
        print("\n" + "="*60)
        print("Generating Reports")
        print("="*60)

        self.generate_csv_export()
        self.generate_statistics_report()


def create_readme():
    """Create README file explaining the outputs"""

    readme_content = """# Data Center Intelligence Database

## Overview

This database tracks data center projects from ERCOT and PJM interconnection queues using aggressive filtering to identify facilities based on:

- Primary keywords (data center, AI, cloud, crypto, etc.)
- Known data center operators (AWS, Google, Equinix, etc.)
- Secondary indicators (high MW + cooling/backup systems)

## Output Files

### 1. datacenter_intelligence.db
SQLite database containing all scraped and filtered data.

Tables:
- `facilities`: All identified data center projects
- `companies`: Operator statistics
- `data_sources`: Scraping metadata

### 2. datacenter_map.html
Interactive map visualization using Folium.

Features:
- Color-coded markers by status:
  * Green = Operational
  * Yellow = Under Construction
  * Blue = Planned
  * Gray = Proposed
- Marker size proportional to MW capacity
- Clickable popups with facility details
- Clustered markers for better performance

### 3. summary_report.csv
Exportable CSV containing all facility data, sorted by MW capacity.

### 4. statistics_summary.txt
Text report with:
- Total projects and MW capacity
- Breakdown by status, state, and data source
- Top 10 operators by MW capacity

## Updating Data

Run the update script to refresh data:

```bash
python update_data.py
```

This will:
1. Scrape latest ERCOT and PJM queue data
2. Apply filtering logic
3. Update database
4. Regenerate all visualizations and reports

## Database Schema

### facilities table
- `id`: Primary key
- `project_name`: Project/facility name
- `operator_company`: Operating company
- `capacity_mw`: Power capacity in MW
- `status`: Operational/Construction/Planned/Proposed
- `location_*`: City, county, state
- `latitude`, `longitude`: Geocoded coordinates
- `expected_online_date`: Planned operational date
- `data_source`: ERCOT or PJM
- `match_reason`: Why this was classified as a data center

## Filtering Criteria

### Primary Keywords
Any mention of: data center, datacenter, compute, AI, cloud, hyperscale, colocation,
crypto, blockchain, HPC, etc.

### Known Operators
AWS, Microsoft, Google, Meta, Equinix, Digital Realty, CyrusOne, and 20+ other
known data center companies.

### Secondary Indicators
Projects >10 MW mentioning: cooling, CRAC/CRAH, UPS, backup generation,
N+1 redundancy, etc.

## Notes

- Geocoding uses Nominatim (OpenStreetMap)
- Sample data included for demonstration when live data unavailable
- Database auto-created on first run
"""

    with open('README.md', 'w') as f:
        f.write(readme_content)

    print("✓ README.md created")

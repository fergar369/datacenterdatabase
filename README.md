# Data Center Intelligence Database

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

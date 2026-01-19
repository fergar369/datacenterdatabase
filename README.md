# Data Center Intelligence Database POC

A proof-of-concept system for scraping ERCOT and PJM interconnection queues to identify data center projects, store them in a SQLite database, and create interactive visualizations.

## Overview

This project uses aggressive filtering to identify data center and compute infrastructure projects from electrical grid interconnection queues. It tracks projects from major cloud providers (AWS, Google, Microsoft), colocation providers (Equinix, Digital Realty), and other large-scale compute facilities.

## Key Features

- **Aggressive Filtering**: Identifies data centers using keywords, company names, and technical indicators
- **Multi-Source Data**: Fetches from both ERCOT (Texas) and PJM (Eastern US) interconnection queues
- **SQLite Database**: Structured storage with facilities, companies, and data sources tables
- **Geocoding**: Converts locations to coordinates for mapping
- **Interactive Map**: Plotly-based visualization with status-based color coding
- **Comprehensive Reports**: CSV exports and statistical summaries

## Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### Running the POC

```bash
# Generate sample data (for demonstration)
python create_sample_data.py

# Create database and fetch data
python create_datacenter_db.py

# Add geocoding coordinates
python add_geocoding.py

# Generate all outputs
python generate_outputs.py

# Or run everything at once
python update_data.py
```

## Project Structure

```
datacenterdatabase/
├── create_datacenter_db.py      # Main database creation script
├── create_sample_data.py        # Generate sample interconnection queue data
├── add_geocoding.py             # Add geocoding coordinates
├── generate_outputs.py          # Create visualizations and reports
├── update_data.py               # Standalone update script
├── requirements.txt             # Python dependencies
├── datacenter_intelligence.db   # SQLite database (generated)
├── datacenter_map.html          # Interactive map (generated)
├── summary_report.csv           # Data export (generated)
└── statistics_summary.txt       # Statistics report (generated)
```

## Filtering Criteria

### Primary Keywords
Data centers are identified if they contain keywords like:
- `data center`, `datacenter`, `compute`, `AI`, `machine learning`
- `hyperscale`, `colocation`, `colo`, `server farm`, `cloud`
- `edge computing`, `crypto`, `bitcoin`, `blockchain`, `HPC`

### Known Data Center Companies
- Cloud: AWS, Azure, Google Cloud, Oracle Cloud, IBM Cloud
- Colocation: Equinix, Digital Realty, CyrusOne, QTS, CoreSite
- Specialized: Switch, Aligned, EdgeConneX, Iron Mountain, Vantage

### Technical Indicators
Large loads (>10 MW) with mentions of:
- `cooling`, `CRAC`, `CRAH`, `UPS`, `backup generation`
- `diesel generators`, `N+1`, `2N redundancy`

## Database Schema

### facilities table
- Project identification (name, operators, developers)
- Location (city, county, state, coordinates)
- Technical specs (capacity, status, online date)
- Metadata (queue position, data source, filtering criteria)

### companies table
- Company name and type (operator/developer/investor)
- Facilities count

### data_sources table
- Source name and URL
- Last updated timestamp
- Records found

## Output Files

### 1. datacenter_map.html
Interactive map with:
- Color-coded markers by status (Green=Operational, Orange=Construction, Blue=Planned, Gray=Proposed)
- Marker size proportional to MW capacity
- Hover popups with project details
- Filterable by status

### 2. summary_report.csv
Complete data export including:
- All facility details
- Geocoded coordinates
- Matching criteria used for identification
- Sortable and filterable in Excel/spreadsheet software

### 3. statistics_summary.txt
Statistical analysis including:
- Total projects and MW capacity
- Breakdowns by status, state, and data source
- Top 10 operators by MW
- Top 10 cities by MW

## Data Sources

### ERCOT (Texas)
- Source: Electric Reliability Council of Texas
- Coverage: Texas interconnection queue
- Access: gridstatus Python library
- URL: https://www.ercot.com/gridinfo/generation

### PJM (Eastern US)
- Source: PJM Interconnection
- Coverage: 13 states + DC in Eastern US
- Access: gridstatus Python library (requires API key)
- URL: https://www.pjm.com/planning/services-requests/interconnection-queues

## Sample Results (POC Demonstration)

Based on demonstration data:
- **21 data center projects** identified
- **4,220 MW** total capacity
- **201 MW** average project size
- **Texas** leads with 10 projects (1,795 MW)
- **Virginia** (Data Center Alley) has 4 projects (1,080 MW)

Top operators:
1. Meta Platforms - 570 MW
2. Amazon Web Services - 530 MW
3. Microsoft - 430 MW
4. Digital Realty - 400 MW
5. QTS Realty - 300 MW

## Environment Variables

- `PJM_API_KEY` - Optional API key for PJM data (free account at pjm.com)

## Technical Notes

### Geocoding
- Uses Nominatim (OpenStreetMap) for geocoding
- Falls back to hardcoded coordinates for known cities
- Respects rate limits (1.1 second delay between requests)
- Caches results to minimize API calls

### Network Restrictions
- If external API access is blocked, uses sample CSV data files
- Sample data represents realistic interconnection queue patterns
- All functionality works in offline mode with sample data

## Future Enhancements

- Additional ISOs (MISO, CAISO, ISONE, NYISO, SPP)
- Historical trend analysis
- Automated scheduling for periodic updates
- Email alerts for new projects
- Power usage effectiveness (PUE) tracking
- Investment and ownership analysis
- Export to additional formats (GeoJSON, KML)

## Requirements

- Python 3.7+
- pandas
- plotly
- geopy
- gridstatus
- sqlite3 (built-in)

## License

This is a proof-of-concept demonstration project.

## Contact

For questions or issues, refer to project documentation.

---

**Last Updated**: 2026-01-19

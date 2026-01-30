# DataCenter Intelligence Platform - Web Application

**Version:** 1.0
**Date:** 2026-01-30

---

## Overview

The **DataCenter Intelligence Platform** is a real-time web application for tracking verified data center and bitcoin mining projects. It combats misinformation by providing only verified data from reputable sources like ERCOT, PJM, and regulatory filings.

### Key Features

✓ **Real-time Updates** - Automatic data updates every 6 hours from verified sources
✓ **Interactive Maps** - Visualize project locations with clustering and detailed popups
✓ **Source Verification** - Confidence scoring (0-100) to filter out low-quality information
✓ **Operator Tracking** - Track major players and their project portfolios
✓ **Analytics Dashboard** - Charts and trends for capacity, status, and geography
✓ **Data Export** - Export to CSV, JSON, or GeoJSON formats
✓ **Notifications** - Real-time alerts for new verified projects

---

## Problem Solved

### The Challenge

LinkedIn and industry forums are flooded with **ChatGPT-written posts** from "experts" announcing data center projects that turn out to be:
- Smoke and mirrors (no queue position, no real project)
- Misleading capacity claims
- Projects that haven't been approved
- Shell companies with no track record

### The Solution

This platform provides:
1. **Only verified sources** - Direct from ERCOT/PJM interconnection queues
2. **Confidence scoring** - Each project gets a score (0-100) based on data quality
3. **Real data points** - Queue positions, approved equipment, actual timelines
4. **Problem tracking** - See challenges other projects encountered
5. **Near real-time** - Updates every 6 hours automatically

---

## Installation & Setup

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Internet connection for data scraping

### Quick Start

1. **Clone or navigate to the repository**
   ```bash
   cd /path/to/datacenterdatabase
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Access the web interface**
   ```
   Open your browser to: http://localhost:5000
   ```

That's it! The application will:
- Initialize the database
- Run an initial data update from ERCOT and PJM
- Start the web server
- Begin automatic updates every 6 hours

---

## Application Structure

```
datacenterdatabase/
├── app.py                      # Main Flask application
├── templates/                  # HTML templates
│   ├── base.html              # Base template with navigation
│   ├── index.html             # Home page
│   ├── dashboard.html         # Interactive map dashboard
│   ├── operators.html         # Operator statistics
│   └── analytics.html         # Charts and trends
├── static/                     # Static assets
│   ├── css/
│   │   └── style.css          # Custom styling
│   └── js/
│       └── app.js             # Frontend JavaScript
├── database.py                 # Database operations
├── scraper_ercot.py           # ERCOT data scraper
├── scraper_pjm.py             # PJM data scraper
├── filters.py                  # Data center identification
├── geocoding.py                # Location coordinates
└── requirements.txt            # Python dependencies
```

---

## Features & Usage

### 1. Home Page (`/`)

**Overview:**
- Live statistics (total projects, capacity, recent additions)
- Feature highlights
- Data source information
- Call to action

**Stats Displayed:**
- Total Projects
- Total Capacity (MW)
- New Projects (30 days)
- Number of Operators

### 2. Dashboard (`/dashboard`)

**Features:**
- **Interactive Map** - Leaflet.js with marker clustering
- **Advanced Filters:**
  - State (TX, VA, PA, OH, etc.)
  - Status (Operational, Construction, Planned, Proposed)
  - Minimum Capacity (MW)
  - Operator Name Search
  - Verification Status (Verified Only / All)
- **Projects Table** - Sortable, clickable rows
- **Project Details Modal** - Full information on click

**Map Markers:**
- Green = Verified projects (confidence ≥ 60%)
- Orange = Unverified projects (confidence < 60%)
- Size = Proportional to capacity (MW)

**Filters:**
```
State: [Dropdown] - All States, TX, VA, PA, OH
Status: [Dropdown] - All, Operational, Construction, Planned, Proposed
Min Capacity: [Input] - 0 MW (default)
Operator: [Text Input] - Search by name
Verified: [Dropdown] - Verified Only (default), All Projects, Unverified
```

### 3. Operators (`/operators`)

**Features:**
- List of all operators
- Facility count per operator
- Total and average capacity
- First seen / last seen dates
- Sortable table

**Metrics:**
- Facility Count
- Total Capacity (MW)
- Average Capacity (MW)
- First Seen (date)
- Last Seen (date)

### 4. Analytics (`/analytics`)

**Charts:**
1. **Capacity by Status** (Bar Chart)
   - Shows MW capacity for Operational, Construction, Planned, Proposed

2. **Capacity by State** (Pie Chart)
   - Distribution of capacity across states

3. **Projects by Source** (Doughnut Chart)
   - ERCOT vs PJM vs Other sources

4. **Top 10 Operators** (Horizontal Bar)
   - Largest operators by total capacity

---

## API Endpoints

All API endpoints return JSON responses.

### GET `/api/projects`

Get all projects with optional filtering.

**Query Parameters:**
- `state` - Filter by state code (e.g., "TX")
- `status` - Filter by status (e.g., "Operational")
- `min_capacity` - Minimum capacity in MW
- `operator` - Search operator name (partial match)
- `verified_only` - "true" to only return verified projects

**Response:**
```json
{
  "success": true,
  "count": 150,
  "projects": [
    {
      "id": 1,
      "project_name": "Example Data Center",
      "operator_company": "Example Corp",
      "capacity_mw": 250,
      "status": "Construction",
      "location_city": "Austin",
      "location_state": "TX",
      "confidence_score": 85.0,
      "is_verified": true,
      ...
    }
  ]
}
```

### GET `/api/projects/<id>`

Get detailed information for a specific project.

**Response:**
```json
{
  "success": true,
  "project": {
    "id": 1,
    "project_name": "Example Data Center",
    "operator_company": "Example Corp",
    "developer_company": "Builder Inc",
    "capacity_mw": 250,
    "status": "Construction",
    "location_city": "Austin",
    "location_county": "Travis",
    "location_state": "TX",
    "latitude": 30.2672,
    "longitude": -97.7431,
    "queue_position": "12345",
    "expected_online_date": "2025-06-01",
    "data_source": "ERCOT",
    "source_url": "https://...",
    "confidence_score": 85.0,
    "is_verified": true,
    "date_scraped": "2026-01-30T10:30:00"
  }
}
```

### GET `/api/operators`

Get statistics for all operators.

**Response:**
```json
{
  "success": true,
  "count": 25,
  "operators": [
    {
      "operator_company": "Example Corp",
      "facility_count": 5,
      "total_capacity_mw": 1250,
      "avg_capacity_mw": 250,
      "first_seen": "2024-01-15",
      "last_seen": "2026-01-30"
    }
  ]
}
```

### GET `/api/statistics`

Get overall platform statistics.

**Response:**
```json
{
  "success": true,
  "statistics": {
    "total_projects": 150,
    "total_capacity_mw": 15000.0,
    "by_status": [...],
    "by_state": [...],
    "by_source": [...],
    "recent_projects_30_days": 12,
    "last_update": "2026-01-30T10:00:00"
  }
}
```

### GET `/api/map_data`

Get project data formatted for map display (GeoJSON).

**Query Parameters:**
- `include_unverified` - "true" to include unverified projects

**Response:**
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [-97.7431, 30.2672]
      },
      "properties": {
        "id": 1,
        "name": "Example Data Center",
        "operator": "Example Corp",
        "capacity_mw": 250,
        "status": "Construction",
        "confidence_score": 85.0,
        "is_verified": true
      }
    }
  ]
}
```

### GET `/api/update`

Trigger manual data update (rate-limited).

**Response:**
```json
{
  "success": true,
  "message": "Data updated successfully",
  "results": {
    "ercot": {"success": true, "count": 5},
    "pjm": {"success": true, "count": 7}
  },
  "timestamp": "2026-01-30T11:00:00"
}
```

### GET `/api/updates/stream`

Server-Sent Events (SSE) stream for real-time updates.

**Events:**
- `new_projects` - Emitted when new verified projects are detected
- `heartbeat` - Periodic heartbeat to keep connection alive

**Usage:**
```javascript
const eventSource = new EventSource('/api/updates/stream');
eventSource.onmessage = function(event) {
  const data = JSON.parse(event.data);
  if (data.type === 'new_projects') {
    console.log(`${data.count} new projects!`);
  }
};
```

### GET `/api/export`

Export data in various formats.

**Query Parameters:**
- `format` - "csv", "json", or "geojson"

**Response:**
- CSV: File download
- JSON: JSON response with all projects
- GeoJSON: GeoJSON FeatureCollection

---

## Confidence Scoring System

Each project receives a confidence score (0-100) based on multiple factors:

### Scoring Breakdown

| Factor | Points | Description |
|--------|--------|-------------|
| **Data Source** | 40 | ERCOT/PJM: 40, Regulatory: 25, Other: 10 |
| **Queue Position** | 15 | Has queue number in interconnection queue |
| **Specific Capacity** | 10 | Has MW capacity specified |
| **Known Operator** | 20 | Recognized company (AWS, Google, etc.): 20, Unknown: 10 |
| **Timeline** | 10 | Has expected online date |
| **Location** | 5 | Has city and county specified |

### Verification Threshold

- **Verified:** Confidence ≥ 60%
- **Unverified:** Confidence < 60%

### Example Scores

**High Confidence (95%):**
```
Project: AWS Data Center
Source: ERCOT (40 pts)
Queue Position: 12345 (15 pts)
Capacity: 300 MW (10 pts)
Operator: Amazon Web Services (20 pts)
Timeline: June 2025 (10 pts)
Location: Austin, Travis County, TX (5 pts)
Total: 100 pts → Capped at 95%
```

**Medium Confidence (65%):**
```
Project: Generic Data Center
Source: ERCOT (40 pts)
Queue Position: 67890 (15 pts)
Capacity: Not specified (0 pts)
Operator: Unknown LLC (10 pts)
Timeline: None (0 pts)
Location: Texas (0 pts)
Total: 65 pts
```

**Low Confidence (35%):**
```
Project: Unnamed
Source: Press Release (25 pts)
Queue Position: None (0 pts)
Capacity: "Large" (0 pts)
Operator: Shell Company (10 pts)
Timeline: "Soon" (0 pts)
Location: Vague (0 pts)
Total: 35 pts
```

---

## Automatic Updates

### Update Schedule

- **Frequency:** Every 6 hours
- **Sources:** ERCOT, PJM interconnection queues
- **Process:**
  1. Scrape latest data from sources
  2. Filter for data center projects
  3. Geocode new locations
  4. Calculate confidence scores
  5. Update database
  6. Notify connected clients

### Manual Updates

Trigger manual update:
1. Click "Update Data" button in navigation
2. Wait for update to complete (usually 30-60 seconds)
3. Page data will refresh automatically

### Update Configuration

Edit in `app.py`:
```python
AUTO_UPDATE_INTERVAL_HOURS = 6  # Change to desired hours
```

---

## Data Sources

### ERCOT (Texas)

**What we scrape:**
- Generation Interconnection Queue
- Large Load Interconnection Queue

**Data quality:**
- ✓ Official utility data
- ✓ Queue positions
- ✓ Specific capacity (MW)
- ✓ Timeline information
- ✓ County-level location

**Coverage:**
- All of Texas (ERCOT territory)
- ~90% of Texas electricity market

### PJM (Mid-Atlantic)

**What we scrape:**
- New Services Queue

**Data quality:**
- ✓ Official utility data
- ✓ Queue positions
- ✓ Specific capacity (MW)
- ✓ Status tracking

**Coverage:**
- Virginia, Pennsylvania, Ohio
- Maryland, Delaware, New Jersey
- Parts of West Virginia, Kentucky, Indiana, Illinois, Michigan, North Carolina, Tennessee

---

## Deployment

### Local Development

```bash
python app.py
```

Access at: http://localhost:5000

### Production Deployment

#### Option 1: Gunicorn (Recommended)

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

#### Option 2: Docker

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

Build and run:
```bash
docker build -t datacenter-intelligence .
docker run -p 5000:5000 datacenter-intelligence
```

#### Option 3: Cloud Platforms

**Heroku:**
```bash
# Create Procfile
echo "web: gunicorn app:app" > Procfile

# Deploy
heroku create datacenter-intelligence
git push heroku main
```

**AWS Elastic Beanstalk:**
```bash
# Install EB CLI
pip install awsebcli

# Initialize and deploy
eb init -p python-3.11 datacenter-intelligence
eb create datacenter-intelligence-env
eb deploy
```

**Google Cloud Run:**
```bash
gcloud run deploy datacenter-intelligence \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Environment Variables

Set these for production:

```bash
export SECRET_KEY="your-secret-key-here"
export DATABASE_PATH="/path/to/datacenter_intelligence.db"
export FLASK_ENV="production"
```

### Database Considerations

**Development:**
- SQLite (default)
- File-based: `datacenter_intelligence.db`

**Production (Optional):**
- Can upgrade to PostgreSQL for better concurrency
- Update database connection in `database.py`

---

## Troubleshooting

### Common Issues

#### 1. "Address already in use" error

Another process is using port 5000.

**Solution:**
```bash
# Find process
lsof -i :5000

# Kill process
kill -9 <PID>

# Or use different port
python app.py --port 5001
```

#### 2. Database locked errors

Multiple processes accessing SQLite simultaneously.

**Solution:**
- Use only one worker in development: `python app.py`
- For production, upgrade to PostgreSQL

#### 3. Scraping errors

Network issues or source website changes.

**Solution:**
- Check internet connection
- Verify source URLs still work
- Update scrapers if website structure changed

#### 4. No projects showing on map

Geocoding failed or projects have no coordinates.

**Solution:**
```python
# Re-run geocoding
from geocoding import Geocoder
from database import Database

db = Database()
geocoder = Geocoder()

facilities = db.get_all_facilities()
for facility in facilities:
    if not facility.get('latitude'):
        geocoder.geocode_project(facility)
        db.update_facility(facility)
```

#### 5. Real-time updates not working

Server-Sent Events connection failed.

**Solution:**
- Check browser console for errors
- Verify `/api/updates/stream` endpoint works
- Some proxies block SSE - try direct connection

---

## Security Considerations

### Production Checklist

- [ ] Change SECRET_KEY from default
- [ ] Enable HTTPS (use SSL certificate)
- [ ] Set proper CORS origins (restrict to your domain)
- [ ] Rate limit API endpoints
- [ ] Add authentication for sensitive operations
- [ ] Regular security updates for dependencies
- [ ] Database backups
- [ ] Monitor for suspicious activity

### Rate Limiting

Consider adding Flask-Limiter:
```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=get_remote_address)

@app.route('/api/update')
@limiter.limit("1 per minute")
def api_update():
    # ...
```

---

## Performance Optimization

### Tips

1. **Enable Caching:**
   ```python
   from flask_caching import Cache
   cache = Cache(app, config={'CACHE_TYPE': 'simple'})

   @app.route('/api/projects')
   @cache.cached(timeout=300)  # 5 minutes
   def api_projects():
       # ...
   ```

2. **Database Indexing:**
   ```python
   # Add indexes in database.py
   cursor.execute("CREATE INDEX IF NOT EXISTS idx_state ON facilities(location_state)")
   cursor.execute("CREATE INDEX IF NOT EXISTS idx_status ON facilities(status)")
   ```

3. **Pagination:**
   ```python
   # Add pagination to API endpoints
   page = request.args.get('page', 1, type=int)
   per_page = request.args.get('per_page', 50, type=int)
   ```

4. **Use CDN for Static Assets:**
   - Bootstrap, Leaflet, Chart.js already use CDN
   - Consider CDN for custom CSS/JS in production

---

## Future Enhancements

### Planned Features

1. **User Accounts**
   - Save custom filters
   - Watchlists for specific operators
   - Email notifications for new projects

2. **Advanced Search**
   - Full-text search across all fields
   - Saved searches
   - Complex filter combinations

3. **Historical Tracking**
   - Track project status changes over time
   - Timeline view of project lifecycle
   - "What changed?" notifications

4. **Additional Data Sources**
   - MISO (Midwest)
   - CAISO (California)
   - SPP (Southwest)
   - Regulatory filings (FERC, state PUCs)

5. **AI/ML Features**
   - Predict project success probability
   - Anomaly detection (suspicious projects)
   - Automatic problem categorization

6. **Enhanced Analytics**
   - Time series forecasting
   - Regional capacity trends
   - Operator strategy analysis

7. **API Rate Limiting & Keys**
   - Public API with rate limits
   - API keys for premium access
   - Webhooks for integrations

8. **Mobile App**
   - iOS/Android apps
   - Push notifications
   - Offline mode

---

## Contributing

### Development Setup

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

### Code Style

- Python: PEP 8
- JavaScript: ES6+
- HTML: Semantic, accessible markup
- CSS: BEM naming convention

### Testing

```bash
# Run tests (when implemented)
python -m pytest tests/
```

---

## Support & Contact

### Issues

Report bugs and feature requests:
- GitHub Issues: [repository URL]
- Email: [your email]

### Documentation

- Project Summary: `PROJECT_SUMMARY.md`
- Power Configuration: `POWER_CONFIGURATION_GUIDE.md`
- This README: `WEB_APP_README.md`

---

## License

[Specify your license here]

---

## Acknowledgments

- **Data Sources:** ERCOT, PJM
- **Libraries:** Flask, Leaflet.js, Bootstrap, Chart.js
- **Inspiration:** Frustration with LinkedIn misinformation

---

**Built with 🔋 to combat data center misinformation**

*Last Updated: 2026-01-30*

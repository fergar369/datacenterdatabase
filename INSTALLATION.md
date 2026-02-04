# Installation Guide

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note:** If you encounter permission errors with system packages, use a virtual environment:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python app.py
```

The application will:
1. Initialize the database
2. Run an initial data update
3. Start the web server at http://localhost:5000
4. Begin automatic updates every 6 hours

### 3. Access the Web Interface

Open your browser to: **http://localhost:5000**

## Dependencies

### Core Dependencies
- Flask 3.0+ (Web framework)
- Flask-CORS 4.0+ (Cross-origin resource sharing)
- pandas 2.0+ (Data processing)
- requests 2.31+ (HTTP requests)
- beautifulsoup4 4.12+ (HTML parsing)
- geopy 2.4+ (Geocoding)
- folium 0.15+ (Map generation)

### Full List
See `requirements.txt` for complete dependency list.

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'flask'"

**Solution:** Install Flask
```bash
pip install Flask Flask-CORS
```

### Issue: "Permission denied" or "RECORD file not found"

**Solution:** Use virtual environment (see above)

### Issue: "Address already in use"

**Solution:** Port 5000 is taken by another process
```bash
# Use different port
python app.py --port 5001

# Or kill the process using port 5000
lsof -i :5000
kill -9 <PID>
```

### Issue: "Database is locked"

**Solution:** Only run one instance of the application in development mode

## Production Deployment

See `WEB_APP_README.md` for detailed production deployment instructions.

### Quick Production Setup with Gunicorn

```bash
# Install Gunicorn
pip install gunicorn

# Run with 4 worker processes
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Environment Variables

Optional configuration via environment variables:

```bash
export SECRET_KEY="your-secret-key-here"
export DATABASE_PATH="/path/to/database.db"
export AUTO_UPDATE_INTERVAL_HOURS="6"
```

## First Run

On first run, the application will:
1. Create `datacenter_intelligence.db` SQLite database
2. Scrape data from ERCOT and PJM sources
3. Process and geocode projects
4. Populate the database

This may take 1-2 minutes depending on internet speed.

## Verifying Installation

Check that everything works:

```bash
# Test API endpoints
curl http://localhost:5000/api/statistics
curl http://localhost:5000/api/projects?verified_only=true

# Check database
sqlite3 datacenter_intelligence.db "SELECT COUNT(*) FROM facilities;"
```

## Support

For issues or questions:
- See `WEB_APP_README.md` for comprehensive documentation
- Check `PROJECT_SUMMARY.md` for project overview
- Review `CLAUDE.md` for development guidelines

"""
DataCenter Intelligence Platform - Web Application

A real-time web application for tracking verified data center and bitcoin mining
projects in Texas and other regions, with automatic updates from reputable sources.

Features:
- Interactive maps with project locations
- Real-time updates from ERCOT, PJM, and regulatory sources
- Operator profiles and equipment specifications
- Problem tracking and analysis
- Source verification to filter out misinformation
- Subscription-based alerts for new projects
"""

from flask import Flask, render_template, jsonify, request, send_file, Response
from flask_cors import CORS
import json
import sqlite3
from datetime import datetime, timedelta
import os
from typing import List, Dict, Optional
import threading
import time

# Import existing modules
from database import DataCenterDB
from scraper_ercot import ERCOTScraper
from scraper_pjm import PJMScraper
import filters
from geocoding import Geocoder
from reports import ReportGenerator

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['DATABASE_PATH'] = 'datacenter_intelligence.db'

# Global database instance
db = DataCenterDB(app.config['DATABASE_PATH'])

# Auto-update configuration
AUTO_UPDATE_INTERVAL_HOURS = 6
last_update_time = None
update_lock = threading.Lock()


class ProjectVerifier:
    """Verifies project authenticity and calculates confidence scores"""

    @staticmethod
    def calculate_confidence_score(project: Dict) -> float:
        """
        Calculate confidence score (0-100) based on data quality indicators

        High confidence indicators:
        - Direct from utility interconnection queue
        - Has queue position number
        - Has specific capacity and timeline
        - Company is known operator (not shell company)
        - Multiple data points corroborate

        Low confidence indicators:
        - Vague information
        - No queue position
        - Unknown operator
        - Single source only
        """
        score = 0.0

        # Source quality (40 points)
        if project.get('data_source') in ['ERCOT', 'PJM']:
            score += 40
        elif project.get('data_source') in ['Regulatory Filing', 'Press Release']:
            score += 25
        else:
            score += 10

        # Has queue position (15 points)
        if project.get('queue_position'):
            score += 15

        # Specific capacity (10 points)
        if project.get('capacity_mw') and project.get('capacity_mw') > 0:
            score += 10

        # Known operator (20 points)
        known_operators = [
            'Amazon', 'Microsoft', 'Google', 'Meta', 'Oracle',
            'Digital Realty', 'Equinix', 'CyrusOne', 'QTS',
            'Riot Platforms', 'Marathon Digital', 'Core Scientific'
        ]
        operator = project.get('operator_company', '')
        if any(known in operator for known in known_operators):
            score += 20
        elif operator and len(operator) > 3:
            score += 10

        # Has timeline (10 points)
        if project.get('expected_online_date'):
            score += 10

        # Has specific location (5 points)
        if project.get('location_city') and project.get('location_county'):
            score += 5

        return min(score, 100.0)

    @staticmethod
    def is_verified(project: Dict) -> bool:
        """Determine if project meets verification threshold"""
        score = ProjectVerifier.calculate_confidence_score(project)
        return score >= 60.0  # 60% confidence threshold


def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(app.config['DATABASE_PATH'])
    conn.row_factory = sqlite3.Row
    return conn


def format_project(row) -> Dict:
    """Format database row as project dictionary"""
    project = dict(row)

    # Add confidence score
    project['confidence_score'] = ProjectVerifier.calculate_confidence_score(project)
    project['is_verified'] = project['confidence_score'] >= 60.0

    # Format dates
    if project.get('date_scraped'):
        project['date_scraped_formatted'] = datetime.fromisoformat(
            project['date_scraped']
        ).strftime('%Y-%m-%d %H:%M')

    if project.get('expected_online_date'):
        try:
            project['expected_online_date_formatted'] = datetime.fromisoformat(
                project['expected_online_date']
            ).strftime('%Y-%m')
        except:
            project['expected_online_date_formatted'] = project['expected_online_date']

    return project


# ============================================================================
# WEB ROUTES
# ============================================================================

@app.route('/')
def index():
    """Home page with overview"""
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    """Main dashboard with interactive map and filters"""
    return render_template('dashboard.html')


@app.route('/operators')
def operators():
    """Operator profiles page"""
    return render_template('operators.html')


@app.route('/analytics')
def analytics():
    """Analytics and trends page"""
    return render_template('analytics.html')


# ============================================================================
# API ROUTES
# ============================================================================

@app.route('/api/projects')
def api_projects():
    """
    Get all projects with optional filtering

    Query parameters:
    - state: Filter by state (TX, VA, etc.)
    - status: Filter by status (Operational, Construction, etc.)
    - min_capacity: Minimum capacity in MW
    - operator: Filter by operator name
    - verified_only: Only return verified projects (true/false)
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Build query with filters
    query = "SELECT * FROM facilities WHERE 1=1"
    params = []

    # State filter
    if request.args.get('state'):
        query += " AND location_state = ?"
        params.append(request.args.get('state'))

    # Status filter
    if request.args.get('status'):
        query += " AND status = ?"
        params.append(request.args.get('status'))

    # Minimum capacity filter
    if request.args.get('min_capacity'):
        query += " AND capacity_mw >= ?"
        params.append(float(request.args.get('min_capacity')))

    # Operator filter
    if request.args.get('operator'):
        query += " AND operator_company LIKE ?"
        params.append(f"%{request.args.get('operator')}%")

    # Order by date
    query += " ORDER BY date_scraped DESC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    projects = [format_project(row) for row in rows]

    # Filter verified only if requested
    if request.args.get('verified_only', '').lower() == 'true':
        projects = [p for p in projects if p['is_verified']]

    return jsonify({
        'success': True,
        'count': len(projects),
        'projects': projects
    })


@app.route('/api/projects/<int:project_id>')
def api_project_detail(project_id):
    """Get detailed information for a specific project"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM facilities WHERE id = ?", (project_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return jsonify({'success': False, 'error': 'Project not found'}), 404

    project = format_project(row)

    return jsonify({
        'success': True,
        'project': project
    })


@app.route('/api/operators')
def api_operators():
    """Get operator statistics"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            operator_company,
            COUNT(*) as facility_count,
            SUM(capacity_mw) as total_capacity_mw,
            AVG(capacity_mw) as avg_capacity_mw,
            MIN(date_scraped) as first_seen,
            MAX(date_scraped) as last_seen
        FROM facilities
        WHERE operator_company IS NOT NULL AND operator_company != ''
        GROUP BY operator_company
        ORDER BY total_capacity_mw DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    operators = []
    for row in rows:
        operator = dict(row)
        operator['first_seen'] = operator['first_seen'][:10] if operator['first_seen'] else None
        operator['last_seen'] = operator['last_seen'][:10] if operator['last_seen'] else None
        operators.append(operator)

    return jsonify({
        'success': True,
        'count': len(operators),
        'operators': operators
    })


@app.route('/api/statistics')
def api_statistics():
    """Get overall statistics"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Total projects
    cursor.execute("SELECT COUNT(*) as count FROM facilities")
    total_projects = cursor.fetchone()['count']

    # Total capacity
    cursor.execute("SELECT SUM(capacity_mw) as total FROM facilities")
    total_capacity = cursor.fetchone()['total'] or 0

    # By status
    cursor.execute("""
        SELECT status, COUNT(*) as count, SUM(capacity_mw) as capacity
        FROM facilities
        GROUP BY status
    """)
    by_status = [dict(row) for row in cursor.fetchall()]

    # By state
    cursor.execute("""
        SELECT location_state, COUNT(*) as count, SUM(capacity_mw) as capacity
        FROM facilities
        WHERE location_state IS NOT NULL
        GROUP BY location_state
        ORDER BY capacity DESC
    """)
    by_state = [dict(row) for row in cursor.fetchall()]

    # By source
    cursor.execute("""
        SELECT data_source, COUNT(*) as count
        FROM facilities
        GROUP BY data_source
    """)
    by_source = [dict(row) for row in cursor.fetchall()]

    # Recent projects (last 30 days)
    thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM facilities
        WHERE date_scraped >= ?
    """, (thirty_days_ago,))
    recent_count = cursor.fetchone()['count']

    conn.close()

    return jsonify({
        'success': True,
        'statistics': {
            'total_projects': total_projects,
            'total_capacity_mw': round(total_capacity, 1),
            'by_status': by_status,
            'by_state': by_state,
            'by_source': by_source,
            'recent_projects_30_days': recent_count,
            'last_update': last_update_time.isoformat() if last_update_time else None
        }
    })


@app.route('/api/map_data')
def api_map_data():
    """Get project data formatted for map display"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM facilities
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        ORDER BY capacity_mw DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    features = []
    for row in rows:
        project = format_project(row)

        # Only include verified projects by default
        if not project['is_verified'] and request.args.get('include_unverified') != 'true':
            continue

        feature = {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [project['longitude'], project['latitude']]
            },
            'properties': {
                'id': project['id'],
                'name': project['project_name'],
                'operator': project['operator_company'],
                'capacity_mw': project['capacity_mw'],
                'status': project['status'],
                'location': f"{project['location_city']}, {project['location_state']}",
                'confidence_score': project['confidence_score'],
                'is_verified': project['is_verified'],
                'data_source': project['data_source']
            }
        }
        features.append(feature)

    geojson = {
        'type': 'FeatureCollection',
        'features': features
    }

    return jsonify(geojson)


@app.route('/api/update')
def api_update():
    """Trigger manual data update"""
    global last_update_time

    # Check if update is already in progress
    if not update_lock.acquire(blocking=False):
        return jsonify({
            'success': False,
            'error': 'Update already in progress'
        }), 429

    try:
        update_results = run_data_update()
        last_update_time = datetime.now()

        return jsonify({
            'success': True,
            'message': 'Data updated successfully',
            'results': update_results,
            'timestamp': last_update_time.isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        update_lock.release()


@app.route('/api/updates/stream')
def api_updates_stream():
    """Server-sent events stream for real-time updates"""
    def event_stream():
        """Generate server-sent events"""
        while True:
            # Check for new projects
            conn = get_db_connection()
            cursor = conn.cursor()

            # Get projects from last 5 minutes
            five_min_ago = (datetime.now() - timedelta(minutes=5)).isoformat()
            cursor.execute("""
                SELECT * FROM facilities
                WHERE date_scraped >= ?
                ORDER BY date_scraped DESC
            """, (five_min_ago,))

            rows = cursor.fetchall()
            conn.close()

            if rows:
                projects = [format_project(row) for row in rows]
                verified_projects = [p for p in projects if p['is_verified']]

                if verified_projects:
                    data = {
                        'type': 'new_projects',
                        'count': len(verified_projects),
                        'projects': verified_projects
                    }
                    yield f"data: {json.dumps(data)}\n\n"

            # Send heartbeat
            yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': datetime.now().isoformat()})}\n\n"

            time.sleep(30)  # Check every 30 seconds

    return Response(event_stream(), mimetype='text/event-stream')


@app.route('/api/export')
def api_export():
    """Export data in various formats"""
    format_type = request.args.get('format', 'csv')

    if format_type not in ['csv', 'json', 'geojson']:
        return jsonify({'success': False, 'error': 'Invalid format'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM facilities ORDER BY date_scraped DESC")
    rows = cursor.fetchall()
    conn.close()

    projects = [format_project(row) for row in rows]

    if format_type == 'json':
        return jsonify({
            'success': True,
            'count': len(projects),
            'projects': projects,
            'exported_at': datetime.now().isoformat()
        })

    elif format_type == 'csv':
        # Generate CSV
        report_gen = ReportGenerator(db)
        csv_path = 'export_temp.csv'
        report_gen.generate_summary_report(csv_path)

        return send_file(
            csv_path,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'datacenter_export_{datetime.now().strftime("%Y%m%d")}.csv'
        )

    elif format_type == 'geojson':
        # Generate GeoJSON
        features = []
        for project in projects:
            if project.get('latitude') and project.get('longitude'):
                feature = {
                    'type': 'Feature',
                    'geometry': {
                        'type': 'Point',
                        'coordinates': [project['longitude'], project['latitude']]
                    },
                    'properties': {k: v for k, v in project.items() if k not in ['latitude', 'longitude']}
                }
                features.append(feature)

        geojson = {
            'type': 'FeatureCollection',
            'features': features
        }

        return jsonify(geojson)


# ============================================================================
# BACKGROUND TASKS
# ============================================================================

def run_data_update() -> Dict:
    """Run data update from all sources"""
    results = {
        'ercot': {'success': False, 'count': 0, 'error': None},
        'pjm': {'success': False, 'count': 0, 'error': None}
    }

    geocoder = Geocoder()
    # No need to instantiate filter class

    # Update ERCOT data
    try:
        ercot_scraper = ERCOTScraper()
        ercot_projects = ercot_scraper.scrape()

        # Filter for data centers
        dc_projects = [p for p in ercot_projects if filters.is_data_center_project(p)[0]]

        # Geocode and save
        for project in dc_projects:
            geocoder.geocode_project(project)
            db.insert_facility(project)

        results['ercot'] = {
            'success': True,
            'count': len(dc_projects),
            'error': None
        }
    except Exception as e:
        results['ercot']['error'] = str(e)

    # Update PJM data
    try:
        pjm_scraper = PJMScraper()
        pjm_projects = pjm_scraper.scrape()

        # Filter for data centers
        dc_projects = [p for p in pjm_projects if filters.is_data_center_project(p)[0]]

        # Geocode and save
        for project in dc_projects:
            geocoder.geocode_project(project)
            db.insert_facility(project)

        results['pjm'] = {
            'success': True,
            'count': len(dc_projects),
            'error': None
        }
    except Exception as e:
        results['pjm']['error'] = str(e)

    return results


def auto_update_worker():
    """Background worker for automatic updates"""
    global last_update_time

    while True:
        try:
            # Wait for interval
            time.sleep(AUTO_UPDATE_INTERVAL_HOURS * 3600)

            # Acquire lock and update
            with update_lock:
                print(f"[{datetime.now()}] Running automatic data update...")
                results = run_data_update()
                last_update_time = datetime.now()
                print(f"[{datetime.now()}] Update completed: {results}")
        except Exception as e:
            print(f"[{datetime.now()}] Auto-update error: {e}")


def start_background_tasks():
    """Start background update worker"""
    update_thread = threading.Thread(target=auto_update_worker, daemon=True)
    update_thread.start()
    print(f"Background update worker started (interval: {AUTO_UPDATE_INTERVAL_HOURS} hours)")


# ============================================================================
# APPLICATION STARTUP
# ============================================================================

if __name__ == '__main__':
    # Initialize database
    print("Initializing database...")
    db.connect()
    db.create_tables()

    # Run initial update
    print("Running initial data update...")
    try:
        results = run_data_update()
        last_update_time = datetime.now()
        print(f"Initial update completed: {results}")
    except Exception as e:
        print(f"Initial update error: {e}")

    # Start background tasks
    start_background_tasks()

    # Run Flask app
    print("Starting Flask application...")
    print("Access the application at: http://localhost:5000")
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=False  # Disable reloader to prevent double background threads
    )

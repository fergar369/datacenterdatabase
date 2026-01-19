#!/usr/bin/env python3
"""
Generate all output files from the datacenter intelligence database
- datacenter_map.html (interactive map)
- summary_report.csv (all data exportable)
- statistics_summary.txt (statistics and breakdowns)
"""

import sqlite3
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

def load_data():
    """Load data from database"""
    conn = sqlite3.connect('datacenter_intelligence.db')

    # Load facilities
    facilities_df = pd.read_sql_query('''
        SELECT * FROM facilities
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
    ''', conn)

    # Load companies
    companies_df = pd.read_sql_query('SELECT * FROM companies ORDER BY facilities_count DESC', conn)

    # Load data sources
    sources_df = pd.read_sql_query('SELECT * FROM data_sources', conn)

    conn.close()

    return facilities_df, companies_df, sources_df

def generate_interactive_map(facilities_df):
    """Generate interactive map using Plotly"""
    print("Generating interactive map...")

    # Color mapping for status
    status_colors = {
        'Operational': 'green',
        'Under Construction': 'orange',
        'Planned': 'blue',
        'Proposed': 'gray'
    }

    # Prepare data for plotting
    facilities_df['color'] = facilities_df['status'].map(status_colors).fillna('gray')
    facilities_df['size'] = facilities_df['capacity_mw'] / 10  # Scale marker size

    # Create figure
    fig = go.Figure()

    # Add traces for each status
    for status in facilities_df['status'].unique():
        df_status = facilities_df[facilities_df['status'] == status]

        hover_text = []
        for idx, row in df_status.iterrows():
            text = f"<b>{row['project_name']}</b><br>"
            text += f"Operator: {row['operator_company']}<br>"
            text += f"Capacity: {row['capacity_mw']} MW<br>"
            text += f"Location: {row['location_city']}, {row['location_state']}<br>"
            text += f"Status: {row['status']}<br>"
            text += f"Expected Online: {row['expected_online_date']}<br>"
            text += f"Source: {row['data_source']}"
            hover_text.append(text)

        fig.add_trace(go.Scattergeo(
            lon=df_status['longitude'],
            lat=df_status['latitude'],
            text=hover_text,
            mode='markers',
            name=status,
            marker=dict(
                size=df_status['size'],
                color=status_colors.get(status, 'gray'),
                line=dict(width=1, color='white'),
                sizemode='diameter'
            ),
            hovertemplate='%{text}<extra></extra>'
        ))

    # Update layout
    fig.update_layout(
        title={
            'text': 'Data Center Intelligence Map<br><sub>ERCOT and PJM Interconnection Queue Projects</sub>',
            'x': 0.5,
            'xanchor': 'center'
        },
        geo=dict(
            scope='usa',
            showland=True,
            landcolor='rgb(243, 243, 243)',
            coastlinecolor='rgb(204, 204, 204)',
            projection_type='albers usa',
            showlakes=True,
            lakecolor='rgb(200, 220, 255)'
        ),
        height=700,
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(255, 255, 255, 0.8)"
        )
    )

    # Save map
    fig.write_html('datacenter_map.html')
    print("✓ Interactive map saved to: datacenter_map.html")

def generate_summary_csv(facilities_df):
    """Generate summary CSV report"""
    print("\nGenerating summary CSV...")

    # Select relevant columns and rename for clarity
    export_df = facilities_df[[
        'project_name', 'operator_company', 'developer_company',
        'location_city', 'location_county', 'location_state',
        'latitude', 'longitude', 'capacity_mw', 'status',
        'expected_online_date', 'queue_position', 'interconnection_type',
        'data_source', 'matching_criteria', 'date_scraped'
    ]].copy()

    export_df.columns = [
        'Project Name', 'Operator', 'Developer',
        'City', 'County', 'State',
        'Latitude', 'Longitude', 'Capacity (MW)', 'Status',
        'Expected Online Date', 'Queue Position', 'Interconnection Type',
        'Data Source', 'Matching Criteria', 'Date Scraped'
    ]

    # Sort by capacity descending
    export_df = export_df.sort_values('Capacity (MW)', ascending=False)

    # Save to CSV
    export_df.to_csv('summary_report.csv', index=False)
    print(f"✓ Summary CSV saved to: summary_report.csv ({len(export_df)} projects)")

def generate_statistics_summary(facilities_df, companies_df, sources_df):
    """Generate statistics summary text file"""
    print("\nGenerating statistics summary...")

    lines = []
    lines.append("="*70)
    lines.append("DATA CENTER INTELLIGENCE DATABASE - STATISTICS SUMMARY")
    lines.append("="*70)
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    # Overall Statistics
    lines.append("-"*70)
    lines.append("OVERALL STATISTICS")
    lines.append("-"*70)
    lines.append(f"Total Projects Found: {len(facilities_df)}")
    lines.append(f"Total MW Capacity: {facilities_df['capacity_mw'].sum():,.0f} MW")
    lines.append(f"Average Project Size: {facilities_df['capacity_mw'].mean():.1f} MW")
    lines.append(f"Largest Project: {facilities_df['capacity_mw'].max():.0f} MW")
    lines.append(f"Smallest Project: {facilities_df['capacity_mw'].min():.0f} MW")
    lines.append("")

    # Breakdown by Status
    lines.append("-"*70)
    lines.append("BREAKDOWN BY STATUS")
    lines.append("-"*70)
    status_breakdown = facilities_df.groupby('status').agg({
        'project_name': 'count',
        'capacity_mw': 'sum'
    }).sort_values('capacity_mw', ascending=False)

    for status, row in status_breakdown.iterrows():
        lines.append(f"{status:25s} | {int(row['project_name']):3d} projects | {row['capacity_mw']:8,.0f} MW")
    lines.append("")

    # Breakdown by State
    lines.append("-"*70)
    lines.append("BREAKDOWN BY STATE")
    lines.append("-"*70)
    state_breakdown = facilities_df.groupby('location_state').agg({
        'project_name': 'count',
        'capacity_mw': 'sum'
    }).sort_values('capacity_mw', ascending=False)

    for state, row in state_breakdown.iterrows():
        lines.append(f"{state:25s} | {int(row['project_name']):3d} projects | {row['capacity_mw']:8,.0f} MW")
    lines.append("")

    # Breakdown by Data Source
    lines.append("-"*70)
    lines.append("BREAKDOWN BY DATA SOURCE")
    lines.append("-"*70)
    source_breakdown = facilities_df.groupby('data_source').agg({
        'project_name': 'count',
        'capacity_mw': 'sum'
    }).sort_values('capacity_mw', ascending=False)

    for source, row in source_breakdown.iterrows():
        lines.append(f"{source:25s} | {int(row['project_name']):3d} projects | {row['capacity_mw']:8,.0f} MW")
    lines.append("")

    # Top 10 Operators by MW
    lines.append("-"*70)
    lines.append("TOP 10 OPERATORS BY TOTAL MW CAPACITY")
    lines.append("-"*70)
    operator_breakdown = facilities_df.groupby('operator_company').agg({
        'project_name': 'count',
        'capacity_mw': 'sum'
    }).sort_values('capacity_mw', ascending=False).head(10)

    rank = 1
    for operator, row in operator_breakdown.iterrows():
        lines.append(f"{rank:2d}. {operator:35s} | {int(row['project_name']):2d} projects | {row['capacity_mw']:8,.0f} MW")
        rank += 1
    lines.append("")

    # Top 10 Cities by MW
    lines.append("-"*70)
    lines.append("TOP 10 CITIES BY TOTAL MW CAPACITY")
    lines.append("-"*70)
    city_breakdown = facilities_df.groupby(['location_city', 'location_state']).agg({
        'project_name': 'count',
        'capacity_mw': 'sum'
    }).sort_values('capacity_mw', ascending=False).head(10)

    rank = 1
    for (city, state), row in city_breakdown.iterrows():
        location = f"{city}, {state}"
        lines.append(f"{rank:2d}. {location:35s} | {int(row['project_name']):2d} projects | {row['capacity_mw']:8,.0f} MW")
        rank += 1
    lines.append("")

    # Data Collection Info
    lines.append("-"*70)
    lines.append("DATA COLLECTION INFORMATION")
    lines.append("-"*70)
    for idx, source in sources_df.iterrows():
        lines.append(f"Source: {source['source_name']}")
        lines.append(f"  URL: {source['source_url']}")
        lines.append(f"  Last Updated: {source['last_updated']}")
        lines.append(f"  Records Found: {source['records_found']}")
        lines.append("")

    lines.append("="*70)
    lines.append("END OF REPORT")
    lines.append("="*70)

    # Write to file
    with open('statistics_summary.txt', 'w') as f:
        f.write('\n'.join(lines))

    print(f"✓ Statistics summary saved to: statistics_summary.txt")

def main():
    """Main execution"""
    print("="*70)
    print("GENERATING OUTPUTS FROM DATA CENTER INTELLIGENCE DATABASE")
    print("="*70)
    print()

    # Load data
    print("Loading data from database...")
    facilities_df, companies_df, sources_df = load_data()
    print(f"✓ Loaded {len(facilities_df)} facilities, {len(companies_df)} companies, {len(sources_df)} sources")

    # Generate outputs
    generate_interactive_map(facilities_df)
    generate_summary_csv(facilities_df)
    generate_statistics_summary(facilities_df, companies_df, sources_df)

    print()
    print("="*70)
    print("ALL OUTPUTS GENERATED SUCCESSFULLY!")
    print("="*70)
    print("\nGenerated files:")
    print("  1. datacenter_map.html       - Interactive map visualization")
    print("  2. summary_report.csv        - Complete data export")
    print("  3. statistics_summary.txt    - Statistical analysis")
    print()

if __name__ == '__main__':
    main()

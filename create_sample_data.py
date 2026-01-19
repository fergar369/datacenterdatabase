#!/usr/bin/env python3
"""
Generate sample interconnection queue data for demonstration
Based on realistic ERCOT and PJM interconnection queue patterns
"""

import pandas as pd
from datetime import datetime, timedelta
import random

def generate_ercot_sample_data():
    """Generate realistic ERCOT sample data with data center projects"""

    projects = [
        # Data Center Projects - Various filtering criteria
        {
            'Project Name': 'Meta Austin Data Center',
            'Entity': 'Meta Platforms Inc',
            'County': 'Travis',
            'City': 'Austin',
            'Capacity (MW)': 250,
            'Status': 'Under Construction',
            'Proposed COD': '2026-06-15',
            'Queue ID': 'LRQ24-001',
            'Type': 'Large Load'
        },
        {
            'Project Name': 'AWS Houston HPC Facility',
            'Entity': 'Amazon Web Services',
            'County': 'Harris',
            'City': 'Houston',
            'Capacity (MW)': 180,
            'Status': 'Planned',
            'Proposed COD': '2026-12-01',
            'Queue ID': 'LRQ24-003',
            'Type': 'Large Load'
        },
        {
            'Project Name': 'Google Cloud Dallas',
            'Entity': 'Google LLC',
            'County': 'Dallas',
            'City': 'Dallas',
            'Capacity (MW)': 200,
            'Status': 'Operational',
            'Proposed COD': '2025-03-20',
            'Queue ID': 'LRQ23-015',
            'Type': 'Large Load'
        },
        {
            'Project Name': 'Microsoft Azure San Antonio',
            'Entity': 'Microsoft Corporation',
            'County': 'Bexar',
            'City': 'San Antonio',
            'Capacity (MW)': 150,
            'Status': 'Under Construction',
            'Proposed COD': '2026-09-01',
            'Queue ID': 'LRQ24-008',
            'Type': 'Large Load'
        },
        {
            'Project Name': 'Crypto Mining Farm Alpha',
            'Entity': 'BitMine Texas LLC',
            'County': 'Midland',
            'City': 'Midland',
            'Capacity (MW)': 100,
            'Status': 'Operational',
            'Proposed COD': '2025-01-10',
            'Queue ID': 'LRQ23-022',
            'Type': 'Large Load'
        },
        {
            'Project Name': 'EdgeConneX Fort Worth Edge Data Center',
            'Entity': 'EdgeConneX Inc',
            'County': 'Tarrant',
            'City': 'Fort Worth',
            'Capacity (MW)': 75,
            'Status': 'Planned',
            'Proposed COD': '2027-03-15',
            'Queue ID': 'LRQ24-012',
            'Type': 'Large Load'
        },
        {
            'Project Name': 'QTS Dallas Hyperscale Campus',
            'Entity': 'QTS Realty Trust',
            'County': 'Dallas',
            'City': 'Dallas',
            'Capacity (MW)': 300,
            'Status': 'Operational',
            'Proposed COD': '2024-11-01',
            'Queue ID': 'LRQ23-005',
            'Type': 'Large Load'
        },
        {
            'Project Name': 'CyrusOne Richardson Colocation',
            'Entity': 'CyrusOne Inc',
            'County': 'Dallas',
            'City': 'Richardson',
            'Capacity (MW)': 120,
            'Status': 'Under Construction',
            'Proposed COD': '2026-08-01',
            'Queue ID': 'LRQ24-006',
            'Type': 'Large Load'
        },
        {
            'Project Name': 'Switch Austin Prime',
            'Entity': 'Switch Ltd',
            'County': 'Travis',
            'City': 'Austin',
            'Capacity (MW)': 200,
            'Status': 'Planned',
            'Proposed COD': '2027-01-15',
            'Queue ID': 'LRQ24-015',
            'Type': 'Large Load'
        },
        {
            'Project Name': 'AI Training Facility - Houston',
            'Entity': 'NVIDIA Corporation',
            'County': 'Harris',
            'City': 'Houston',
            'Capacity (MW)': 220,
            'Status': 'Planned',
            'Proposed COD': '2027-06-01',
            'Queue ID': 'LRQ24-018',
            'Type': 'Large Load'
        },
        # Non-Data Center Projects (for filtering demonstration)
        {
            'Project Name': 'West Texas Solar Farm',
            'Entity': 'Renewable Energy Corp',
            'County': 'Pecos',
            'City': 'Fort Stockton',
            'Capacity (MW)': 500,
            'Status': 'Planned',
            'Proposed COD': '2026-11-01',
            'Queue ID': 'GRQ24-045',
            'Type': 'Generation - Solar'
        },
        {
            'Project Name': 'Gulf Coast Wind Project',
            'Entity': 'Wind Power LLC',
            'County': 'Cameron',
            'City': 'Brownsville',
            'Capacity (MW)': 350,
            'Status': 'Under Construction',
            'Proposed COD': '2026-05-15',
            'Queue ID': 'GRQ24-032',
            'Type': 'Generation - Wind'
        },
        {
            'Project Name': 'Chemical Plant Expansion',
            'Entity': 'Dow Chemical',
            'County': 'Brazoria',
            'City': 'Freeport',
            'Capacity (MW)': 85,
            'Status': 'Planned',
            'Proposed COD': '2026-10-01',
            'Queue ID': 'LRQ24-020',
            'Type': 'Large Load - Industrial'
        },
        {
            'Project Name': 'Natural Gas Peaker Plant',
            'Entity': 'Calpine Corp',
            'County': 'Harris',
            'City': 'Houston',
            'Capacity (MW)': 150,
            'Status': 'Planned',
            'Proposed COD': '2027-02-01',
            'Queue ID': 'GRQ24-055',
            'Type': 'Generation - Gas'
        }
    ]

    return pd.DataFrame(projects)

def generate_pjm_sample_data():
    """Generate realistic PJM sample data with data center projects"""

    projects = [
        # Data Center Projects
        {
            'Project Name': 'Digital Realty Virginia Campus',
            'Owner': 'Digital Realty Trust Inc',
            'State': 'Virginia',
            'County': 'Loudoun',
            'City': 'Ashburn',
            'MW Capacity': 400,
            'Status': 'Operational',
            'In Service Date': '2025-02-01',
            'Queue Position': '1234',
            'Interconnection Type': 'Load'
        },
        {
            'Project Name': 'Equinix DC15 Expansion',
            'Owner': 'Equinix Inc',
            'State': 'Virginia',
            'County': 'Loudoun',
            'City': 'Ashburn',
            'MW Capacity': 180,
            'Status': 'Under Construction',
            'In Service Date': '2026-04-15',
            'Queue Position': '1456',
            'Interconnection Type': 'Load'
        },
        {
            'Project Name': 'CoreSite Northern Virginia',
            'Owner': 'CoreSite Realty',
            'State': 'Virginia',
            'County': 'Fairfax',
            'City': 'Reston',
            'MW Capacity': 150,
            'Status': 'Planned',
            'In Service Date': '2026-11-01',
            'Queue Position': '1478',
            'Interconnection Type': 'Load'
        },
        {
            'Project Name': 'AWS Northern VA Region Expansion',
            'Owner': 'Amazon Web Services',
            'State': 'Virginia',
            'County': 'Loudoun',
            'City': 'Sterling',
            'MW Capacity': 350,
            'Status': 'Under Construction',
            'In Service Date': '2026-08-15',
            'Queue Position': '1467',
            'Interconnection Type': 'Load'
        },
        {
            'Project Name': 'Microsoft Azure East Coast Hub',
            'Owner': 'Microsoft Corporation',
            'State': 'Pennsylvania',
            'County': 'Chester',
            'City': 'Malvern',
            'MW Capacity': 280,
            'Status': 'Planned',
            'In Service Date': '2027-01-15',
            'Queue Position': '1501',
            'Interconnection Type': 'Load'
        },
        {
            'Project Name': 'Aligned Data Centers - Chicago',
            'Owner': 'Aligned Data Centers',
            'State': 'Illinois',
            'County': 'Cook',
            'City': 'Chicago',
            'MW Capacity': 200,
            'Status': 'Under Construction',
            'In Service Date': '2026-07-01',
            'Queue Position': '1488',
            'Interconnection Type': 'Load'
        },
        {
            'Project Name': 'Iron Mountain Data Centers - Pittsburgh',
            'Owner': 'Iron Mountain Inc',
            'State': 'Pennsylvania',
            'County': 'Allegheny',
            'City': 'Pittsburgh',
            'MW Capacity': 90,
            'Status': 'Operational',
            'In Service Date': '2025-05-20',
            'Queue Position': '1398',
            'Interconnection Type': 'Load'
        },
        {
            'Project Name': 'Meta Maryland HPC Cluster',
            'Owner': 'Meta Platforms Inc',
            'State': 'Maryland',
            'County': 'Montgomery',
            'City': 'Clarksburg',
            'MW Capacity': 320,
            'Status': 'Planned',
            'In Service Date': '2027-03-01',
            'Queue Position': '1512',
            'Interconnection Type': 'Load'
        },
        {
            'Project Name': 'Oracle Cloud Columbus',
            'Owner': 'Oracle Corporation',
            'State': 'Ohio',
            'County': 'Franklin',
            'City': 'Columbus',
            'MW Capacity': 240,
            'Status': 'Under Construction',
            'In Service Date': '2026-10-15',
            'Queue Position': '1495',
            'Interconnection Type': 'Load'
        },
        {
            'Project Name': 'Bitcoin Mining NJ',
            'Owner': 'Crypto Power Inc',
            'State': 'New Jersey',
            'County': 'Bergen',
            'City': 'Jersey City',
            'MW Capacity': 95,
            'Status': 'Proposed',
            'In Service Date': '2027-05-01',
            'Queue Position': '1523',
            'Interconnection Type': 'Load'
        },
        # Non-Data Center Projects
        {
            'Project Name': 'Offshore Wind Project',
            'Owner': 'Atlantic Wind LLC',
            'State': 'New Jersey',
            'County': 'Atlantic',
            'City': 'Atlantic City',
            'MW Capacity': 800,
            'Status': 'Planned',
            'In Service Date': '2027-06-01',
            'Queue Position': '1516',
            'Interconnection Type': 'Generation'
        },
        {
            'Project Name': 'Solar Park Maryland',
            'Owner': 'Clean Energy Corp',
            'State': 'Maryland',
            'County': 'Prince George\'s',
            'City': 'Bowie',
            'MW Capacity': 300,
            'Status': 'Under Construction',
            'In Service Date': '2026-09-15',
            'Queue Position': '1482',
            'Interconnection Type': 'Generation'
        },
        {
            'Project Name': 'Steel Mill Modernization',
            'Owner': 'US Steel',
            'State': 'Pennsylvania',
            'County': 'Allegheny',
            'City': 'Pittsburgh',
            'MW Capacity': 120,
            'Status': 'Planned',
            'In Service Date': '2026-12-01',
            'Queue Position': '1499',
            'Interconnection Type': 'Load'
        }
    ]

    return pd.DataFrame(projects)

def save_sample_data():
    """Save sample data to CSV files"""
    ercot_df = generate_ercot_sample_data()
    pjm_df = generate_pjm_sample_data()

    ercot_df.to_csv('sample_ercot_queue.csv', index=False)
    pjm_df.to_csv('sample_pjm_queue.csv', index=False)

    print(f"Generated {len(ercot_df)} ERCOT sample projects ({sum(ercot_df['Type'].str.contains('Large Load', case=False))} large loads)")
    print(f"Generated {len(pjm_df)} PJM sample projects ({sum(pjm_df['Interconnection Type'] == 'Load')} loads)")
    print("\nSample data saved to:")
    print("  - sample_ercot_queue.csv")
    print("  - sample_pjm_queue.csv")

if __name__ == '__main__':
    save_sample_data()

"""
Filtering logic for identifying data center projects
"""

import re
from typing import Tuple, Optional
import config


def normalize_text(text: str) -> str:
    """Normalize text for matching"""
    if not text:
        return ""
    return text.lower().strip()


def check_primary_keywords(text: str) -> Tuple[bool, Optional[str]]:
    """
    Check if text contains any primary data center keywords

    Returns:
        (match_found, matched_keyword)
    """
    normalized = normalize_text(text)

    for keyword in config.DATA_CENTER_KEYWORDS:
        if keyword.lower() in normalized:
            return True, keyword

    return False, None


def check_company_match(company_name: str) -> Tuple[bool, Optional[str]]:
    """
    Check if company is a known data center operator

    Returns:
        (match_found, matched_company)
    """
    normalized = normalize_text(company_name)

    for dc_company in config.DATA_CENTER_COMPANIES:
        if dc_company.lower() in normalized:
            return True, dc_company

    return False, None


def check_secondary_keywords(text: str, capacity_mw: float) -> Tuple[bool, Optional[str]]:
    """
    Check if text contains secondary keywords (requires >10 MW)

    Returns:
        (match_found, matched_keyword)
    """
    if capacity_mw <= config.SECONDARY_MW_THRESHOLD:
        return False, None

    normalized = normalize_text(text)

    for keyword in config.SECONDARY_KEYWORDS:
        if keyword.lower() in normalized:
            return True, keyword

    return False, None


def is_data_center_project(project_data: dict) -> Tuple[bool, str]:
    """
    Determine if a project is a data center using aggressive filtering

    Args:
        project_data: Dictionary containing project information
            Required keys: project_name, operator_company, notes, capacity_mw

    Returns:
        (is_match, reason)
    """

    # Extract fields
    project_name = project_data.get('project_name', '')
    operator = project_data.get('operator_company', '')
    developer = project_data.get('developer_company', '')
    notes = project_data.get('notes', '')
    capacity_mw = project_data.get('capacity_mw', 0) or 0

    # Combine all text for searching
    all_text = f"{project_name} {operator} {developer} {notes}"

    # Check 1: Primary keywords in any field
    match, keyword = check_primary_keywords(all_text)
    if match:
        return True, f"Primary keyword: '{keyword}'"

    # Check 2: Known data center company
    match, company = check_company_match(operator)
    if match:
        return True, f"Known DC operator: '{company}'"

    match, company = check_company_match(developer)
    if match:
        return True, f"Known DC developer: '{company}'"

    # Check 3: Secondary keywords + high MW
    match, keyword = check_secondary_keywords(all_text, capacity_mw)
    if match:
        return True, f"Secondary keyword (>{config.SECONDARY_MW_THRESHOLD}MW): '{keyword}'"

    return False, "No match"


def extract_capacity_mw(capacity_str: str) -> Optional[float]:
    """
    Extract MW capacity from various string formats

    Examples:
        "100 MW" -> 100.0
        "50MW" -> 50.0
        "1.5 GW" -> 1500.0
        "500 kW" -> 0.5
    """
    if not capacity_str:
        return None

    # Convert to string and normalize
    capacity_str = str(capacity_str).upper().strip()

    # Try to extract number and unit
    match = re.search(r'([\d.]+)\s*(MW|GW|KW)?', capacity_str)

    if not match:
        return None

    try:
        value = float(match.group(1))
        unit = match.group(2) if match.group(2) else 'MW'

        # Convert to MW
        if unit == 'GW':
            value *= 1000
        elif unit == 'KW':
            value /= 1000

        return value

    except (ValueError, AttributeError):
        return None


def standardize_status(status_str: str) -> str:
    """
    Standardize status strings to consistent values
    """
    if not status_str:
        return config.STATUS_PROPOSED

    normalized = normalize_text(status_str)

    if any(word in normalized for word in ['operational', 'active', 'online', 'in service']):
        return config.STATUS_OPERATIONAL
    elif any(word in normalized for word in ['construction', 'building', 'under construction']):
        return config.STATUS_CONSTRUCTION
    elif any(word in normalized for word in ['planned', 'approved', 'permitted']):
        return config.STATUS_PLANNED
    else:
        return config.STATUS_PROPOSED

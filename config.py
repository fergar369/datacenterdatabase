"""
Configuration for Data Center Intelligence Database
"""

# Aggressive filtering keywords
DATA_CENTER_KEYWORDS = [
    "data center", "datacenter", "data centre",
    "compute", "ai", "artificial intelligence",
    "machine learning", "hyperscale", "hyperscaler",
    "colocation", "colo", "server farm",
    "cloud", "digital infrastructure",
    "edge computing", "edge data",
    "crypto", "cryptocurrency", "bitcoin", "blockchain",
    "mining",  # In crypto context
    "hpc", "high performance computing"
]

# Secondary keywords (require >10 MW load)
SECONDARY_KEYWORDS = [
    "cooling", "crac", "crah", "ups",
    "uninterruptible power", "backup generation",
    "diesel generators", "n+1", "2n redundancy"
]

# Known data center companies
DATA_CENTER_COMPANIES = [
    # Hyperscalers
    "aws", "amazon", "microsoft", "azure", "google", "meta", "facebook",
    # Cloud providers
    "oracle", "ibm", "alibaba", "tencent",
    # Colo/wholesale
    "equinix", "digital realty", "cyrusone", "qts", "coresite",
    "switch", "aligned", "edgeconnex", "databank", "flexential",
    "vantage", "iron mountain", "t5", "stream data centers",
    # Other operators
    "ntt", "telx", "cologix", "internap", "rackspace",
    "savvis", "terremark", "centurylink", "lumen"
]

# Minimum MW threshold for secondary keyword matching
SECONDARY_MW_THRESHOLD = 10.0

# Data sources
ERCOT_QUEUE_URL = "https://www.ercot.com/gridinfo/generation"
PJM_QUEUE_URL = "https://www.pjm.com/planning/services-requests/interconnection-queues"

# Database configuration
DB_NAME = "datacenter_intelligence.db"

# Output files
OUTPUT_MAP = "datacenter_map.html"
OUTPUT_CSV = "summary_report.csv"
OUTPUT_STATS = "statistics_summary.txt"

# Geocoding settings
GEOCODING_TIMEOUT = 10  # seconds
GEOCODING_USER_AGENT = "datacenter_intelligence_poc"

# Status mappings
STATUS_OPERATIONAL = "Operational"
STATUS_CONSTRUCTION = "Under Construction"
STATUS_PLANNED = "Planned"
STATUS_PROPOSED = "Proposed"

# Map visualization colors
MAP_COLORS = {
    STATUS_OPERATIONAL: "green",
    STATUS_CONSTRUCTION: "yellow",
    STATUS_PLANNED: "blue",
    STATUS_PROPOSED: "gray"
}

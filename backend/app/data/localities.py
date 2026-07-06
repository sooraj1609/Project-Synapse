"""
Locality master data for Project Synapse MVP.
City: Hyderabad. 5 localities for the demo.
"""

LOCALITIES = [
    {"locality_id": "gachibowli", "name": "Gachibowli", "population": 250000, "lat": 17.4401, "lng": 78.3489},
    {"locality_id": "hitechcity", "name": "Hitech City", "population": 180000, "lat": 17.4483, "lng": 78.3915},
    {"locality_id": "kukatpally", "name": "Kukatpally", "population": 450000, "lat": 17.4849, "lng": 78.4138},
    {"locality_id": "secunderabad", "name": "Secunderabad", "population": 300000, "lat": 17.4399, "lng": 78.4983},
    {"locality_id": "lbnagar", "name": "LB Nagar", "population": 320000, "lat": 17.3456, "lng": 78.5532},
]

DOMAINS = ["mobility", "environment", "health", "citizen_services"]

# Metrics tracked per domain. Each has a "higher_is_worse" flag used by the risk engine.
DOMAIN_METRICS = {
    "mobility": [
        {"metric_name": "congestion_index", "higher_is_worse": True, "unit": "index(0-100)"},
        {"metric_name": "avg_travel_time_min", "higher_is_worse": True, "unit": "minutes"},
    ],
    "environment": [
        {"metric_name": "aqi", "higher_is_worse": True, "unit": "AQI"},
        {"metric_name": "temperature_c", "higher_is_worse": True, "unit": "celsius"},
    ],
    "health": [
        {"metric_name": "hospital_occupancy_pct", "higher_is_worse": True, "unit": "percent"},
        {"metric_name": "respiratory_cases_index", "higher_is_worse": True, "unit": "index(0-100)"},
    ],
    "citizen_services": [
        {"metric_name": "complaint_count", "higher_is_worse": True, "unit": "count/day"},
        {"metric_name": "complaint_sentiment", "higher_is_worse": False, "unit": "score(-1 to 1)"},
    ],
}

# Documented, fixed domain weights used by the risk engine (Section 13 of build prompt).
# Equal weighting for MVP transparency -- easy to defend in a demo Q&A.
DOMAIN_WEIGHTS = {
    "mobility": 0.25,
    "environment": 0.25,
    "health": 0.25,
    "citizen_services": 0.25,
}

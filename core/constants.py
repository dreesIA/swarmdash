"""Application constants and configuration"""

# Required columns for data validation
REQUIRED_COLUMNS = [
    "Player Name", "Session Type", "Total Distance", "Max Speed", "No of Sprints",
    "Sprint Distance", "Accelerations", "Decelerations", "High Speed Running"
]

# Metrics used throughout the application
METRICS = REQUIRED_COLUMNS[2:]

# Metric descriptions for UI
METRIC_DESCRIPTIONS = {
    "Total Distance": "Total distance covered in kilometers",
    "Max Speed": "Maximum speed achieved in km/h",
    "No of Sprints": "Number of high-speed runs",
    "Sprint Distance": "Total distance covered while sprinting",
    "Accelerations": "Number of rapid speed increases",
    "Decelerations": "Number of rapid speed decreases",
    "High Speed Running": "Distance covered at high speed (meters)"
}

# Performance score weights
PERFORMANCE_WEIGHTS = {
    "Total Distance": 0.2,
    "Max Speed": 0.15,
    "No of Sprints": 0.15,
    "Sprint Distance": 0.15,
    "High Speed Running": 0.15,
    "Accelerations": 0.1,
    "Decelerations": 0.1
}

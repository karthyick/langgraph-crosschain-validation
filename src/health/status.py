from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional

class HealthStatus(Enum):
    """
    Represents the health status of a component or service.
    Possible states include HEALTHY, DEGRADED, UNHEALTHY, and UNKNOWN.
    """
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

@dataclass
class HealthMetrics:
    """
    Represents detailed health metrics for a component or service.

    Attributes:
        timestamp (datetime): The UTC timestamp when the metrics were recorded.
        response_time_ms (float): The response time in milliseconds.
        error_rate (float): The error rate as a percentage (0.0 to 1.0).
        availability (float): The availability as a percentage (0.0 to 1.0).
        last_checked (datetime): The UTC timestamp when the health was last checked.
        metadata (Optional[Dict[str, Any]]): Optional dictionary for additional, custom metrics.
    """
    timestamp: datetime
    response_time_ms: float
    error_rate: float
    availability: float
    last_checked: datetime
    metadata: Optional[Dict[str, Any]] = None
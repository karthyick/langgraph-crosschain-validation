from abc import ABC, abstractmethod
from src.health.status import HealthMetrics

class BaseHealthMonitor(ABC):
    """
    Abstract Base Class for health monitors.

    Defines the interface for health monitoring components, ensuring
    that all concrete monitors implement methods to check health and
    retrieve metrics.
    """
    @abstractmethod
    def check_health(self) -> HealthMetrics:
        """
        Abstract method to be implemented by concrete health monitors.
        This method should perform health checks and return HealthMetrics.
        """
        pass

    @abstractmethod
    def get_metrics(self) -> HealthMetrics:
        """
        Abstract method to retrieve the latest health metrics.
        """
        pass

from typing import Dict, Any, TYPE_CHECKING
from datetime import datetime

from src.health.base_monitor import BaseHealthMonitor
from src.health.status import HealthStatus, HealthMetrics
from src.health.heartbeat import HeartbeatManager

if TYPE_CHECKING:
    # This is a forward declaration for type hinting a generic chain API client.
    # In a real scenario, this would be a concrete class with methods like ping() or get_status().
    class ChainApiClient:
        async def ping(self) -> bool:
            """Simulates pinging the chain and returns True for success, False for failure."""
            return True
        async def get_status(self) -> Dict[str, Any]:
            """Simulates getting status from the chain. Returns a dict."""
            # Simulate more realistic metrics for demonstration
            return {
                "status": "operational",
                "response_time_ms": 50,
                "error_rate": 0.01, # 1% error rate
                "error": None
            }


class ChainHealthMonitor(BaseHealthMonitor):
    """
    Concrete implementation of a health monitor for a specific chain.
    Combines heartbeat checking with chain-specific response validation and metrics collection.
    """

    def __init__(self, chain_id: str, heartbeat_manager: HeartbeatManager, chain_api_client: 'ChainApiClient' = None):
        self.chain_id = chain_id
        self.heartbeat_manager = heartbeat_manager
        self.chain_api_client = chain_api_client
        # Initialize with default metrics
        self._last_metrics: HealthMetrics = HealthMetrics(
            timestamp=datetime.now(),
            response_time_ms=0.0,
            error_rate=0.0,
            availability=0.0,
            last_checked=datetime.now(),
            metadata={}
        )

    async def check_health(self) -> HealthStatus:
        """
        Checks the overall health of the chain.
        Combines heartbeat status with actual chain response validation.
        """
        if not self.heartbeat_manager.is_chain_alive(self.chain_id):
            return HealthStatus.UNHEALTHY

        # If heartbeat is alive, proceed to chain-specific validation
        if self.chain_api_client:
            try:
                # Simulate a ping or status check to the chain
                chain_response = await self.chain_api_client.ping()
                if chain_response:
                    return HealthStatus.HEALTHY
                else:
                    # Chain responded but indicated an issue
                    return HealthStatus.DEGRADED
            except Exception as e:
                # Chain call failed (e.g., connection error, internal server error)
                print(f"Chain {self.chain_id} API call failed during health check: {e}")
                return HealthStatus.UNHEALTHY
        
        # If no specific chain_api_client is provided, assume healthy if heartbeat is fine
        return HealthStatus.HEALTHY

    async def get_metrics(self) -> HealthMetrics:
        """
        Collects various health metrics for the chain.
        Retrieves response time, error rate, and availability metrics from the simulated client.
        """
        self._last_metrics.is_alive = self.heartbeat_manager.is_chain_alive(self.chain_id)
        self._last_metrics.last_checked = datetime.now()

        if self.chain_api_client:
            try:
                status_data = await self.chain_api_client.get_status()
                self._last_metrics.response_time_ms = status_data.get("response_time_ms", 0)
                self._last_metrics.error_rate = status_data.get("error_rate", 0.0)
            except Exception as e:
                print(f"Failed to get metrics from chain API client for {self.chain_id}: {e}")
                self._last_metrics.response_time_ms = -1 # Indicate failure
                self._last_metrics.error_rate = 1.0     # Indicate high error rate
        else:
            # If no client, default to basic heartbeat-based availability and zero other metrics
            self._last_metrics.response_time_ms = 0
            self._last_metrics.error_rate = 0.0
        
        return self._last_metrics

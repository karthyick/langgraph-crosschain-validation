from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List

from src.health.status import HealthStatus, HealthMetrics
from src.health.heartbeat import HeartbeatManager
from src.health.chain_monitor import ChainHealthMonitor

# This will be managed by a dependency injection system in a real application
# For now, we will create instances directly or pass them as dependencies
router = APIRouter(prefix="/health", tags=["Health Monitoring"])

# In a real application, these would likely be managed globally or via a singleton pattern
# For this example, we'll create simple placeholders.
# A proper dependency injection setup would be used to provide these.
# For now, we'll assume a way to get these instances.

# Placeholder for a global heartbeat manager and chain monitors
# In a real FastAPI app, you'd use FastAPI's dependency injection system
# to manage these singletons across requests.
_heartbeat_manager: HeartbeatManager = HeartbeatManager()
_chain_monitors: Dict[str, ChainHealthMonitor] = {}

def get_heartbeat_manager() -> HeartbeatManager:
    return _heartbeat_manager

def get_chain_monitor(chain_id: str) -> ChainHealthMonitor:
    if chain_id not in _chain_monitors:
        # In a real scenario, you'd create a ChainHealthMonitor with an actual chain_api_client
        # For now, we'll create a dummy one for demonstration
        class DummyChainApiClient:
            async def ping(self) -> bool:
                return True
            async def get_status(self) -> Dict[str, Any]:
                import random
                return {
                    "status": "operational",
                    "response_time_ms": random.randint(20, 100),
                    "error_rate": round(random.uniform(0.0, 0.05), 2),
                    "error": None
                }
        
        # Register chain in heartbeat manager if not already
        if _heartbeat_manager.get_last_seen(chain_id) is None:
            _heartbeat_manager.register_chain(chain_id, ping_interval_seconds=5)

        _chain_monitors[chain_id] = ChainHealthMonitor(chain_id, _heartbeat_manager, DummyChainApiClient())
    return _chain_monitors[chain_id]

@router.get("/")
async def get_health_status() -> Dict[str, str]:
    """
    Returns the overall health status of the API.
    """
    # For now, a simple indicator. This will be expanded later with a dashboard.
    return {"status": "operational", "message": "API is healthy"}

@router.get("/chains/{chain_id}")
async def get_chain_health(chain_id: str) -> Dict[str, Any]:
    """
    Returns the health status and detailed metrics for a specific chain.
    """
    monitor = get_chain_monitor(chain_id)
    health_status = await monitor.check_health()
    metrics = await monitor.get_metrics()
    
    return {
        "chain_id": chain_id,
        "status": health_status.value,
        "metrics": metrics
    }

@router.get("/dashboard")
async def get_health_dashboard() -> Dict[str, Any]:
    """
    Returns an overview of the health status for all monitored chains.
    """
    dashboard_data: Dict[str, Any] = {
        "overall_status": HealthStatus.HEALTHY.value,
        "total_chains": len(_chain_monitors),
        "chains": {}
    }

    unhealthy_count = 0
    degraded_count = 0

    for chain_id, monitor in _chain_monitors.items():
        health_status = await monitor.check_health()
        metrics = await monitor.get_metrics()
        
        dashboard_data["chains"][chain_id] = {
            "status": health_status.value,
            "metrics": metrics
        }

        if health_status == HealthStatus.UNHEALTHY:
            unhealthy_count += 1
        elif health_status == HealthStatus.DEGRADED:
            degraded_count += 1
    
    if unhealthy_count > 0:
        dashboard_data["overall_status"] = HealthStatus.UNHEALTHY.value
    elif degraded_count > 0:
        dashboard_data["overall_status"] = HealthStatus.DEGRADED.value
    
    dashboard_data["unhealthy_chains"] = unhealthy_count
    dashboard_data["degraded_chains"] = degraded_count

    return dashboard_data




from datetime import datetime, timedelta
from typing import Dict, Optional

from src.health.status import HealthStatus, HealthMetrics # Assuming these are defined in status.py

class HeartbeatManager:
    """
    Manages heartbeat for multiple chains, tracking their last seen timestamps and ping intervals.
    """

    def __init__(self, default_ping_interval_seconds: int = 30):
        self._last_seen: Dict[str, datetime] = {}
        self._ping_intervals: Dict[str, int] = {}
        self._default_ping_interval_seconds = default_ping_interval_seconds

    def register_chain(self, chain_id: str, ping_interval_seconds: Optional[int] = None):
        """
        Registers a chain for heartbeat monitoring.

        Args:
            chain_id: The unique identifier of the chain.
            ping_interval_seconds: The expected ping interval for this chain in seconds.
                                   If None, uses the default interval.
        """
        if chain_id not in self._last_seen:
            self._last_seen[chain_id] = datetime.now()
            self._ping_intervals[chain_id] = ping_interval_seconds or self._default_ping_interval_seconds
            print(f"Chain '{chain_id}' registered with ping interval {self._ping_intervals[chain_id]} seconds.")
        else:
            print(f"Chain '{chain_id}' already registered.")

    def unregister_chain(self, chain_id: str):
        """
        Unregisters a chain from heartbeat monitoring.

        Args:
            chain_id: The unique identifier of the chain.
        """
        if chain_id in self._last_seen:
            del self._last_seen[chain_id]
            del self._ping_intervals[chain_id]
            print(f"Chain '{chain_id}' unregistered.")
        else:
            print(f"Chain '{chain_id}' not found.")

    def get_last_seen(self, chain_id: str) -> Optional[datetime]:
        """
        Returns the last seen timestamp for a given chain.

        Args:
            chain_id: The unique identifier of the chain.

        Returns:
            The datetime object of the last heartbeat, or None if the chain is not registered.
        """
        return self._last_seen.get(chain_id)

    def get_ping_interval(self, chain_id: str) -> Optional[int]:
        """
        Returns the ping interval for a given chain.

        Args:
            chain_id: The unique identifier of the chain.

        Returns:
            The ping interval in seconds, or None if the chain is not registered.
        """
        return self._ping_intervals.get(chain_id)

    def ping_chain(self, chain_id: str) -> bool:
        """
        Updates the last seen timestamp for a given chain, simulating a successful ping.

        Args:
            chain_id: The unique identifier of the chain.

        Returns:
            True if the chain is registered and its timestamp was updated, False otherwise.
        """
        if chain_id in self._last_seen:
            self._last_seen[chain_id] = datetime.now()
            print(f"Chain '{chain_id}' pinged successfully at {self._last_seen[chain_id]}.")
            return True
        print(f"Chain '{chain_id}' not registered, cannot ping.")
        return False

    def is_chain_alive(self, chain_id: str) -> bool:
        """
        Checks if a chain is considered alive based on its last seen timestamp and ping interval.

        Args:
            chain_id: The unique identifier of the chain.

        Returns:
            True if the chain is registered and its last seen timestamp is within the
            expected ping interval, False otherwise.
        """
        last_seen = self._last_seen.get(chain_id)
        ping_interval = self._ping_intervals.get(chain_id)

        if last_seen is None or ping_interval is None:
            return False  # Chain not registered or no interval set

        time_since_last_ping = datetime.now() - last_seen
        if time_since_last_ping <= timedelta(seconds=ping_interval):
            return True
        return False

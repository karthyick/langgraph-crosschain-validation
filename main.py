from fastapi import FastAPI
from src.api.health_router import router as health_router, _heartbeat_manager, get_chain_monitor
import asyncio

app = FastAPI(
    title="LangGraph Cross-Chain Health Monitoring API",
    description="API for monitoring the health and status of LangGraph cross-chain instances.",
    version="0.1.0",
)

app.include_router(health_router)

@app.on_event("startup")
async def startup_event():
    print("Application startup...")
    # Register some dummy chains for testing purposes
    # In a real app, these would be discovered or configured
    dummy_chains = ["chain_alpha", "chain_beta", "chain_gamma"]
    for chain_id in dummy_chains:
        if _heartbeat_manager.get_last_seen(chain_id) is None:
            _heartbeat_manager.register_chain(chain_id, ping_interval_seconds=5)
            # Initialize the monitor so it's ready for health checks
            _ = get_chain_monitor(chain_id)
            print(f"Registered dummy chain: {chain_id}")

    # Start a background task to periodically ping chains
    asyncio.create_task(periodic_pinger())

async def periodic_pinger():
    """Periodically pings registered chains to keep heartbeats alive."""
    while True:
        await asyncio.sleep(2)  # Ping every 2 seconds
        for chain_id in _heartbeat_manager._last_seen.keys():
            _heartbeat_manager.ping_chain(chain_id)

@app.get("/")
async def root():
    return {"message": "LangGraph Cross-Chain Health Monitoring API is running. Access /docs for API documentation."}

if __name__ == "__main__":
    import uvicorn
    # To run this: uvicorn main:app --reload --port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)

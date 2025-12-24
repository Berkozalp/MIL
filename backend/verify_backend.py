import asyncio
import websockets
import json
import sys

async def verify_backend():
    uri = "ws://localhost:8000/ws"
    print(f"Connecting to {uri}...")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to WebSocket.")
            
            # Wait for a message
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                data = json.loads(message)
                
                print(f"Received data: {data}")
                
                required_keys = ["total_in", "total_out", "currently_tracked"]
                missing_keys = [key for key in required_keys if key not in data]
                
                if missing_keys:
                    print(f"FAILED: Missing keys in response: {missing_keys}")
                    sys.exit(1)
                
                print("PASSED: Received valid stats structure.")
                print(f"Stats - In: {data.get('total_in')}, Out: {data.get('total_out')}, Tracked: {data.get('currently_tracked')}")
                sys.exit(0)
                
            except asyncio.TimeoutError:
                print("FAILED: Timed out waiting for stats message (Streamer might not be broadcasting).")
                sys.exit(1)
                
    except Exception as e:
        print(f"FAILED: Could not connect to backend: {e}")
        print("Ensure the backend is running: `uvicorn backend.main:app --port 8000`")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(verify_backend())

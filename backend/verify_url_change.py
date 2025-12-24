import requests
import sys
import time

def verify_url_update():
    url = "http://localhost:8000/stream-url"
    payload = {"url": "https://www.youtube.com/watch?v=Hu1FkdAOQIk"} # Another stream
    
    print(f"Testing POST {url}...")
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "updated":
                print("SUCCESS: URL updated via API.")
                print(f"Response: {data}")
            else:
                print(f"FAILED: Unexpected response: {data}")
                sys.exit(1)
        else:
            print(f"FAILED: Status code {response.status_code}")
            print(response.text)
            sys.exit(1)
            
    except Exception as e:
        print(f"FAILED: Could not connect to backend: {e}")
        print("Ensure the backend is running: `uvicorn backend.main:app --port 8000`")
        sys.exit(1)

if __name__ == "__main__":
    # Wait a bit just in case
    time.sleep(1)
    verify_url_update()

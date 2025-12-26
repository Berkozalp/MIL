import requests
import time

def test_switch():
    url = "http://localhost:8000/model"
    
    # Check current
    try:
        r = requests.get(url)
        print(f"Current model: {r.json()}")
    except Exception as e:
        print(f"Backend not running? {e}")
        return

    # Switch to YOLOv8
    print("\nSwitching to yolov8...")
    payload = {
        "detector_type": "yolov8",
        "settings": {
            "confidence": 0.3,
            "iou_threshold": 0.45,
            "model_size": "n"
        }
    }
    r = requests.post(url, json=payload)
    print(f"Status: {r.status_code}, Response: {r.json()}")

    # Verify
    r = requests.get(url)
    print(f"Model after switch: {r.json()}")

    # Switch back to MediaPipe
    print("\nSwitching to mediapipe...")
    payload = {
        "detector_type": "mediapipe",
        "settings": {
            "score_threshold": 0.3,
            "max_results": 10
        }
    }
    r = requests.post(url, json=payload)
    print(f"Status: {r.status_code}, Response: {r.json()}")

    # Verify
    r = requests.get(url)
    print(f"Model after switching back: {r.json()}")

if __name__ == "__main__":
    test_switch()

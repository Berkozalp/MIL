from backend.capture_frame import get_stream_url, VIDEO_URL
import cv2
import time

print(f"Testing stream extraction for: {VIDEO_URL}")
try:
    url = get_stream_url(VIDEO_URL)
    print("URL extracted successfully")
    print(f"URL: {url[:50]}...")
    
    cap = cv2.VideoCapture(url)
    if cap.isOpened():
        print("VideoCapture opened successfully")
        ret, frame = cap.read()
        if ret:
            print("Frame read successfully")
        else:
            print("Failed to read frame")
    else:
        print("Failed to open VideoCapture")
except Exception as e:
    print(f"Error: {e}")

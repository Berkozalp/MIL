import cv2
import yt_dlp
import numpy as np

VIDEO_URL = "https://www.youtube.com/watch?v=u4UZ4UvZXrg"

def get_stream_url(youtube_url):
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=False)
        return info['url']

def capture_frame():
    print("Fetching stream URL...")
    try:
        stream_url = get_stream_url(VIDEO_URL)
        print(f"Stream URL obtained based on {VIDEO_URL}")
    except Exception as e:
        print(f"Error getting stream URL: {e}")
        return

    cap = cv2.VideoCapture(stream_url)
    if not cap.isOpened():
        print("Error: Could not open video stream.")
        return

    # Skip first 180 frames (assuming 30fps -> 6 seconds)
    for _ in range(180):
        cap.grab()

    ret, frame = cap.read()
    if ret:
        cv2.imwrite("backend/reference_frame.jpg", frame)
        print("Success: protected backend/reference_frame.jpg saved.")
        
        # Also save a small version for quick preview if needed
        small_frame = cv2.resize(frame, (640, 360))
        cv2.imwrite("backend/reference_frame_small.jpg", small_frame)
    else:
        print("Error: Could not read frame.")
    
    cap.release()

if __name__ == "__main__":
    capture_frame()

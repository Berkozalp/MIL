import cv2
import asyncio
import json
import time
from fastapi.responses import StreamingResponse
from analyzer import UrbanFlowAnalyzer
from capture_frame import get_stream_url, VIDEO_URL

class Streamer:
    def __init__(self):
        # Load config first to get model settings
        config = self._load_config_file()
        
        # Initialize analyzer with configured model
        detector_type = config.get("detection_model", "mediapipe")
        detector_settings = config.get(f"{detector_type}_settings", {})
        self.analyzer = UrbanFlowAnalyzer(detector_type, detector_settings)
        
        self.active_websockets = []
        self.current_stats = {}
        
        # Singleton Capture State
        self.current_url = config.get("video_url", "https://www.youtube.com/watch?v=u4UZ4UvZXrg")
        self.cap = None
        self.running = False
        self.lock = asyncio.Lock()
        self.new_frame_event = asyncio.Event()
        self.latest_jpeg = None
        
        # Configuration
        self.skip_frames = config.get("skip_frames", 2)

    def _load_config_file(self):
        """Load configuration from file"""
        try:
            with open("roi_config.json", "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}

    def load_config(self):
        """Reload configuration"""
        config = self._load_config_file()
        self.skip_frames = config.get("skip_frames", 2)
        if "video_url" in config and config["video_url"]:
            self.current_url = config["video_url"]

    async def add_websocket(self, websocket):
        await websocket.accept()
        self.active_websockets.append(websocket)
        try:
            while True:
                await websocket.receive_text()
        except:
            if websocket in self.active_websockets:
                self.active_websockets.remove(websocket)

    async def broadcast_stats(self):
        if not self.active_websockets:
            return
            
        message = json.dumps(self.current_stats)
        to_remove = []
        for ws in self.active_websockets:
            try:
                await ws.send_text(message)
            except:
                to_remove.append(ws)
        
        for ws in to_remove:
            self.active_websockets.remove(ws)

    def start_stream(self):
        if self.running:
            return
        self.running = True
        # Run the blocking capture loop in a separate thread
        import threading
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()
        print("Streamer background thread started.")

    def update_stream_url(self, new_url):
        print(f"Updating stream URL to: {new_url}")
        self.current_url = new_url
        self.running = False # Stop current loop
        if hasattr(self, 'capture_thread'):
            self.capture_thread.join(timeout=2.0)
        
        self.start_stream() # Restart with new URL
        
        # Save to config
        try:
            with open("roi_config.json", "r") as f:
                data = json.load(f)
            data["video_url"] = new_url
            with open("roi_config.json", "w") as f:
                json.dump(data, f, indent=4)
        except:
            pass

    def seek(self, seconds):
        """Seek video by specified seconds (positive or negative)"""
        if self.cap and self.cap.isOpened():
            try:
                # Get current position in milliseconds
                current_pos = self.cap.get(cv2.CAP_PROP_POS_MSEC)
                # Calculate new position
                new_pos = max(0, current_pos + (seconds * 1000))
                # Set new position
                self.cap.set(cv2.CAP_PROP_POS_MSEC, new_pos)
                print(f"Seeked {seconds}s to position {new_pos}ms")
            except Exception as e:
                print(f"Seek error: {e}")


    def _capture_loop(self):
        print(f"Starting capture loop for {self.current_url}")
        
        # 1. Get Stream URL (Blocking network call)
        try:
            real_url = get_stream_url(self.current_url)
            self.cap = cv2.VideoCapture(real_url)
        except Exception as e:
            print(f"Error fetching stream: {e}")
            self.running = False
            return

        frame_count = 0
        
        while self.running and self.cap.isOpened():
            success, frame = self.cap.read()
            if not success:
                print("Frame read failed, attempting reconnect...")
                self.cap.release()
                time.sleep(1)
                try:
                    self.cap = cv2.VideoCapture(get_stream_url(self.current_url))
                except:
                    pass
                continue

            frame_count += 1
            
            # --- Frame Skipping Logic ---
            if frame_count % (self.skip_frames + 1) != 0:
                # Still update the jpeg for fluid video, but SKIP processing?
                # Actually, if we skip processing, we should verify if we want to show the RAW frame or the last processed frame.
                # Use raw frame for smoothness usually, but overlays might lag.
                # Let's process every Nth frame, and for others just overlay the LAST known stats/boxes?
                # For now: SIMPLEST implementation: Just skip the loop entirely (video FPS drops).
                # User asked for "Optimization (Skip frames)" separately.
                # Better approach for smooth video + low CPU:
                # 1. Always encode/broadcast the frame for video.
                # 2. Only run `analyzer.process_frame` every N frames.
                
                # Check previous frame stats to re-draw? 
                # Analyzer handles state, but drawing happens IN process_frame.
                # Modifying analyzer to separate drawing is risky right now.
                # FALLBACK: Just continue (skip this frame entirely).
                continue
            
            # --- Processing ---
            annotated_frame, state = self.analyzer.process_frame(frame)
            
            # Update Stats
            self.current_stats = {
                "total_in": state.total_in,
                "total_out": state.total_out,
                "currently_tracked": state.currently_tracked
            }
            
            # Encode
            ret, buffer = cv2.imencode('.jpg', annotated_frame)
            if ret:
                self.latest_jpeg = buffer.tobytes()
                # Notify async consumers
                # In a thread, we can't await asyncio.Event directly for the main loop?
                # Actually, generate_frames is async generator? No, it's usually sync generator in FastAPI.
                # Standard pattern: usage of sleep or Event.
                pass
        
        self.cap.release()
        print("Capture loop ended.")

    async def frame_generator(self):
        while True:
            if self.latest_jpeg:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + self.latest_jpeg + b'\r\n')
                await asyncio.sleep(1.0 / 20) # Limit broadcast FPS to ~20 to save bandwidth
            else:
                await asyncio.sleep(0.1)

# Global Instance
streamer_instance = Streamer()

def get_video_stream():
    return StreamingResponse(streamer_instance.frame_generator(), media_type="multipart/x-mixed-replace; boundary=frame")

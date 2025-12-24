# Motion Image Learner

Real-time object detection and tracking system with multi-model support (MediaPipe & YOLOv8).

## Quick Start

### Option 1: Using the Launcher Script (Recommended)

Simply run:
```bash
python start.py
```

This will:
- ✓ Check all dependencies
- ✓ Start backend server (http://0.0.0.0:8000)
- ✓ Start frontend server (http://localhost:5173)
- ✓ Open browser automatically

Press `Ctrl+C` to stop all servers.

### Option 2: Manual Start

**Backend:**
```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
cmd /c npm run dev
```

## Features

- 🔄 **Multi-Model Detection**: Switch between MediaPipe and YOLOv8
- 📊 **Real-time Tracking**: Advanced object tracking with motion compensation
- ⚙️ **Configurable Settings**: Adjust detection parameters on-the-fly
- 💡 **Helpful Tooltips**: Turkish explanations for all settings
- ⏱️ **Video Controls**: ±15s seek buttons
- 📈 **Live Statistics**: Monitor active entities, entries, and exits

## Model Options

### MediaPipe (EfficientDet Lite)
- Fast and lightweight
- Good for real-time applications
- Settings: Score Threshold, Max Results

### YOLOv8 (Ultralytics)
- More accurate detection
- Multiple model sizes (n/s/m/l/x)
- Settings: Confidence, IoU Threshold, Model Size

## Requirements

- Python 3.8+
- Node.js 16+
- Dependencies listed in `backend/requirements.txt`

## Installation

```bash
# Install Python dependencies
pip install -r backend/requirements.txt

# Install Ultralytics for YOLOv8 support
pip install ultralytics

# Install frontend dependencies
cd frontend
npm install
```

## Configuration

Edit `backend/roi_config.json` to configure:
- Detection model (mediapipe/yolov8)
- Model-specific settings
- ROI (Region of Interest)
- Video stream URL
- Frame skip settings

## Usage

1. Start the application using `python start.py`
2. Open http://localhost:5173 in your browser
3. Click "Settings" tab to:
   - Select detection model
   - Adjust parameters
   - Change video stream
4. Use tooltips (ⓘ icons) for help
5. Monitor real-time statistics in "Monitor" tab

## Project Structure

```
MIL/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── analyzer.py          # Detection & tracking logic
│   ├── detector_base.py     # Detector abstraction
│   ├── detector_mediapipe.py
│   ├── detector_yolov8.py
│   ├── streamer.py          # Video streaming
│   └── roi_config.json      # Configuration
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   └── components/
│   │       ├── DashboardOverlay.jsx
│   │       ├── VideoControls.jsx
│   │       └── ...
│   └── package.json
└── start.py                 # Quick launcher script
```

## License

MIT

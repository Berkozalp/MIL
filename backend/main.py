from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from streamer import get_video_stream, streamer_instance
import asyncio

app = FastAPI(title="Motion Image Learner", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    # Start the singleton streamer background thread
    streamer_instance.start_stream()
    # Start stats broadcaster
    asyncio.create_task(stats_broadcaster())

async def stats_broadcaster():
    while True:
        await streamer_instance.broadcast_stats()
        await asyncio.sleep(0.1) # 10 FPS stats update

@app.get("/")
def read_root():
    return {"message": "Motion Image Learner Backend is Running"}

@app.get("/video_feed")
def video_feed():
    return get_video_stream()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await streamer_instance.add_websocket(websocket)

from calibration import load_calibration, save_calibration, CalibrationSettings
from pydantic import BaseModel

class StreamSettings(BaseModel):
    url: str

@app.post("/stream-url")
def update_stream_url(settings: StreamSettings):
    streamer_instance.update_stream_url(settings.url)
    return {"status": "updated", "url": settings.url}

@app.get("/calibration")
def get_calibration():
    return load_calibration()

@app.post("/calibration")
def update_calibration(settings: CalibrationSettings):
    save_calibration(settings)
    return {"status": "saved", "settings": settings}

class SeekSettings(BaseModel):
    seconds: int

@app.post("/seek")
def seek_video(settings: SeekSettings):
    streamer_instance.seek(settings.seconds)
    return {"status": "seeked", "seconds": settings.seconds}

class ModelSettings(BaseModel):
    detector_type: str
    settings: dict = {}

@app.get("/model")
def get_model():
    return {
        "detector_type": streamer_instance.analyzer.detector_type,
        "settings": streamer_instance.analyzer.detector.get_settings()
    }

@app.post("/model")
def update_model(model_settings: ModelSettings):
    streamer_instance.analyzer.set_detector(
        model_settings.detector_type,
        model_settings.settings
    )
    
    # Save to config
    try:
        import json
        with open("roi_config.json", "r") as f:
            data = json.load(f)
        data["detection_model"] = model_settings.detector_type
        data[f"{model_settings.detector_type}_settings"] = model_settings.settings
        with open("roi_config.json", "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving model config: {e}")
    
    return {
        "status": "updated",
        "detector_type": model_settings.detector_type,
        "settings": model_settings.settings
    }



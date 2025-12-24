from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from streamer import get_video_stream, streamer_instance
import asyncio

app = FastAPI(title="Urban Flow AI", version="0.1.0")

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
    return {"message": "Urban Flow AI Backend is Running"}

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

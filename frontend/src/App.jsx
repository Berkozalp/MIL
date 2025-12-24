import React, { useEffect, useState } from 'react';
import DashboardOverlay from './components/DashboardOverlay';
import MaskOverlay from './components/MaskOverlay';
import PerspectiveOverlay from './components/PerspectiveOverlay';
import './App.css';

function App() {
  const [stats, setStats] = useState({ total_in: 0, total_out: 0, currently_tracked: 0 });
  const [isConnected, setIsConnected] = useState(false);
  const [mode, setMode] = useState('LIVE'); // 'LIVE', 'MASK', 'CALIB'

  // Centralized Tracker Settings State
  const [trackerSettings, setTrackerSettings] = useState({
    maxDistance: 100,
    maxDisappeared: 50,
    scoreThreshold: 0.4,
    streamUrl: 'https://www.youtube.com/watch?v=u4UZ4UvZXrg'
  });

  const updateStreamUrl = async (url) => {
    try {
      await fetch('http://localhost:8000/stream-url', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url }),
      });
      console.log('Stream URL updated');
      // Force reload video element
      const img = document.querySelector('img[alt="Live Feed"]');
      if (img) img.src = "http://localhost:8000/video_feed?t=" + Date.now();
    } catch (e) { console.error(e); }
  };

  const updateBackendSettings = async () => {
    try {
      await fetch('http://localhost:8000/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(trackerSettings),
      });
      console.log('Settings updated');
    } catch (e) { console.error(e); }
  };

  const handleSaveMask = async (points) => {
    try {
      await fetch('http://localhost:8000/roi', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ points }),
      });
      setMode('LIVE');
    } catch (e) { console.error(e); }
  };

  const handleSaveCalibration = async (points) => {
    try {
      await fetch('http://localhost:8000/calibration', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ points }),
      });
      console.log('Calibration saved');
      setMode('LIVE');
    } catch (e) { console.error(e); }
  };

  // WebSocket Connection
  useEffect(() => {
    const connectWs = () => {
      const ws = new WebSocket('ws://localhost:8000/ws');
      ws.onopen = () => setIsConnected(true);
      ws.onmessage = (e) => {
        try { setStats(JSON.parse(e.data)); } catch (err) { }
      };
      ws.onclose = () => {
        setIsConnected(false);
        setTimeout(connectWs, 3000);
      };
      return ws;
    };
    const ws = connectWs();
    return () => ws.close();
  }, []);

  return (
    <div className="app-container">
      {/* 1. Full Screen Video Feed (Background) */}
      <div className="video-background">
        <img
          src="http://localhost:8000/video_feed"
          alt="Live Feed"
          className="video-feed"
          onError={(e) => {
            setTimeout(() => {
              e.target.src = "http://localhost:8000/video_feed?t=" + Date.now();
            }, 5000);
          }}
        />
      </div>

      {/* 2. Aesthetic Gradient Overlay */}
      <div className="gradient-overlay" />

      {/* 3. Overlays based on Mode */}
      {mode === 'MASK' && (
        <MaskOverlay isActive={true} onSave={handleSaveMask} />
      )}

      {mode === 'CALIB' && (
        <PerspectiveOverlay isActive={true} onSave={handleSaveCalibration} />
      )}

      {/* 4. Live Dashboard (Unified Top-Right Panel) */}
      {mode === 'LIVE' && (
        <DashboardOverlay
          stats={stats}
          settings={trackerSettings}
          onSettingsChange={setTrackerSettings}
          onUpdateStream={updateStreamUrl}
          onUpdateBackend={updateBackendSettings}
        />
      )}

      {/* 5. Main Control UI (Top Left Title & Mode Switchers) */}
      <div className="header-container">
        <div>
          <h1 className="app-title">
            URBAN<span>FLOW</span> AI
          </h1>
          <div className="app-subtitle">Real-time Analytics</div>
        </div>

        <div className="controls-row">
          <button
            onClick={() => setMode(mode === 'MASK' ? 'LIVE' : 'MASK')}
            className={`btn-mode ${mode === 'MASK' ? 'active-mask' : ''}`}
          >
            <span>{mode === 'MASK' ? 'SAVE & EXIT' : 'ROI MASK'}</span>
          </button>

          <button
            onClick={() => setMode(mode === 'CALIB' ? 'LIVE' : 'CALIB')}
            className={`btn-mode ${mode === 'CALIB' ? 'active-calib' : ''}`}
          >
            <span>{mode === 'CALIB' ? 'SAVE & EXIT' : 'CALIBRATE'}</span>
          </button>
        </div>
      </div>

      {/* 6. Status Indicator (Bottom Left) */}
      <div className="status-indicator">
        <div className={`status-dot ${isConnected ? 'online' : 'offline'}`} />
        <span className="status-text">
          {isConnected ? 'System Online' : 'Connecting...'}
        </span>
      </div>
    </div>
  );
}

export default App;

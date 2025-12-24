import React, { useEffect, useState } from 'react';
import DashboardOverlay from './components/DashboardOverlay';
import MaskOverlay from './components/MaskOverlay';
import PerspectiveOverlay from './components/PerspectiveOverlay';

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
    <div className="relative w-screen h-screen bg-black overflow-hidden font-sans select-none">
      {/* 1. Full Screen Video Feed (Background) */}
      <div className="absolute inset-0 z-0">
        <img
          src="http://localhost:8000/video_feed"
          alt="Live Feed"
          className="w-full h-full object-cover"
          onError={(e) => {
            setTimeout(() => {
              e.target.src = "http://localhost:8000/video_feed?t=" + Date.now();
            }, 5000);
          }}
        />
      </div>

      {/* 2. Aesthetic Gradient Overlay */}
      <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-transparent to-black/40 pointer-events-none z-10" />

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
      <div className="absolute top-8 left-8 z-50 flex flex-col gap-6">
        <div>
          <h1 className="text-4xl font-black italic text-white tracking-tighter drop-shadow-2xl">
            URBAN<span className="text-cyan-400">FLOW</span> AI
          </h1>
          <div className="text-[10px] font-mono text-cyan-200/60 uppercase tracking-[0.4em] ml-1">Real-time Analytics</div>
        </div>

        <div className="flex gap-3">
          <button
            onClick={() => setMode(mode === 'MASK' ? 'LIVE' : 'MASK')}
            className={`px-5 py-2.5 rounded-xl font-bold text-xs tracking-wider transition-all border backdrop-blur-md flex items-center gap-2 ${mode === 'MASK'
              ? 'bg-emerald-500 text-black border-emerald-400 shadow-[0_0_20px_rgba(16,185,129,0.4)]'
              : 'bg-white/5 text-white border-white/10 hover:bg-white/10 hover:border-white/20'}`}
          >
            <span>{mode === 'MASK' ? 'SAVE & EXIT' : 'ROI MASK'}</span>
          </button>

          <button
            onClick={() => setMode(mode === 'CALIB' ? 'LIVE' : 'CALIB')}
            className={`px-5 py-2.5 rounded-xl font-bold text-xs tracking-wider transition-all border backdrop-blur-md flex items-center gap-2 ${mode === 'CALIB'
              ? 'bg-cyan-500 text-black border-cyan-400 shadow-[0_0_20px_rgba(6,182,212,0.4)]'
              : 'bg-white/5 text-white border-white/10 hover:bg-white/10 hover:border-white/20'}`}
          >
            <span>{mode === 'CALIB' ? 'SAVE & EXIT' : 'CALIBRATE'}</span>
          </button>
        </div>
      </div>

      {/* 6. Status Indicator (Bottom Left) */}
      <div className="absolute bottom-8 left-8 z-50 flex items-center gap-3 bg-black/40 backdrop-blur-md px-4 py-2 rounded-full border border-white/5">
        <div className={`w-2 h-2 rounded-full shadow-[0_0_10px_currentColor] ${isConnected ? 'bg-emerald-500 text-emerald-500 animate-pulse' : 'bg-rose-500 text-rose-500'}`} />
        <span className="text-[10px] font-mono font-bold text-white/80 tracking-widest uppercase">
          {isConnected ? 'System Online' : 'Connecting...'}
        </span>
      </div>
    </div>
  );
}

export default App;

import React from 'react';
import './VideoControls.css';

function VideoControls({ onSeekBackward, onSeekForward }) {
    return (
        <div className="video-controls">
            <button
                className="seek-button seek-backward"
                onClick={onSeekBackward}
                title="Seek backward 15 seconds"
            >
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M12 2a10 10 0 1 0 10 10" />
                    <polyline points="12 6 12 12 16 14" />
                    <path d="M2 12h4" />
                </svg>
                <span>-15s</span>
            </button>

            <button
                className="seek-button seek-forward"
                onClick={onSeekForward}
                title="Seek forward 15 seconds"
            >
                <span>+15s</span>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M12 2a10 10 0 0 1 10 10" />
                    <polyline points="12 6 12 12 16 14" />
                    <path d="M18 12h4" />
                </svg>
            </button>
        </div>
    );
}

export default VideoControls;

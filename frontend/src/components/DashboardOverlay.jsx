import React, { useState } from 'react';

export default function DashboardOverlay({ stats, settings, onSettingsChange, onUpdateStream, onUpdateBackend }) {
    const [isOpen, setIsOpen] = useState(true);
    const [activeTab, setActiveTab] = useState('monitor'); // 'monitor' or 'settings'

    if (!stats || !settings) return null;

    const handleChange = (key, value) => {
        onSettingsChange({ ...settings, [key]: value });
    };

    return (
        <div style={{ position: 'fixed', top: '1.5rem', right: '1.5rem', zIndex: 50, display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
            {/* Toggle Button (visible when closed) */}
            {!isOpen && (
                <button
                    onClick={() => setIsOpen(true)}
                    className="dashboard-toggle-btn"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16m-7 6h7" />
                    </svg>
                </button>
            )}

            {/* Main Panel */}
            <div className={`dashboard-panel ${!isOpen ? 'closed' : ''}`}>

                {/* Header */}
                <div className="dashboard-header">
                    <div className="dashboard-tabs">
                        <button
                            onClick={() => setActiveTab('monitor')}
                            className={`tab-btn ${activeTab === 'monitor' ? 'active-monitor' : ''}`}
                        >
                            Monitor
                        </button>
                        <button
                            onClick={() => setActiveTab('settings')}
                            className={`tab-btn ${activeTab === 'settings' ? 'active-settings' : ''}`}
                        >
                            Settings
                        </button>
                    </div>
                    <button onClick={() => setIsOpen(false)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#9ca3af' }}>
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                            <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                        </svg>
                    </button>
                </div>

                {/* Content */}
                <div className="dashboard-content">
                    {activeTab === 'monitor' ? (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                            <div className="stat-main">
                                {/* Simple blur effect via inline style if needed, or CSS */}
                                <div style={{ position: 'relative', zIndex: 1 }}>
                                    <div className="stat-value-lg">{stats.currently_tracked || 0}</div>
                                    <div className="stat-label-lg">Active Entities</div>
                                </div>
                            </div>

                            <div className="stats-grid">
                                <div className="stat-card-sm stat-card-in">
                                    <div className="stat-value-sm">{stats.total_in || 0}</div>
                                    <div className="stat-label-sm">Entered</div>
                                </div>
                                <div className="stat-card-sm stat-card-out">
                                    <div className="stat-value-sm">{stats.total_out || 0}</div>
                                    <div className="stat-label-sm">Exited</div>
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                                <div className="settings-group">
                                    <label className="settings-label tooltip-trigger">
                                        Max Distance (px)
                                        <span className="tooltip-content">
                                            Bir nesnenin yeni bir algılama ile eşleştirilmesi için gereken maksimum piksel mesafesi.
                                        </span>
                                    </label>
                                    <div className="range-group">
                                        <input
                                            type="range" min="10" max="300" step="1"
                                            value={settings.maxDistance}
                                            onChange={(e) => handleChange('maxDistance', Number(e.target.value))}
                                            className="range-input"
                                        />
                                        <span className="range-value">{settings.maxDistance}</span>
                                    </div>
                                </div>

                                <div className="settings-group">
                                    <label className="settings-label tooltip-trigger">
                                        Max Disappeared
                                        <span className="tooltip-content">
                                            Nesne algılanmadığında kaç kare boyunca takip edilmeye devam edileceği.
                                        </span>
                                    </label>
                                    <div className="range-group">
                                        <input
                                            type="range" min="1" max="200" step="1"
                                            value={settings.maxDisappeared}
                                            onChange={(e) => handleChange('maxDisappeared', Number(e.target.value))}
                                            className="range-input"
                                        />
                                        <span className="range-value">{settings.maxDisappeared}</span>
                                    </div>
                                </div>

                                <div className="settings-group">
                                    <label className="settings-label tooltip-trigger">
                                        Score Threshold
                                        <span className="tooltip-content">
                                            Bir algılamanın geçerli sayılması için gereken minimum güven skoru (0-1 arası).
                                        </span>
                                    </label>
                                    <div className="range-group">
                                        <input
                                            type="range" min="0.1" max="1.0" step="0.05"
                                            value={settings.scoreThreshold}
                                            onChange={(e) => handleChange('scoreThreshold', Number(e.target.value))}
                                            className="range-input"
                                        />
                                        <span className="range-value">{settings.scoreThreshold}</span>
                                    </div>
                                </div>
                            </div>

                            <button
                                onClick={onUpdateBackend}
                                className="btn-update"
                            >
                                Update Algorithm
                            </button>

                            <div style={{ paddingTop: '1rem', borderTop: '1px solid rgba(255, 255, 255, 0.1)', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                                <label className="settings-label">Stream URL</label>
                                <input
                                    type="text"
                                    value={settings.streamUrl}
                                    onChange={(e) => handleChange('streamUrl', e.target.value)}
                                    className="input-text"
                                    placeholder="Enter YouTube URL..."
                                />
                                <button
                                    onClick={() => onUpdateStream(settings.streamUrl)}
                                    className="btn-update"
                                    style={{ backgroundColor: 'transparent', border: '1px solid rgba(255,255,255,0.1)' }}
                                    onMouseOver={(e) => e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.1)'}
                                    onMouseOut={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                                >
                                    Change Stream
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

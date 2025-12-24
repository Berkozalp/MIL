import React, { useState, useEffect } from 'react';
import './DashboardOverlay.css';

const Tooltip = ({ text, children }) => {
    return (
        <div className="tooltip-wrapper">
            {children}
            <div className="tooltip-box">
                <span className="tooltip-icon">ⓘ</span>
                <div className="tooltip-text">{text}</div>
            </div>
        </div>
    );
};

export default function DashboardOverlay({ stats, settings, onSettingsChange, onUpdateStream, onUpdateBackend }) {
    const [isOpen, setIsOpen] = useState(true);
    const [activeTab, setActiveTab] = useState('monitor');
    const [modelType, setModelType] = useState('mediapipe');
    const [modelSettings, setModelSettings] = useState({
        mediapipe: {
            score_threshold: 0.25,
            max_results: 20
        },
        yolov8: {
            confidence: 0.25,
            iou_threshold: 0.45,
            model_size: 'n'
        }
    });

    // Load current model on mount
    useEffect(() => {
        fetch('http://localhost:8000/model')
            .then(res => res.json())
            .then(data => {
                setModelType(data.detector_type);
                setModelSettings(prev => ({
                    ...prev,
                    [data.detector_type]: data.settings
                }));
            })
            .catch(console.error);
    }, []);

    if (!stats || !settings) return null;

    const handleChange = (key, value) => {
        onSettingsChange({ ...settings, [key]: value });
    };

    const handleModelChange = (newModel) => {
        setModelType(newModel);
    };

    const handleModelSettingChange = (key, value) => {
        setModelSettings(prev => ({
            ...prev,
            [modelType]: {
                ...prev[modelType],
                [key]: value
            }
        }));
    };

    const applyModelSettings = async () => {
        try {
            await fetch('http://localhost:8000/model', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    detector_type: modelType,
                    settings: modelSettings[modelType]
                })
            });
            console.log('Model settings applied');
        } catch (e) {
            console.error('Error applying model settings:', e);
        }
    };

    const currentModelSettings = modelSettings[modelType];

    return (
        <div style={{ position: 'fixed', top: '1.5rem', right: '1.5rem', zIndex: 50, display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
            {!isOpen && (
                <button onClick={() => setIsOpen(true)} className="dashboard-toggle-btn">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16m-7 6h7" />
                    </svg>
                </button>
            )}

            <div className={`dashboard-panel ${!isOpen ? 'closed' : ''}`}>
                <div className="dashboard-header">
                    <div className="dashboard-tabs">
                        <button onClick={() => setActiveTab('monitor')} className={`tab-btn ${activeTab === 'monitor' ? 'active-monitor' : ''}`}>
                            Monitor
                        </button>
                        <button onClick={() => setActiveTab('settings')} className={`tab-btn ${activeTab === 'settings' ? 'active-settings' : ''}`}>
                            Settings
                        </button>
                    </div>
                    <button onClick={() => setIsOpen(false)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#9ca3af' }}>
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                            <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                        </svg>
                    </button>
                </div>

                <div className="dashboard-content">
                    {activeTab === 'monitor' ? (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                            <div className="stat-main">
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
                            {/* Model Selection */}
                            <div className="settings-group">
                                <Tooltip text="Nesne algılama için kullanılacak model: MediaPipe (hızlı) veya YOLOv8 (daha doğru)">
                                    <label className="settings-label">Detection Model</label>
                                </Tooltip>
                                <select
                                    value={modelType}
                                    onChange={(e) => handleModelChange(e.target.value)}
                                    className="model-select"
                                >
                                    <option value="mediapipe">MediaPipe (EfficientDet)</option>
                                    <option value="yolov8">YOLOv8</option>
                                </select>
                            </div>

                            {/* Model-Specific Settings */}
                            {modelType === 'mediapipe' ? (
                                <>
                                    <div className="settings-group">
                                        <Tooltip text="Bir algılamanın geçerli sayılması için gereken minimum güven skoru (0-1 arası). Düşük değer daha fazla tespit, yüksek değer daha az yanlış tespit.">
                                            <label className="settings-label">Score Threshold</label>
                                        </Tooltip>
                                        <div className="range-group">
                                            <input
                                                type="range" min="0.1" max="1.0" step="0.05"
                                                value={currentModelSettings.score_threshold}
                                                onChange={(e) => handleModelSettingChange('score_threshold', Number(e.target.value))}
                                                className="range-input"
                                            />
                                            <span className="range-value">{currentModelSettings.score_threshold.toFixed(2)}</span>
                                        </div>
                                    </div>

                                    <div className="settings-group">
                                        <Tooltip text="Her karede algılanacak maksimum nesne sayısı. Yüksek değer daha fazla CPU kullanır.">
                                            <label className="settings-label">Max Results</label>
                                        </Tooltip>
                                        <div className="range-group">
                                            <input
                                                type="range" min="5" max="50" step="1"
                                                value={currentModelSettings.max_results}
                                                onChange={(e) => handleModelSettingChange('max_results', Number(e.target.value))}
                                                className="range-input"
                                            />
                                            <span className="range-value">{currentModelSettings.max_results}</span>
                                        </div>
                                    </div>
                                </>
                            ) : (
                                <>
                                    <div className="settings-group">
                                        <Tooltip text="YOLOv8 için minimum güven skoru. Düşük değer daha fazla tespit, yüksek değer daha az yanlış tespit.">
                                            <label className="settings-label">Confidence</label>
                                        </Tooltip>
                                        <div className="range-group">
                                            <input
                                                type="range" min="0.1" max="1.0" step="0.05"
                                                value={currentModelSettings.confidence}
                                                onChange={(e) => handleModelSettingChange('confidence', Number(e.target.value))}
                                                className="range-input"
                                            />
                                            <span className="range-value">{currentModelSettings.confidence.toFixed(2)}</span>
                                        </div>
                                    </div>

                                    <div className="settings-group">
                                        <Tooltip text="Çakışan algılamaları birleştirmek için IoU eşiği. Düşük değer daha az birleştirme, yüksek değer daha fazla birleştirme.">
                                            <label className="settings-label">IoU Threshold</label>
                                        </Tooltip>
                                        <div className="range-group">
                                            <input
                                                type="range" min="0.1" max="0.9" step="0.05"
                                                value={currentModelSettings.iou_threshold}
                                                onChange={(e) => handleModelSettingChange('iou_threshold', Number(e.target.value))}
                                                className="range-input"
                                            />
                                            <span className="range-value">{currentModelSettings.iou_threshold.toFixed(2)}</span>
                                        </div>
                                    </div>

                                    <div className="settings-group">
                                        <Tooltip text="YOLOv8 model boyutu: n (nano, en hızlı), s (small), m (medium), l (large), x (xlarge, en doğru)">
                                            <label className="settings-label">Model Size</label>
                                        </Tooltip>
                                        <select
                                            value={currentModelSettings.model_size}
                                            onChange={(e) => handleModelSettingChange('model_size', e.target.value)}
                                            className="model-select"
                                        >
                                            <option value="n">Nano (fastest)</option>
                                            <option value="s">Small</option>
                                            <option value="m">Medium</option>
                                            <option value="l">Large</option>
                                            <option value="x">XLarge (most accurate)</option>
                                        </select>
                                    </div>
                                </>
                            )}

                            <button onClick={applyModelSettings} className="btn-update">
                                Apply Model Settings
                            </button>

                            {/* Tracker Settings */}
                            <div style={{ paddingTop: '1rem', borderTop: '1px solid rgba(255, 255, 255, 0.1)' }}>
                                <div className="settings-group">
                                    <Tooltip text="Bir nesnenin yeni bir algılama ile eşleştirilmesi için gereken maksimum piksel mesafesi.">
                                        <label className="settings-label">Max Distance (px)</label>
                                    </Tooltip>
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
                                    <Tooltip text="Nesne algılanmadığında kaç kare boyunca takip edilmeye devam edileceği.">
                                        <label className="settings-label">Max Disappeared</label>
                                    </Tooltip>
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

                                <button onClick={onUpdateBackend} className="btn-update">
                                    Update Tracker
                                </button>
                            </div>

                            {/* Stream URL */}
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

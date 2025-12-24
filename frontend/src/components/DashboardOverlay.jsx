import React, { useState } from 'react';

export default function DashboardOverlay({ stats, settings, onSettingsChange, onUpdateStream, onUpdateBackend }) {
    const [isOpen, setIsOpen] = useState(true);
    const [activeTab, setActiveTab] = useState('monitor'); // 'monitor' or 'settings'

    if (!stats || !settings) return null;

    const handleChange = (key, value) => {
        onSettingsChange({ ...settings, [key]: value });
    };

    return (
        <div className="fixed top-6 right-6 z-50 flex flex-col items-end">
            {/* Toggle Button (visible when closed) */}
            {!isOpen && (
                <button
                    onClick={() => setIsOpen(true)}
                    className="bg-black/80 backdrop-blur-md text-white p-3 rounded-xl border border-white/10 shadow-2xl hover:bg-white/10 transition-all"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16m-7 6h7" />
                    </svg>
                </button>
            )}

            {/* Main Panel */}
            <div className={`bg-black/90 backdrop-blur-xl text-white rounded-2xl shadow-2xl transition-all duration-300 overflow-hidden border border-white/10 w-80 ${isOpen ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0 pointer-events-none absolute'}`}>

                {/* Header */}
                <div className="flex justify-between items-center p-4 border-b border-white/10 bg-white/5">
                    <div className="flex gap-4">
                        <button
                            onClick={() => setActiveTab('monitor')}
                            className={`text-xs font-bold uppercase tracking-wider pb-1 border-b-2 transition-colors ${activeTab === 'monitor' ? 'border-cyan-400 text-white' : 'border-transparent text-gray-400 hover:text-white'}`}
                        >
                            Monitor
                        </button>
                        <button
                            onClick={() => setActiveTab('settings')}
                            className={`text-xs font-bold uppercase tracking-wider pb-1 border-b-2 transition-colors ${activeTab === 'settings' ? 'border-purple-400 text-white' : 'border-transparent text-gray-400 hover:text-white'}`}
                        >
                            Settings
                        </button>
                    </div>
                    <button onClick={() => setIsOpen(false)} className="text-gray-400 hover:text-white transition-colors">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                            <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                        </svg>
                    </button>
                </div>

                {/* Content */}
                <div className="p-5">
                    {activeTab === 'monitor' ? (
                        <div className="space-y-4">
                            <div className="text-center p-6 bg-gradient-to-br from-cyan-500/10 to-blue-500/10 rounded-2xl border border-cyan-500/20 shadow-inner relative overflow-hidden group">
                                <div className="absolute inset-0 bg-cyan-400/5 blur-xl group-hover:bg-cyan-400/10 transition-all duration-700"></div>
                                <div className="relative">
                                    <div className="text-6xl font-black text-cyan-400 drop-shadow-[0_0_15px_rgba(34,211,238,0.5)] font-mono tracking-tighter">{stats.currently_tracked || 0}</div>
                                    <div className="text-[10px] text-cyan-200/70 uppercase tracking-[0.3em] font-bold mt-2">Active Entities</div>
                                </div>
                            </div>

                            <div className="grid grid-cols-2 gap-3">
                                <div className="bg-emerald-500/10 p-4 rounded-xl border border-emerald-500/20 text-center relative overflow-hidden">
                                    <div className="text-2xl font-black text-emerald-400 font-mono">{stats.total_in || 0}</div>
                                    <div className="text-[9px] text-emerald-200/60 uppercase font-bold tracking-wider mt-1">Entered</div>
                                </div>
                                <div className="bg-rose-500/10 p-4 rounded-xl border border-rose-500/20 text-center relative overflow-hidden">
                                    <div className="text-2xl font-black text-rose-400 font-mono">{stats.total_out || 0}</div>
                                    <div className="text-[9px] text-rose-200/60 uppercase font-bold tracking-wider mt-1">Exited</div>
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div className="space-y-4">
                            <div className="space-y-3">
                                <div className="space-y-1">
                                    <label className="text-[10px] uppercase font-bold text-gray-400 tracking-wider">Max Distance (px)</label>
                                    <div className="flex items-center gap-3">
                                        <input
                                            type="range" min="10" max="300" step="1"
                                            value={settings.maxDistance}
                                            onChange={(e) => handleChange('maxDistance', Number(e.target.value))}
                                            className="flex-1 h-1 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-purple-500"
                                        />
                                        <span className="text-xs font-mono text-purple-400 w-8 text-right">{settings.maxDistance}</span>
                                    </div>
                                </div>

                                <div className="space-y-1">
                                    <label className="text-[10px] uppercase font-bold text-gray-400 tracking-wider">Max Disappeared</label>
                                    <div className="flex items-center gap-3">
                                        <input
                                            type="range" min="1" max="200" step="1"
                                            value={settings.maxDisappeared}
                                            onChange={(e) => handleChange('maxDisappeared', Number(e.target.value))}
                                            className="flex-1 h-1 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-purple-500"
                                        />
                                        <span className="text-xs font-mono text-purple-400 w-8 text-right">{settings.maxDisappeared}</span>
                                    </div>
                                </div>

                                <div className="space-y-1">
                                    <label className="text-[10px] uppercase font-bold text-gray-400 tracking-wider">Score Threshold</label>
                                    <div className="flex items-center gap-3">
                                        <input
                                            type="range" min="0.1" max="1.0" step="0.05"
                                            value={settings.scoreThreshold}
                                            onChange={(e) => handleChange('scoreThreshold', Number(e.target.value))}
                                            className="flex-1 h-1 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-purple-500"
                                        />
                                        <span className="text-xs font-mono text-purple-400 w-8 text-right">{settings.scoreThreshold}</span>
                                    </div>
                                </div>
                            </div>

                            <button
                                onClick={onUpdateBackend}
                                className="w-full py-2 bg-purple-600 hover:bg-purple-500 text-white text-xs font-bold uppercase tracking-wider rounded-lg transition-colors shadow-lg shadow-purple-900/20"
                            >
                                Update Algorithm
                            </button>

                            <div className="pt-4 border-t border-white/10 space-y-2">
                                <label className="text-[10px] uppercase font-bold text-gray-400 tracking-wider">Stream URL</label>
                                <input
                                    type="text"
                                    value={settings.streamUrl}
                                    onChange={(e) => handleChange('streamUrl', e.target.value)}
                                    className="w-full bg-black/50 border border-white/10 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-purple-500 transition-colors"
                                    placeholder="Enter YouTube URL..."
                                />
                                <button
                                    onClick={() => onUpdateStream(settings.streamUrl)}
                                    className="w-full py-2 bg-white/5 hover:bg-white/10 border border-white/10 text-white text-xs font-bold uppercase tracking-wider rounded-lg transition-colors"
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

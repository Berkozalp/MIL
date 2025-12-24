import React, { useState, useEffect } from 'react';

const MaskOverlay = ({ isActive, onSave, savedMask = [] }) => {
    const [points, setPoints] = useState(savedMask);
    const [isClosed, setIsClosed] = useState(false);

    useEffect(() => {
        if (savedMask.length > 2) {
            setIsClosed(true);
        }
    }, [savedMask]);

    if (!isActive) return null;

    const handleCanvasClick = (e) => {
        if (isClosed) return;

        const rect = e.currentTarget.getBoundingClientRect();
        const x = ((e.clientX - rect.left) / rect.width) * 100;
        const y = ((e.clientY - rect.top) / rect.height) * 100;

        // Check if clicking near the first point to close
        if (points.length > 2) {
            const firstPoint = points[0];
            const dist = Math.sqrt(Math.pow(x - firstPoint.x, 2) + Math.pow(y - firstPoint.y, 2));
            if (dist < 2) {
                setIsClosed(true);
                return;
            }
        }

        setPoints([...points, { x, y }]);
    };

    const handlePointRightClick = (index, e) => {
        e.preventDefault();
        const newPoints = points.filter((_, i) => i !== index);
        setPoints(newPoints);
        if (newPoints.length < 3) setIsClosed(false);
    };

    const clearMask = () => {
        setPoints([]);
        setIsClosed(false);
    };

    return (
        <div className="absolute inset-0 z-30 pointer-events-auto cursor-crosshair" onClick={handleCanvasClick}>
            <svg className="w-full h-full">
                {/* Polygon Mask */}
                {points.length > 0 && (
                    <polygon
                        points={points.map(p => `${p.x}%,${p.y}%`).join(' ')}
                        fill="rgba(0, 255, 0, 0.2)"
                        stroke="#00ff00"
                        strokeWidth="2"
                    />
                )}

                {/* Lines following cursor (while drawing) */}
                {!isClosed && points.length > 0 && (
                    <polyline
                        points={points.map(p => `${p.x}%,${p.y}%`).join(' ')}
                        fill="none"
                        stroke="#00ff00"
                        strokeWidth="1"
                        strokeDasharray="4"
                    />
                )}

                {/* Points */}
                {points.map((p, i) => (
                    <circle
                        key={i}
                        cx={`${p.x}%`}
                        cy={`${p.y}%`}
                        r="6"
                        fill={i === 0 ? "#ff0000" : "#00ff00"}
                        className="hover:scale-150 transition-transform cursor-pointer"
                        onContextMenu={(e) => handlePointRightClick(i, e)}
                    />
                ))}
            </svg>

            {/* Controls */}
            <div className="absolute top-4 left-1/2 -translate-x-1/2 flex gap-4 z-50">
                <button
                    onClick={(e) => { e.stopPropagation(); clearMask(); }}
                    className="bg-black/60 backdrop-blur-md text-white px-8 py-3 rounded-xl border border-white/10 hover:bg-white/10 transition-all font-bold tracking-widest uppercase text-xs shadow-xl"
                >
                    Clear All
                </button>
                <button
                    onClick={(e) => { e.stopPropagation(); onSave(points); }}
                    className="bg-green-500/80 backdrop-blur-md text-black px-10 py-3 rounded-xl font-black hover:bg-green-400 transition-all shadow-[0_0_30px_rgba(34,197,94,0.3)] tracking-widest uppercase text-xs"
                >
                    Save Mask
                </button>
            </div>

            {/* Hint */}
            <div className="absolute bottom-10 left-10 bg-black/80 backdrop-blur-xl p-6 rounded-2xl border border-white/10 text-white/90 font-mono text-xs pointer-events-none shadow-2xl max-w-xs transition-opacity duration-500">
                <p className="font-bold text-green-400 mb-3 tracking-tighter text-sm">MASKING WORKFLOW</p>
                <ul className="space-y-2 opacity-80">
                    <li>• <span className="text-white font-bold">CLICK</span> to plot path points</li>
                    <li>• <span className="text-red-400 font-bold">CLICK RED POINT</span> to close loop</li>
                    <li>• <span className="text-white font-bold">RIGHT-CLICK</span> points to delete</li>
                    <li>• Analysis only active <span className="text-green-400 italic">INSIDE</span> zone</li>
                </ul>
            </div>
        </div>
    );
};

export default MaskOverlay;

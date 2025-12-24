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
        <div className="mask-overlay-container" onClick={handleCanvasClick}>
            <svg className="width-full height-full" style={{ width: '100%', height: '100%' }}>
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
                        style={{ cursor: 'pointer', transition: 'transform 0.2s' }}
                        onMouseEnter={(e) => e.target.style.transform = 'scale(1.5)'}
                        onMouseLeave={(e) => e.target.style.transform = 'scale(1)'}
                        onContextMenu={(e) => handlePointRightClick(i, e)}
                    />
                ))}
            </svg>

            {/* Controls */}
            <div className="mask-controls">
                <button
                    onClick={(e) => { e.stopPropagation(); clearMask(); }}
                    className="btn-clear"
                >
                    Clear All
                </button>
                <button
                    onClick={(e) => { e.stopPropagation(); onSave(points); }}
                    className="btn-save-mask"
                >
                    Save Mask
                </button>
            </div>

            {/* Hint */}
            <div className="mask-hint">
                <p className="mask-hint-title">MASKING WORKFLOW</p>
                <ul className="mask-hint-list">
                    <li>• <span style={{ color: 'white', fontWeight: 'bold' }}>CLICK</span> to plot path points</li>
                    <li>• <span style={{ color: '#f87171', fontWeight: 'bold' }}>CLICK RED POINT</span> to close loop</li>
                    <li>• <span style={{ color: 'white', fontWeight: 'bold' }}>RIGHT-CLICK</span> points to delete</li>
                    <li>• Analysis only active <span style={{ color: '#4ade80', fontStyle: 'italic' }}>INSIDE</span> zone</li>
                </ul>
            </div>
        </div>
    );
};

export default MaskOverlay;

import React, { useState, useEffect, useRef } from 'react';

const PerspectiveOverlay = ({ isActive, onSave, savedPoints }) => {
    // Default to a central rectangle if no points saved
    const defaultPoints = [
        { x: 20, y: 20 }, // Top Left
        { x: 80, y: 20 }, // Top Right
        { x: 80, y: 80 }, // Bottom Right
        { x: 20, y: 80 }  // Bottom Left
    ];

    const [points, setPoints] = useState(savedPoints || defaultPoints);
    const [draggingIdx, setDraggingIdx] = useState(null);
    const containerRef = useRef(null);

    useEffect(() => {
        if (savedPoints && savedPoints.length === 4) {
            setPoints(savedPoints);
        }
    }, [savedPoints]);

    if (!isActive) return null;

    const handleMouseDown = (index, e) => {
        e.stopPropagation();
        setDraggingIdx(index);
    };

    const handleMouseMove = (e) => {
        if (draggingIdx === null || !containerRef.current) return;

        const rect = containerRef.current.getBoundingClientRect();
        const x = ((e.clientX - rect.left) / rect.width) * 100;
        const y = ((e.clientY - rect.top) / rect.height) * 100;

        // Constraint to 0-100%
        const clampedX = Math.max(0, Math.min(100, x));
        const clampedY = Math.max(0, Math.min(100, y));

        setPoints(prev => {
            const newPoints = [...prev];
            newPoints[draggingIdx] = { x: clampedX, y: clampedY };
            return newPoints;
        });
    };

    const handleMouseUp = () => {
        setDraggingIdx(null);
    };

    return (
        <div
            ref={containerRef}
            className="absolute inset-0 z-40"
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseUp}
        >
            <svg className="w-full h-full absolute inset-0 pointer-events-none">
                {/* Polygon connecting the 4 points */}
                <polygon
                    points={points.map(p => `${p.x}%,${p.y}%`).join(' ')}
                    fill="rgba(0, 255, 255, 0.1)"
                    stroke="#00ffff"
                    strokeWidth="2"
                    strokeDasharray="5,5"
                />

                {/* Connecting lines for visual clarity */}
                <line x1={`${points[0].x}%`} y1={`${points[0].y}%`} x2={`${points[1].x}%`} y2={`${points[1].y}%`} stroke="#00ffff" strokeWidth="2" />
                <line x1={`${points[1].x}%`} y1={`${points[1].y}%`} x2={`${points[2].x}%`} y2={`${points[2].y}%`} stroke="#00ffff" strokeWidth="2" />
                <line x1={`${points[2].x}%`} y1={`${points[2].y}%`} x2={`${points[3].x}%`} y2={`${points[3].y}%`} stroke="#00ffff" strokeWidth="2" />
                <line x1={`${points[3].x}%`} y1={`${points[3].y}%`} x2={`${points[0].x}%`} y2={`${points[0].y}%`} stroke="#00ffff" strokeWidth="2" />
            </svg>

            {/* Draggable Corner Points */}
            {points.map((p, i) => (
                <div
                    key={i}
                    className="absolute w-6 h-6 -ml-3 -mt-3 rounded-full bg-cyan-500 border-2 border-white cursor-pointer hover:scale-125 transition-transform shadow-[0_0_15px_rgba(6,182,212,0.5)] flex items-center justify-center font-bold text-xs text-black"
                    style={{ left: `${p.x}%`, top: `${p.y}%`, pointerEvents: 'auto' }}
                    onMouseDown={(e) => handleMouseDown(i, e)}
                >
                    {i + 1}
                </div>
            ))}

            {/* Instruction / Save Panel */}
            <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex gap-4 pointer-events-auto">
                <div className="bg-black/80 backdrop-blur text-cyan-400 px-6 py-3 rounded-xl border border-cyan-500/30 flex items-center gap-4">
                    <span className="font-mono text-sm font-bold">🎯 DRAG CORNERS TO MATCH ROAD PERSPECTIVE</span>
                    <button
                        onClick={() => onSave(points)}
                        className="bg-cyan-500 text-black px-6 py-2 rounded-lg font-bold hover:bg-cyan-400 transition-colors shadow-lg"
                    >
                        SAVE CALIBRATION
                    </button>
                    <button
                        onClick={() => setPoints(defaultPoints)}
                        className="text-white/60 hover:text-white text-xs underline"
                    >
                        Reset
                    </button>
                </div>
            </div>
        </div>
    );
};

export default PerspectiveOverlay;

import React, { useState, useRef, useEffect } from 'react';

const CalibrationOverlay = () => {
    // Default corner positions (percentage of screen)
    const defaultCorners = {
        topLeft: { x: 15, y: 15 },
        topRight: { x: 85, y: 15 },
        bottomLeft: { x: 15, y: 85 },
        bottomRight: { x: 85, y: 85 }
    };

    const [corners, setCorners] = useState(() => {
        const saved = localStorage.getItem('calibrationCorners');
        return saved ? JSON.parse(saved) : defaultCorners;
    });

    const [draggingCorner, setDraggingCorner] = useState(null);
    const [draggingGrid, setDraggingGrid] = useState(false);
    const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
    const containerRef = useRef(null);

    // Grid settings
    const [gridSize, setGridSize] = useState(() => {
        const saved = localStorage.getItem('calibrationGridSize');
        return saved ? parseInt(saved) : 20;
    });
    const [gridColor, setGridColor] = useState(() => {
        const saved = localStorage.getItem('calibrationGridColor');
        return saved || '#00ff00';
    });
    const [gridOpacity, setGridOpacity] = useState(() => {
        const saved = localStorage.getItem('calibrationGridOpacity');
        return saved ? parseFloat(saved) : 0.7;
    });
    const [showCorners, setShowCorners] = useState(true);
    const [showSettings, setShowSettings] = useState(false);

    // Save to localStorage
    useEffect(() => {
        localStorage.setItem('calibrationCorners', JSON.stringify(corners));
    }, [corners]);

    useEffect(() => {
        localStorage.setItem('calibrationGridSize', gridSize.toString());
    }, [gridSize]);

    useEffect(() => {
        localStorage.setItem('calibrationGridColor', gridColor);
    }, [gridColor]);

    useEffect(() => {
        localStorage.setItem('calibrationGridOpacity', gridOpacity.toString());
    }, [gridOpacity]);

    // Mouse handlers
    const handleMouseMove = (e) => {
        if (!containerRef.current) return;

        const rect = containerRef.current.getBoundingClientRect();
        const x = ((e.clientX - rect.left) / rect.width) * 100;
        const y = ((e.clientY - rect.top) / rect.height) * 100;

        if (draggingCorner) {
            setCorners(prev => ({
                ...prev,
                [draggingCorner]: { x: Math.max(0, Math.min(100, x)), y: Math.max(0, Math.min(100, y)) }
            }));
        } else if (draggingGrid) {
            const dx = x - dragOffset.x;
            const dy = y - dragOffset.y;

            setCorners(prev => ({
                topLeft: { x: prev.topLeft.x + dx, y: prev.topLeft.y + dy },
                topRight: { x: prev.topRight.x + dx, y: prev.topRight.y + dy },
                bottomLeft: { x: prev.bottomLeft.x + dx, y: prev.bottomLeft.y + dy },
                bottomRight: { x: prev.bottomRight.x + dx, y: prev.bottomRight.y + dy }
            }));

            setDragOffset({ x, y });
        }
    };

    const handleMouseUp = () => {
        setDraggingCorner(null);
        setDraggingGrid(false);
    };

    const handleCornerMouseDown = (corner, e) => {
        e.stopPropagation();
        setDraggingCorner(corner);
    };

    const handleGridMouseDown = (e) => {
        if (!containerRef.current) return;
        const rect = containerRef.current.getBoundingClientRect();
        const x = ((e.clientX - rect.left) / rect.width) * 100;
        const y = ((e.clientY - rect.top) / rect.height) * 100;

        setDragOffset({ x, y });
        setDraggingGrid(true);
    };

    const resetGrid = () => {
        setCorners(defaultCorners);
    };

    // Generate grid lines with perspective
    const generateGridLines = () => {
        const lines = [];
        const numLines = gridSize;

        // Vertical lines
        for (let i = 0; i <= numLines; i++) {
            const t = i / numLines;
            const topX = corners.topLeft.x + (corners.topRight.x - corners.topLeft.x) * t;
            const topY = corners.topLeft.y + (corners.topRight.y - corners.topLeft.y) * t;
            const bottomX = corners.bottomLeft.x + (corners.bottomRight.x - corners.bottomLeft.x) * t;
            const bottomY = corners.bottomLeft.y + (corners.bottomRight.y - corners.bottomLeft.y) * t;

            lines.push(
                <line
                    key={`v-${i}`}
                    x1={`${topX}%`}
                    y1={`${topY}%`}
                    x2={`${bottomX}%`}
                    y2={`${bottomY}%`}
                    stroke={gridColor}
                    strokeWidth="2"
                    opacity={gridOpacity}
                />
            );
        }

        // Horizontal lines
        for (let i = 0; i <= numLines; i++) {
            const t = i / numLines;
            const leftX = corners.topLeft.x + (corners.bottomLeft.x - corners.topLeft.x) * t;
            const leftY = corners.topLeft.y + (corners.bottomLeft.y - corners.topLeft.y) * t;
            const rightX = corners.topRight.x + (corners.bottomRight.x - corners.topRight.x) * t;
            const rightY = corners.topRight.y + (corners.bottomRight.y - corners.topRight.y) * t;

            lines.push(
                <line
                    key={`h-${i}`}
                    x1={`${leftX}%`}
                    y1={`${leftY}%`}
                    x2={`${rightX}%`}
                    y2={`${rightY}%`}
                    stroke={gridColor}
                    strokeWidth="2"
                    opacity={gridOpacity}
                />
            );
        }

        return lines;
    };

    return (
        <div
            ref={containerRef}
            style={{ position: 'absolute', inset: 0, zIndex: 100 }}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseUp}
        >
            {/* SVG Grid */}
            <svg
                style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', cursor: 'move', pointerEvents: 'auto' }}
                onMouseDown={handleGridMouseDown}
            >
                {generateGridLines()}
            </svg>

            {/* Corner Handles */}
            {showCorners && Object.entries(corners).map(([key, pos]) => (
                <div
                    key={key}
                    style={{
                        position: 'absolute',
                        cursor: 'grab',
                        left: `${pos.x}%`,
                        top: `${pos.y}%`,
                        transform: 'translate(-50%, -50%)',
                        zIndex: 200,
                        pointerEvents: 'auto',
                        transition: 'transform 0.1s'
                    }}
                    onMouseDown={(e) => handleCornerMouseDown(key, e)}
                    onMouseEnter={(e) => e.currentTarget.style.transform = 'translate(-50%, -50%) scale(1.25)'}
                    onMouseLeave={(e) => e.currentTarget.style.transform = 'translate(-50%, -50%) scale(1)'}
                >
                    <div
                        style={{
                            borderRadius: '50%',
                            border: '2px solid #ffffff',
                            backgroundColor: draggingCorner === key ? '#ff0000' : gridColor,
                            boxShadow: '0 0 10px rgba(0,0,0,0.8)',
                            width: draggingCorner === key ? '24px' : '18px',
                            height: draggingCorner === key ? '24px' : '18px',
                            transition: 'all 0.1s'
                        }}
                    />
                    <div
                        style={{
                            position: 'absolute',
                            top: '1.5rem',
                            left: '50%',
                            transform: 'translateX(-50%)',
                            fontSize: '0.75rem',
                            fontFamily: 'monospace',
                            padding: '0.25rem 0.5rem',
                            borderRadius: '0.25rem',
                            whiteSpace: 'nowrap',
                            backgroundColor: 'rgba(0,0,0,0.8)',
                            color: gridColor,
                        }}
                    >
                        {key.replace(/([A-Z])/g, ' $1').trim()}
                    </div>
                </div>
            ))}

            {/* Control Panel */}
            <div className="grid-controls-panel">
                <button
                    onClick={() => setShowSettings(!showSettings)}
                    className="btn-grid-settings"
                    style={{
                        backgroundColor: 'rgba(0,0,0,0.8)',
                        color: gridColor
                    }}
                >
                    ⚙️ Settings
                </button>

                {showSettings && (
                    <div
                        className="grid-settings-popup"
                        style={{
                            backgroundColor: 'rgba(0,0,0,0.9)',
                            color: '#ffffff',
                            pointerEvents: 'auto'
                        }}
                    >
                        <div>
                            <label style={{ display: 'block', fontSize: '0.75rem', marginBottom: '0.25rem' }}>Grid Size: {gridSize}</label>
                            <input
                                type="range"
                                min="5"
                                max="50"
                                value={gridSize}
                                onChange={(e) => setGridSize(parseInt(e.target.value))}
                                style={{ width: '100%' }}
                            />
                        </div>
                        <div>
                            <label style={{ display: 'block', fontSize: '0.75rem', marginBottom: '0.25rem' }}>Opacity: {gridOpacity.toFixed(1)}</label>
                            <input
                                type="range"
                                min="0"
                                max="1"
                                step="0.1"
                                value={gridOpacity}
                                onChange={(e) => setGridOpacity(parseFloat(e.target.value))}
                                style={{ width: '100%' }}
                            />
                        </div>
                        <div>
                            <label style={{ display: 'block', fontSize: '0.75rem', marginBottom: '0.25rem' }}>Color</label>
                            <input
                                type="color"
                                value={gridColor}
                                onChange={(e) => setGridColor(e.target.value)}
                                style={{ width: '100%', height: '2rem', borderRadius: '0.25rem', cursor: 'pointer' }}
                            />
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <input
                                type="checkbox"
                                checked={showCorners}
                                onChange={(e) => setShowCorners(e.target.checked)}
                                id="showCorners"
                            />
                            <label htmlFor="showCorners" style={{ fontSize: '0.75rem' }}>Show Corners</label>
                        </div>
                    </div>
                )}

                <button
                    onClick={resetGrid}
                    className="btn-grid-settings"
                    style={{
                        backgroundColor: 'rgba(255,0,0,0.8)',
                        color: 'white'
                    }}
                >
                    Reset Grid
                </button>
            </div>

            {/* Instructions */}
            <div
                style={{
                    position: 'absolute',
                    bottom: '1rem',
                    left: '1rem',
                    padding: '0.75rem 1rem',
                    borderRadius: '0.5rem',
                    fontFamily: 'monospace',
                    fontSize: '0.875rem',
                    backgroundColor: 'rgba(0,0,0,0.8)',
                    color: gridColor,
                    zIndex: 300,
                    pointerEvents: 'none',
                    maxWidth: '300px'
                }}
            >
                <div style={{ fontWeight: 'bold', marginBottom: '0.5rem' }}>Calibration Controls:</div>
                <div>• Drag corners to warp perspective</div>
                <div>• Drag grid to move position</div>
                <div>• Use settings to adjust appearance</div>
            </div>
        </div>
    );
};

export default CalibrationOverlay;

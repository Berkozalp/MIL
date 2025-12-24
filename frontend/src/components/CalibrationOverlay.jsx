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
            className="absolute inset-0"
            style={{ zIndex: 100 }}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseUp}
        >
            {/* SVG Grid */}
            <svg
                className="absolute inset-0 w-full h-full cursor-move"
                onMouseDown={handleGridMouseDown}
                style={{ pointerEvents: 'auto' }}
            >
                {generateGridLines()}
            </svg>

            {/* Corner Handles */}
            {showCorners && Object.entries(corners).map(([key, pos]) => (
                <div
                    key={key}
                    className="absolute cursor-grab active:cursor-grabbing transition-transform hover:scale-125"
                    style={{
                        left: `${pos.x}%`,
                        top: `${pos.y}%`,
                        transform: 'translate(-50%, -50%)',
                        zIndex: 200,
                        pointerEvents: 'auto'
                    }}
                    onMouseDown={(e) => handleCornerMouseDown(key, e)}
                >
                    <div
                        className="rounded-full border-2 transition-all"
                        style={{
                            backgroundColor: draggingCorner === key ? '#ff0000' : gridColor,
                            borderColor: '#ffffff',
                            boxShadow: '0 0 10px rgba(0,0,0,0.8)',
                            width: draggingCorner === key ? '24px' : '18px',
                            height: draggingCorner === key ? '24px' : '18px'
                        }}
                    />
                    <div
                        className="absolute top-6 left-1/2 transform -translate-x-1/2 text-xs font-mono px-2 py-1 rounded whitespace-nowrap"
                        style={{
                            backgroundColor: 'rgba(0,0,0,0.8)',
                            color: gridColor,
                        }}
                    >
                        {key.replace(/([A-Z])/g, ' $1').trim()}
                    </div>
                </div>
            ))}

            {/* Control Panel */}
            <div className="absolute top-4 right-4 flex flex-col gap-2" style={{ zIndex: 300 }}>
                <button
                    onClick={() => setShowSettings(!showSettings)}
                    className="px-4 py-2 rounded-lg font-semibold transition-all hover:scale-105 backdrop-blur"
                    style={{
                        backgroundColor: 'rgba(0,0,0,0.8)',
                        color: gridColor,
                        pointerEvents: 'auto'
                    }}
                >
                    ⚙️ Settings
                </button>

                {showSettings && (
                    <div
                        className="px-4 py-3 rounded-lg font-mono text-sm space-y-3"
                        style={{
                            backgroundColor: 'rgba(0,0,0,0.9)',
                            color: '#ffffff',
                            pointerEvents: 'auto',
                            minWidth: '200px'
                        }}
                    >
                        <div>
                            <label className="block text-xs mb-1">Grid Size: {gridSize}</label>
                            <input
                                type="range"
                                min="5"
                                max="50"
                                value={gridSize}
                                onChange={(e) => setGridSize(parseInt(e.target.value))}
                                className="w-full"
                            />
                        </div>
                        <div>
                            <label className="block text-xs mb-1">Opacity: {gridOpacity.toFixed(1)}</label>
                            <input
                                type="range"
                                min="0"
                                max="1"
                                step="0.1"
                                value={gridOpacity}
                                onChange={(e) => setGridOpacity(parseFloat(e.target.value))}
                                className="w-full"
                            />
                        </div>
                        <div>
                            <label className="block text-xs mb-1">Color</label>
                            <input
                                type="color"
                                value={gridColor}
                                onChange={(e) => setGridColor(e.target.value)}
                                className="w-full h-8 rounded cursor-pointer"
                            />
                        </div>
                        <div className="flex items-center gap-2">
                            <input
                                type="checkbox"
                                checked={showCorners}
                                onChange={(e) => setShowCorners(e.target.checked)}
                                id="showCorners"
                            />
                            <label htmlFor="showCorners" className="text-xs">Show Corners</label>
                        </div>
                    </div>
                )}

                <button
                    onClick={resetGrid}
                    className="px-4 py-2 rounded-lg font-semibold transition-all hover:scale-105"
                    style={{
                        backgroundColor: 'rgba(255,0,0,0.8)',
                        color: 'white',
                        pointerEvents: 'auto'
                    }}
                >
                    Reset Grid
                </button>
            </div>

            {/* Instructions */}
            <div
                className="absolute bottom-4 left-4 px-4 py-3 rounded-lg font-mono text-sm"
                style={{
                    backgroundColor: 'rgba(0,0,0,0.8)',
                    color: gridColor,
                    zIndex: 300,
                    pointerEvents: 'none',
                    maxWidth: '300px'
                }}
            >
                <div className="font-bold mb-2">Calibration Controls:</div>
                <div>• Drag corners to warp perspective</div>
                <div>• Drag grid to move position</div>
                <div>• Use settings to adjust appearance</div>
            </div>
        </div>
    );
};

export default CalibrationOverlay;

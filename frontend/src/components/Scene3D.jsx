import React, { useState, useRef, useEffect } from 'react';
import { useControls } from 'leva';

const Scene3D = ({ isActive }) => {
    if (!isActive) return null;

    // Default corner positions (percentage of screen)
    const defaultCorners = {
        topLeft: { x: 20, y: 20 },
        topRight: { x: 80, y: 20 },
        bottomLeft: { x: 20, y: 80 },
        bottomRight: { x: 80, y: 80 }
    };

    const [corners, setCorners] = useState(() => {
        const saved = localStorage.getItem('gridCorners');
        return saved ? JSON.parse(saved) : defaultCorners;
    });

    const [draggingCorner, setDraggingCorner] = useState(null);
    const [draggingGrid, setDraggingGrid] = useState(false);
    const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
    const containerRef = useRef(null);

    // Grid settings
    const { gridSize, gridColor, gridOpacity, showCorners } = useControls('Grid Settings', {
        gridSize: { value: 20, min: 5, max: 50, step: 1, label: 'Grid Size' },
        gridColor: { value: '#00ff00', label: 'Grid Color' },
        gridOpacity: { value: 0.6, min: 0, max: 1, step: 0.1, label: 'Opacity' },
        showCorners: { value: true, label: 'Show Corners' }
    });

    // Save corners to localStorage
    useEffect(() => {
        localStorage.setItem('gridCorners', JSON.stringify(corners));
    }, [corners]);

    // Mouse move handler
    const handleMouseMove = (e) => {
        if (!containerRef.current) return;

        const rect = containerRef.current.getBoundingClientRect();
        const x = ((e.clientX - rect.left) / rect.width) * 100;
        const y = ((e.clientY - rect.top) / rect.height) * 100;

        if (draggingCorner) {
            setCorners(prev => ({
                ...prev,
                [draggingCorner]: { x, y }
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

    // Generate grid lines
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
                    strokeWidth="1"
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
                    strokeWidth="1"
                    opacity={gridOpacity}
                />
            );
        }

        return lines;
    };

    return (
        <div
            ref={containerRef}
            className="absolute inset-0 pointer-events-auto"
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
                        className="w-4 h-4 rounded-full border-2 transition-all"
                        style={{
                            backgroundColor: draggingCorner === key ? '#ff0000' : gridColor,
                            borderColor: '#ffffff',
                            boxShadow: '0 0 10px rgba(0,0,0,0.5)',
                            width: draggingCorner === key ? '20px' : '16px',
                            height: draggingCorner === key ? '20px' : '16px'
                        }}
                    />
                    <div
                        className="absolute top-6 left-1/2 transform -translate-x-1/2 text-xs font-mono px-2 py-1 rounded"
                        style={{
                            backgroundColor: 'rgba(0,0,0,0.7)',
                            color: gridColor,
                            whiteSpace: 'nowrap'
                        }}
                    >
                        {key.replace(/([A-Z])/g, ' $1').trim()}
                    </div>
                </div>
            ))}

            {/* Reset Button */}
            <button
                onClick={resetGrid}
                className="absolute top-4 right-4 px-4 py-2 rounded-lg font-semibold transition-all hover:scale-105"
                style={{
                    backgroundColor: 'rgba(255,0,0,0.8)',
                    color: 'white',
                    zIndex: 300,
                    pointerEvents: 'auto'
                }}
            >
                Reset Grid
            </button>

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
                <div>• Use panel to adjust settings</div>
            </div>
        </div>
    );
};

export default Scene3D;

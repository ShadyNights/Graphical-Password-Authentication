import React, { useRef, useState, useCallback } from 'react';
import { Point } from '../services/api';


function CanvasBackground({ category }: { category: string }) {
    const patterns: Record<string, React.ReactNode> = {
        mountain: (
            <svg viewBox="0 0 800 450" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#1a1a4e" />
                        <stop offset="100%" stopColor="#3d1f6d" />
                    </linearGradient>
                    <linearGradient id="mt" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#667eea" />
                        <stop offset="100%" stopColor="#2d1b69" />
                    </linearGradient>
                </defs>
                <rect width="800" height="450" fill="url(#sky)" />
                <circle cx="650" cy="80" r="40" fill="#ffeaa7" opacity="0.8" />
                <polygon points="50,450 200,150 350,450" fill="url(#mt)" opacity="0.8" />
                <polygon points="200,450 380,100 560,450" fill="#5a3d8a" opacity="0.9" />
                <polygon points="400,450 550,180 700,450" fill="url(#mt)" opacity="0.7" />
                <polygon points="550,450 680,200 800,450" fill="#4a2d7a" opacity="0.8" />
                {[...Array(50)].map((_, i) => (
                    <circle key={i} cx={(i * 137.5 + 50) % 800} cy={(i * 73.1 + 20) % 200} r={1 + (i % 3) * 0.5} fill="white" opacity={0.3 + (i % 5) * 0.12} />
                ))}
                <ellipse cx="400" cy="430" rx="350" ry="20" fill="#1a0a30" opacity="0.3" />
                <path d="M0,400 Q100,380 200,400 Q300,420 400,400 Q500,380 600,400 Q700,420 800,400 L800,450 L0,450 Z" fill="#0d0520" opacity="0.5" />
            </svg>
        ),
        ocean: (
            <svg viewBox="0 0 800 450" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <linearGradient id="ocean-sky" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#0093E9" />
                        <stop offset="100%" stopColor="#004080" />
                    </linearGradient>
                </defs>
                <rect width="800" height="450" fill="url(#ocean-sky)" />
                <circle cx="600" cy="100" r="50" fill="#ffeaa7" opacity="0.6" />
                {[...Array(8)].map((_, i) => (
                    <path key={i} d={`M${i * 100},${250 + i * 5} Q${i * 100 + 50},${230 + i * 8} ${i * 100 + 100},${250 + i * 5}`} stroke="#80D0C7" fill="none" strokeWidth="2" opacity="0.5" />
                ))}
                <path d="M0,300 Q200,260 400,300 Q600,340 800,300 L800,450 L0,450 Z" fill="#006994" opacity="0.6" />
                <path d="M0,350 Q200,320 400,350 Q600,380 800,350 L800,450 L0,450 Z" fill="#004070" opacity="0.7" />
                <path d="M300,200 L310,180 L320,200 Z" fill="white" opacity="0.7" />
                <rect x="295" y="200" width="30" height="15" rx="3" fill="white" opacity="0.5" />
            </svg>
        ),
        forest: (
            <svg viewBox="0 0 800 450" xmlns="http://www.w3.org/2000/svg">
                <rect width="800" height="450" fill="#0a1a0a" />
                <rect width="800" height="300" fill="#0d2b0d" />
                {[...Array(12)].map((_, i) => {
                    const x = 40 + i * 65;
                    const h = 100 + (i % 3) * 40;
                    return (
                        <g key={i}>
                            <polygon points={`${x},${400 - h} ${x - 30},400 ${x + 30},400`} fill={`hsl(${140 + i * 5}, 60%, ${15 + i * 2}%)`} />
                            <polygon points={`${x},${400 - h - 30} ${x - 22},${400 - h + 20} ${x + 22},${400 - h + 20}`} fill={`hsl(${140 + i * 5}, 65%, ${20 + i * 2}%)`} />
                            <rect x={x - 3} y={400 - 20} width="6" height="20" fill="#3d2b1f" />
                        </g>
                    );
                })}
                <rect y="400" width="800" height="50" fill="#1a0f0a" />
                {[...Array(30)].map((_, i) => (
                    <circle key={i} cx={(i * 137.5 + 30) % 800} cy={(i * 73.1 + 10) % 150} r={0.8} fill="#fffde7" opacity={0.5 + (i % 4) * 0.12} />
                ))}
            </svg>
        ),
    };

    
    const defaultPattern = (
        <svg viewBox="0 0 800 450" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <linearGradient id="default-bg" x1="0" y1="0" x2="1" y2="1">
                    <stop offset="0%" stopColor="#0A0A0F" />
                    <stop offset="50%" stopColor="#0E1225" />
                    <stop offset="100%" stopColor="#0A1A30" />
                </linearGradient>
            </defs>
            <rect width="800" height="450" fill="url(#default-bg)" />
            {[...Array(20)].map((_, i) => (
                <circle key={i} cx={(i * 123 + 50) % 800} cy={(i * 87 + 30) % 450} r={10 + (i % 5) * 8} fill={`hsl(${195 + i * 8}, 80%, 50%)`} opacity={0.06 + (i % 4) * 0.03} />
            ))}
            {[...Array(8)].map((_, i) => (
                <line key={`l${i}`} x1={(i * 100)} y1={0} x2={(i * 100 + 200)} y2={450} stroke="#00D1FF" strokeWidth="0.5" opacity="0.08" />
            ))}
            <rect x="100" y="100" width="200" height="150" rx="8" fill="none" stroke="#00D1FF" strokeWidth="1" opacity="0.1" />
            <rect x="400" y="200" width="150" height="100" rx="8" fill="none" stroke="#00FFB2" strokeWidth="1" opacity="0.08" />
            <circle cx="600" cy="150" r="60" fill="none" stroke="#00D1FF" strokeWidth="1" opacity="0.1" />
        </svg>
    );

    return (
        <div className="canvas-bg">
            {patterns[category] || defaultPattern}
        </div>
    );
}


function ConnectionLines({ points }: { points: Point[] }) {
    if (points.length < 2) return null;
    return (
        <svg className="connection-line" viewBox="0 0 100 100" preserveAspectRatio="none">
            {points.map((pt, i) => {
                if (i === 0) return null;
                const prev = points[i - 1];
                return (
                    <line
                        key={i}
                        x1={prev.x * 100}
                        y1={prev.y * 100}
                        x2={pt.x * 100}
                        y2={pt.y * 100}
                    />
                );
            })}
        </svg>
    );
}

interface Props {
    category: string;
    points: Point[];
    onAddPoint: (point: Point) => void;
    maxPoints: number;
    showPoints: boolean; 
    disabled?: boolean;
}

export default function ClickCanvas({ category, points, onAddPoint, maxPoints, showPoints, disabled }: Props) {
    const containerRef = useRef<HTMLDivElement>(null);
    const [lastClick, setLastClick] = useState<Point | null>(null);

    const handleClick = useCallback((e: React.MouseEvent<HTMLDivElement>) => {
        if (disabled || points.length >= maxPoints) return;

        const rect = containerRef.current?.getBoundingClientRect();
        if (!rect) return;

        
        const x = (e.clientX - rect.left) / rect.width;
        const y = (e.clientY - rect.top) / rect.height;

        const point: Point = {
            x: Math.max(0, Math.min(1, x)),
            y: Math.max(0, Math.min(1, y)),
        };

        setLastClick(point);
        onAddPoint(point);
    }, [disabled, points.length, maxPoints, onAddPoint]);

    return (
        <div>
            <div
                ref={containerRef}
                className="canvas-container"
                onClick={handleClick}
                role="img"
                aria-label={`Click canvas — place authentication points. ${points.length} of ${maxPoints} placed.`}
            >
                <CanvasBackground category={category} />

                {}
                {showPoints && <ConnectionLines points={points} />}

                {}
                {points.map((pt, i) => (
                    <div
                        key={i}
                        className={`click-point ${showPoints ? 'neon-active' : 'click-point-login'}`}
                        style={{
                            left: `${pt.x * 100}%`,
                            top: `${pt.y * 100}%`,
                        }}
                    >
                        {showPoints && (
                            <span className="mono-label">{i + 1}</span>
                        )}
                    </div>
                ))}
            </div>

            <div className="canvas-info">
                <span>Click to place coordinates</span>
                <span className="points-count">{points.length} / {maxPoints}</span>
            </div>
        </div>
    );
}

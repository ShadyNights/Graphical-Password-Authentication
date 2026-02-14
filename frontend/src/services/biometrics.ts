

export interface BiometricsData {
    velocities: number[];
    accelerations: number[];
    click_intervals: number[];
    mouse_path: { x: number; y: number; t: number }[];
    dwell_time_ms: number;
    total_time_ms: number;
    scroll_jitter_count: number;
    honey_pixel_hits: number;
}

export class BiometricsCollector {
    private startTime: number = 0;
    private firstClickTime: number = 0;
    private lastClickTime: number = 0;
    private lastMousePos: { x: number; y: number; t: number } | null = null;
    private lastVelocity: number = 0;

    private velocities: number[] = [];
    private accelerations: number[] = [];
    private clickIntervals: number[] = [];
    private mousePath: { x: number; y: number; t: number }[] = [];
    private scrollCount: number = 0;
    private honeyPixelHits: number = 0;

    
    private honeyPixels: { x: number; y: number }[] = [
        { x: 0.25, y: 0.25 },
        { x: 0.5, y: 0.5 },
        { x: 0.75, y: 0.75 },
        { x: 0.25, y: 0.75 },
        { x: 0.75, y: 0.25 },
    ];

    private scrollHandler: (() => void) | null = null;

    start() {
        this.startTime = Date.now();
        this.firstClickTime = 0;
        this.lastClickTime = 0;
        this.lastMousePos = null;
        this.lastVelocity = 0;
        this.velocities = [];
        this.accelerations = [];
        this.clickIntervals = [];
        this.mousePath = [];
        this.scrollCount = 0;
        this.honeyPixelHits = 0;

        
        this.scrollHandler = () => { this.scrollCount++; };
        window.addEventListener('scroll', this.scrollHandler, { passive: true });
    }

    recordMouseMove(clientX: number, clientY: number) {
        const now = Date.now();
        const pos = { x: clientX, y: clientY, t: now };

        
        if (this.mousePath.length < 200) {
            if (this.mousePath.length === 0 || now - this.mousePath[this.mousePath.length - 1].t > 30) {
                this.mousePath.push(pos);
            }
        }

        if (this.lastMousePos) {
            const dt = (now - this.lastMousePos.t) / 1000; 
            if (dt > 0.005) { 
                const dx = clientX - this.lastMousePos.x;
                const dy = clientY - this.lastMousePos.y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                const velocity = distance / dt;

                this.velocities.push(velocity);

                
                if (this.lastVelocity > 0) {
                    const acceleration = (velocity - this.lastVelocity) / dt;
                    this.accelerations.push(Math.abs(acceleration));
                }
                this.lastVelocity = velocity;
            }
        }

        this.lastMousePos = pos;
    }

    recordClick(normalizedX: number, normalizedY: number) {
        const now = Date.now();

        
        if (this.firstClickTime === 0) {
            this.firstClickTime = now;
        }

        
        if (this.lastClickTime > 0) {
            this.clickIntervals.push(now - this.lastClickTime);
        }
        this.lastClickTime = now;

        
        for (const hp of this.honeyPixels) {
            if (Math.abs(normalizedX - hp.x) < 0.005 && Math.abs(normalizedY - hp.y) < 0.005) {
                this.honeyPixelHits++;
            }
        }
    }

    getData(): BiometricsData {
        const now = Date.now();
        return {
            velocities: this.velocities.slice(-50), 
            accelerations: this.accelerations.slice(-50),
            click_intervals: this.clickIntervals,
            mouse_path: this.mousePath.slice(-100).map(p => ({
                x: p.x / window.innerWidth, 
                y: p.y / window.innerHeight,
                t: p.t - this.startTime,
            })),
            dwell_time_ms: this.firstClickTime > 0 ? this.firstClickTime - this.startTime : 0,
            total_time_ms: now - this.startTime,
            scroll_jitter_count: this.scrollCount,
            honey_pixel_hits: this.honeyPixelHits,
        };
    }

    stop() {
        if (this.scrollHandler) {
            window.removeEventListener('scroll', this.scrollHandler);
            this.scrollHandler = null;
        }
    }
}

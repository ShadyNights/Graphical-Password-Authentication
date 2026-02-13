/**
 * Device Fingerprint Generator
 *
 * Collects non-invasive device attributes and produces a SHA-256 hash.
 * Used for device anomaly detection in the risk scoring model.
 *
 * Attributes collected:
 * - Screen resolution
 * - Timezone
 * - CPU core count
 * - Canvas rendering hash
 * - WebGL renderer string
 */

async function sha256(message: string): Promise<string> {
    const msgBuffer = new TextEncoder().encode(message);
    const hashBuffer = await crypto.subtle.digest('SHA-256', msgBuffer);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}

function getCanvasFingerprint(): string {
    try {
        const canvas = document.createElement('canvas');
        canvas.width = 200;
        canvas.height = 50;
        const ctx = canvas.getContext('2d');
        if (!ctx) return 'no-canvas';

        ctx.textBaseline = 'top';
        ctx.font = '14px Arial';
        ctx.fillStyle = '#f60';
        ctx.fillRect(125, 1, 62, 20);
        ctx.fillStyle = '#069';
        ctx.fillText('GPA fingerprint', 2, 15);
        ctx.fillStyle = 'rgba(102, 204, 0, 0.7)';
        ctx.fillText('GPA fingerprint', 4, 17);

        return canvas.toDataURL().slice(-50);
    } catch {
        return 'canvas-error';
    }
}

function getWebGLRenderer(): string {
    try {
        const canvas = document.createElement('canvas');
        const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
        if (!gl) return 'no-webgl';

        const debugInfo = (gl as WebGLRenderingContext).getExtension('WEBGL_debug_renderer_info');
        if (!debugInfo) return 'no-debug-info';

        return (gl as WebGLRenderingContext).getParameter(debugInfo.UNMASKED_RENDERER_WEBGL) || 'unknown';
    } catch {
        return 'webgl-error';
    }
}

export async function generateDeviceFingerprint(): Promise<string> {
    const components = [
        `${screen.width}x${screen.height}`,
        `${screen.colorDepth}`,
        Intl.DateTimeFormat().resolvedOptions().timeZone,
        `${navigator.hardwareConcurrency || 0}`,
        navigator.language,
        `${navigator.maxTouchPoints || 0}`,
        getCanvasFingerprint(),
        getWebGLRenderer(),
    ];

    const raw = components.join('|');
    return sha256(raw);
}

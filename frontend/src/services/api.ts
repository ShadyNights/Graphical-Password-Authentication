import { BiometricsData } from './biometrics';

const BASE_URL = import.meta.env.VITE_API_URL || '';
const cleanBase = BASE_URL.replace(/\/$/, '');
const API_BASE = cleanBase.endsWith('/api/auth') ? cleanBase : `${cleanBase}/api/auth`;

export interface Point {
    x: number;
    y: number;
}

export interface ImageInfo {
    id: string;
    label: string;
    category: string;
}

export interface ChallengeResponse {
    challenge_id: string;
    image_pool: ImageInfo[];
    message: string;
}

export interface AuthResponse {
    status: 'processing' | 'success' | 'failed' | 'error';
    challenge_id?: string;
    message: string;
    token?: string;
    risk_level?: string;
}

export async function requestChallenge(username: string): Promise<ChallengeResponse> {
    const res = await fetch(`${API_BASE}/challenge`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username }),
    });
    if (!res.ok) throw new Error('Challenge request failed');
    return res.json();
}

export async function register(
    username: string,
    challengeId: string,
    selectedImageIds: string[],
    clickPoints: Point[],
): Promise<AuthResponse> {
    const res = await fetch(`${API_BASE}/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            username,
            challenge_id: challengeId,
            selected_image_ids: selectedImageIds,
            click_points: clickPoints,
        }),
    });
    return res.json();
}

export async function login(
    username: string,
    challengeId: string,
    selectedImageIds: string[],
    clickPoints: Point[],
    mouseMetrics?: BiometricsData,
    deviceFingerprint?: string,
): Promise<AuthResponse> {
    const res = await fetch(`${API_BASE}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            username,
            challenge_id: challengeId,
            selected_image_ids: selectedImageIds,
            click_points: clickPoints,
            mouse_metrics: mouseMetrics,
            device_fingerprint: deviceFingerprint,
        }),
    });
    return res.json();
}

import React, { useState, useCallback, useRef, useEffect } from 'react';
import ImageGrid from './ImageGrid';
import ClickCanvas from './ClickCanvas';
import {
    requestChallenge, register, login,
    Point, ImageInfo, AuthResponse,
} from '../services/api';
import { BiometricsCollector } from '../services/biometrics';
import { generateDeviceFingerprint } from '../services/fingerprint';

type Mode = 'register' | 'login';
type Phase = 'username' | 'recognition' | 'recall' | 'loading' | 'success' | 'failed';

const REQUIRED_IMAGES = 3;
const REQUIRED_POINTS = 6;

/* ── Challenge-Handshake Phases ─────────────────────────────────────── */
const HANDSHAKE_PHASES = [
    { label: 'Validating Nonce', icon: '🔑' },
    { label: 'Verifying Credentials', icon: '🛡️' },
    { label: 'Analyzing Biometrics', icon: '🧬' },
    { label: 'Establishing Session', icon: '🔗' },
];

export default function AuthFlow() {
    const [mode, setMode] = useState<Mode>('register');
    const [phase, setPhase] = useState<Phase>('username');
    const [username, setUsername] = useState('');
    const [challengeId, setChallengeId] = useState('');
    const [imagePool, setImagePool] = useState<ImageInfo[]>([]);
    const [selectedImageIds, setSelectedImageIds] = useState<string[]>([]);
    const [clickPoints, setClickPoints] = useState<Point[]>([]);
    const [result, setResult] = useState<AuthResponse | null>(null);
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const [deviceFp, setDeviceFp] = useState('');
    const [handshakeStep, setHandshakeStep] = useState(0);

    // Phase II: Biometrics collector instance
    const biometricsRef = useRef<BiometricsCollector>(new BiometricsCollector());

    // Generate device fingerprint on mount
    useEffect(() => {
        generateDeviceFingerprint().then(setDeviceFp);
    }, []);

    // Track mouse movements globally during auth flow
    useEffect(() => {
        if (phase === 'recognition' || phase === 'recall') {
            const handler = (e: MouseEvent) => {
                biometricsRef.current.recordMouseMove(e.clientX, e.clientY);
            };
            window.addEventListener('mousemove', handler, { passive: true });
            return () => window.removeEventListener('mousemove', handler);
        }
    }, [phase]);

    // Handshake animation timer
    useEffect(() => {
        if (phase !== 'loading') return;
        setHandshakeStep(0);
        const interval = setInterval(() => {
            setHandshakeStep(prev => {
                if (prev >= HANDSHAKE_PHASES.length - 1) {
                    clearInterval(interval);
                    return prev;
                }
                return prev + 1;
            });
        }, 800);
        return () => clearInterval(interval);
    }, [phase]);

    const resetFlow = useCallback(() => {
        setPhase('username');
        setChallengeId('');
        setImagePool([]);
        setSelectedImageIds([]);
        setClickPoints([]);
        setResult(null);
        setError('');
        setHandshakeStep(0);
        biometricsRef.current.stop();
        biometricsRef.current = new BiometricsCollector();
    }, []);

    const handleModeSwitch = useCallback((newMode: Mode) => {
        setMode(newMode);
        resetFlow();
    }, [resetFlow]);

    // ── Phase 1: Request Challenge ──────────────────────────────────────

    const handleUsernameSubmit = useCallback(async (e: React.FormEvent) => {
        e.preventDefault();
        if (!username.trim() || username.length < 3) {
            setError('PROTOCOL_ERR: Identifier must be ≥ 3 characters');
            return;
        }
        setError('');
        setLoading(true);

        try {
            const challenge = await requestChallenge(username);
            setChallengeId(challenge.challenge_id);
            setImagePool(challenge.image_pool);
            setPhase('recognition');
            biometricsRef.current.start();
        } catch (err) {
            setError('CONNECTION_ERR: Backend unreachable. Verify service status.');
        } finally {
            setLoading(false);
        }
    }, [username]);

    // ── Phase 2: Image Recognition ──────────────────────────────────────

    const handleImageToggle = useCallback((id: string) => {
        setSelectedImageIds((prev) => {
            if (prev.includes(id)) return prev.filter((x) => x !== id);
            if (prev.length < REQUIRED_IMAGES) return [...prev, id];
            return prev;
        });
    }, []);

    const handleRecognitionNext = useCallback(() => {
        if (selectedImageIds.length !== REQUIRED_IMAGES) return;
        setPhase('recall');
    }, [selectedImageIds]);

    // ── Phase 3: Cued Recall (Click Points) ─────────────────────────────

    const handleAddPoint = useCallback((point: Point) => {
        biometricsRef.current.recordClick(point.x, point.y);
        setClickPoints((prev) => {
            if (prev.length >= REQUIRED_POINTS) return prev;
            return [...prev, point];
        });
    }, []);

    // ── Submit ──────────────────────────────────────────────────────────

    const handleSubmit = useCallback(async () => {
        if (clickPoints.length !== REQUIRED_POINTS) return;
        setPhase('loading');

        const biometricsData = biometricsRef.current.getData();
        biometricsRef.current.stop();

        try {
            let response: AuthResponse;
            if (mode === 'register') {
                response = await register(username, challengeId, selectedImageIds, clickPoints);
            } else {
                response = await login(
                    username, challengeId, selectedImageIds, clickPoints,
                    biometricsData,
                    deviceFp,
                );
            }

            setResult(response);
            setPhase(response.status === 'success' ? 'success' : 'failed');
        } catch (err) {
            setResult({ status: 'error', message: 'CONNECTION_ERR: Handshake terminated.' });
            setPhase('failed');
        }
    }, [clickPoints, mode, username, challengeId, selectedImageIds, deviceFp]);

    // ── Derived state ──────────────────────────────────────────────────

    const primaryCategory = imagePool.find((img) => img.id === selectedImageIds[0])?.category || 'default';

    const phaseNumber =
        phase === 'username' ? 1 :
            phase === 'recognition' ? 2 :
                phase === 'recall' || phase === 'loading' ? 3 : 3;

    const phaseSteps = [
        { label: 'Identity', num: 1 },
        { label: 'Recognition', num: 2 },
        { label: 'Recall', num: 3 },
    ];

    return (
        <>
            {/* ── Pill Toggle (Mode Switcher) ─────────────────────── */}
            <div className="pill-toggle">
                <div className={`slider ${mode}`} />
                <button
                    className={mode === 'register' ? 'active' : ''}
                    onClick={() => handleModeSwitch('register')}
                    aria-label="Switch to registration mode"
                >
                    Register
                </button>
                <button
                    className={mode === 'login' ? 'active' : ''}
                    onClick={() => handleModeSwitch('login')}
                    aria-label="Switch to login mode"
                >
                    Login
                </button>
            </div>

            {/* ── Auth Card ───────────────────────────────────────── */}
            <div className="auth-card">
                <div className="auth-card-header">
                    <h2>
                        <span className="header-icon">{mode === 'register' ? '◈' : '◇'}</span>
                        {mode === 'register' ? 'Create Graphical Password' : 'Authenticate Identity'}
                    </h2>
                    <span className={`security-badge ${phase === 'success' ? 'verified' : 'pending'}`}>
                        <span className={`badge-dot ${phase === 'success' ? 'live' : 'pending'}`} />
                        {phase === 'success' ? 'Verified' : 'Pending'}
                    </span>
                </div>

                {/* ── Phase Indicator (Node-Line) ──────────────────── */}
                {phase !== 'success' && phase !== 'failed' && (
                    <div className="phase-line">
                        {phaseSteps.map((step, i) => (
                            <React.Fragment key={step.num}>
                                <div className={`phase-node ${phaseNumber > step.num ? 'completed' : phaseNumber === step.num ? 'active' : ''}`}>
                                    <span className="pulse-dot" />
                                    <span>{step.label}</span>
                                </div>
                                {i < phaseSteps.length - 1 && (
                                    <div className={`phase-connector ${phaseNumber > step.num ? 'completed' : ''}`} />
                                )}
                            </React.Fragment>
                        ))}
                    </div>
                )}

                <div className="auth-card-body">
                    {/* ── Username Phase ────────────────────────────── */}
                    {phase === 'username' && (
                        <form className="username-form" onSubmit={handleUsernameSubmit}>
                            <div className="input-group">
                                <label htmlFor="username">Identifier</label>
                                <input
                                    id="username"
                                    type="text"
                                    className="input-field"
                                    placeholder="Enter your identifier..."
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                    autoFocus
                                    autoComplete="off"
                                    maxLength={64}
                                    aria-describedby={error ? 'username-error' : undefined}
                                />
                            </div>
                            {error && (
                                <div id="username-error" className="error-inline" role="alert">{error}</div>
                            )}
                            <div className="btn-row">
                                <button type="submit" className="btn btn-primary" disabled={loading} style={{ flex: 1 }}>
                                    {loading ? (
                                        <><span className="loading-spinner" /> Initiating Challenge...</>
                                    ) : (
                                        `Initialize ${mode === 'register' ? 'Registration' : 'Authentication'} →`
                                    )}
                                </button>
                            </div>
                            {deviceFp && (
                                <div className="device-fp" aria-label="Device fingerprint">
                                    DEVICE_FP: {deviceFp.slice(0, 16)}···
                                </div>
                            )}
                        </form>
                    )}

                    {/* ── Recognition Phase ─────────────────────────── */}
                    {phase === 'recognition' && (
                        <div>
                            <p className="phase-description">
                                {mode === 'register'
                                    ? <>Select <span className="highlight">{REQUIRED_IMAGES} recognition images</span> — these become part of your graphical credential. Commit to memory.</>
                                    : <>Identify the <span className="highlight">{REQUIRED_IMAGES} images</span> chosen during registration.</>}
                            </p>
                            <ImageGrid
                                images={imagePool}
                                selectedIds={selectedImageIds}
                                onToggle={handleImageToggle}
                                maxSelections={REQUIRED_IMAGES}
                            />
                            <div className="btn-row">
                                <button className="btn btn-secondary" onClick={resetFlow}>← Abort</button>
                                <button
                                    className="btn btn-primary"
                                    onClick={handleRecognitionNext}
                                    disabled={selectedImageIds.length !== REQUIRED_IMAGES}
                                    style={{ flex: 1 }}
                                >
                                    Proceed to Recall Phase →
                                </button>
                            </div>
                        </div>
                    )}

                    {/* ── Recall Phase ──────────────────────────────── */}
                    {phase === 'recall' && (
                        <div>
                            <p className="phase-description">
                                {mode === 'register'
                                    ? <>Place <span className="highlight">{REQUIRED_POINTS} secret coordinates</span> on the canvas below. Order matters.</>
                                    : <>Reproduce your <span className="highlight">{REQUIRED_POINTS} coordinates</span> in the original sequence.</>}
                            </p>
                            <ClickCanvas
                                category={primaryCategory}
                                points={clickPoints}
                                onAddPoint={handleAddPoint}
                                maxPoints={REQUIRED_POINTS}
                                showPoints={mode === 'register'}
                                disabled={clickPoints.length >= REQUIRED_POINTS}
                            />
                            <div className="btn-row">
                                <button className="btn btn-secondary" onClick={() => { setClickPoints([]); setPhase('recognition'); }}>← Back</button>
                                <button className="btn btn-danger" onClick={() => setClickPoints([])} disabled={clickPoints.length === 0}>
                                    Reset
                                </button>
                                <button
                                    className="btn btn-primary"
                                    onClick={handleSubmit}
                                    disabled={clickPoints.length !== REQUIRED_POINTS}
                                    style={{ flex: 1 }}
                                >
                                    {mode === 'register' ? 'Commit Password' : 'Execute Authentication'} →
                                </button>
                            </div>
                        </div>
                    )}

                    {/* ── Loading Phase (Challenge-Handshake Skeleton) ── */}
                    {phase === 'loading' && (
                        <div className="handshake-container" role="status" aria-label="Authentication in progress">
                            {HANDSHAKE_PHASES.map((step, i) => (
                                <div
                                    key={step.label}
                                    className={`handshake-step ${i < handshakeStep ? 'completed' : i === handshakeStep ? 'active' : ''}`}
                                >
                                    <div className="handshake-icon">{step.icon}</div>
                                    <span className="handshake-label">{step.label}</span>
                                </div>
                            ))}
                            <div className="handshake-progress">
                                <div
                                    className="handshake-progress-bar"
                                    style={{ width: `${((handshakeStep + 1) / HANDSHAKE_PHASES.length) * 100}%` }}
                                />
                            </div>
                        </div>
                    )}

                    {/* ── Success Phase ─────────────────────────────── */}
                    {phase === 'success' && result && (
                        <div className="result-screen success-glow neon-success">
                            <div className="result-icon success" aria-hidden="true">✓</div>
                            <h3 className="result-title" style={{ color: 'var(--accent-success)' }}>
                                {mode === 'register' ? 'Credential Established' : 'Access Granted'}
                            </h3>
                            <p className="result-subtitle">
                                {mode === 'register'
                                    ? 'Graphical credential hashed with Argon2id and committed to secure storage.'
                                    : 'Identity verified. Encrypted session token issued.'}
                            </p>
                            {result.risk_level && (
                                <div style={{ marginBottom: '12px' }}>
                                    <span className={`security-badge ${result.risk_level === 'normal' ? 'verified' : 'pending'}`}>
                                        <span className={`badge-dot ${result.risk_level === 'normal' ? 'live' : 'pending'}`} />
                                        Risk: {result.risk_level.toUpperCase()}
                                    </span>
                                </div>
                            )}
                            {result.token && (
                                <div className="result-token">
                                    <div className="result-token-label">JWT Session Token</div>
                                    {result.token}
                                </div>
                            )}
                            <div className="btn-row" style={{ justifyContent: 'center', marginTop: '24px' }}>
                                <button className="btn btn-primary" onClick={() => { resetFlow(); if (mode === 'register') setMode('login'); }}>
                                    {mode === 'register' ? 'Proceed to Authentication →' : 'Session Active'}
                                </button>
                            </div>
                        </div>
                    )}

                    {/* ── Failed Phase ──────────────────────────────── */}
                    {phase === 'failed' && result && (
                        <div className="result-screen neon-error shake">
                            <div className="result-icon failure" aria-hidden="true">✕</div>
                            <h3 className="result-title" style={{ color: 'var(--accent-danger)' }}>
                                Authentication Failed
                            </h3>
                            <p className="result-subtitle">
                                {result.message || 'Authentication Failed: Retry Protocol'}
                            </p>
                            {result.risk_level && result.risk_level !== 'normal' && (
                                <div style={{ marginBottom: '12px' }}>
                                    <span className="security-badge pending">
                                        <span className="badge-dot pending" />
                                        Threat Level: {result.risk_level.toUpperCase()}
                                    </span>
                                </div>
                            )}
                            <div className="btn-row" style={{ justifyContent: 'center', marginTop: '24px' }}>
                                <button className="btn btn-primary" onClick={resetFlow}>Retry Authentication</button>
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* ── Security Status Bar ──────────────────────────────── */}
            <div className="status-bar" role="status" aria-label="Security status indicators">
                <div className="status-item">
                    <span className="status-dot" />
                    <span>Argon2id</span>
                </div>
                <div className="status-item">
                    <span className="status-dot" />
                    <span>JWT-RS256</span>
                </div>
                <div className="status-item">
                    <span className="status-dot" />
                    <span>Nonce-Auth</span>
                </div>
                <div className="status-item">
                    <span className="status-dot" />
                    <span>Biometrics</span>
                </div>
                <div className="status-item">
                    <span className={`status-dot ${deviceFp ? '' : 'warning'}`} />
                    <span>Device-FP</span>
                </div>
                <div className="status-item">
                    <span className="status-dot" />
                    <span>Anti-Bot</span>
                </div>
            </div>

            {error && phase !== 'username' && (
                <div className="toast error" role="alert">{error}</div>
            )}
        </>
    );
}

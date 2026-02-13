import AuthFlow from './components/AuthFlow'

function ShieldIcon() {
    return (
        <svg width="32" height="32" viewBox="0 0 24 24">
            <path
                fill="none"
                stroke="#00D1FF"
                strokeWidth="2"
                d="M12 2l7 4v6c0 5-3 8-7 10-4-2-7-5-7-10V6l7-4z"
            />
        </svg>
    )
}

export default function App() {
    return (
        <div className="app-shell scan-overlay">
            {/* ── Logo Section ───────────────────────────────────── */}
            <div className="logo-section">
                <div className="logo-icon">
                    <ShieldIcon />
                </div>
                <h1 className="logo-title">
                    <span>GPA</span> Secure Auth
                </h1>
                <p className="logo-subtitle">Graphical Password Authentication</p>
                <div className="security-classification glass-card">
                    SECURITY LEVEL: FINTECH-GRADE
                </div>
            </div>

            {/* ── Auth Flow ──────────────────────────────────────── */}
            <AuthFlow />
        </div>
    )
}

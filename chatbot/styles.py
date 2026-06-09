"""
styles.py — CSS theme for PolicyAI Chatbot
"""

CSS = """
/* ─────────────────────── Google Font ─────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ─────────────────────── Design tokens ───────────────────── */
:root {
    --bg-base    : #070b14;
    --bg-panel   : #0d1422;
    --bg-raised  : #111c2e;
    --border     : rgba(99,130,188,0.12);
    --border-lit : rgba(99,130,188,0.28);
    --accent     : #3b82f6;
    --accent-dim : rgba(59,130,246,0.18);
    --accent-glow: rgba(59,130,246,0.35);
    --text-hi    : #f0f4ff;
    --text-mid   : #8fa3c8;
    --text-lo    : #3d546e;
    --radius-lg  : 18px;
    --radius-md  : 12px;
    --radius-sm  : 8px;
    --font       : 'Inter', ui-sans-serif, system-ui, sans-serif;
    --mono       : 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
}

/* ─────────────────────── Page / container ─────────────────── */
body,
.gradio-container {
    background : var(--bg-base) !important;
    font-family: var(--font) !important;
    color      : var(--text-hi) !important;
}

.gradio-container {
    max-width: 1380px !important;
    padding  : 28px 24px !important;
    margin   : 0 auto !important;
}

/* ─────────────────────── Strip Gradio chrome ──────────────── */
footer,
.footer        { display : none !important; }
.block,
.form          { background : transparent !important;
                 border     : none !important;
                 box-shadow : none !important;
                 padding    : 0 !important; }
label > span   { display : none !important; }

/* ─────────────────────── Header card ─────────────────────── */
#policyai-header {
    background   : linear-gradient(135deg, #0d1730 0%, #0f1d36 60%, #10172b 100%);
    border       : 1px solid var(--border-lit);
    border-radius: var(--radius-lg);
    padding      : 30px 36px 26px;
    margin-bottom: 20px;
    position     : relative;
    overflow     : hidden;
}

#policyai-header::before {
    content : '';
    position: absolute;
    inset   : 0;
    background: radial-gradient(ellipse 60% 80% at 80% 30%,
                rgba(59,130,246,0.07) 0%, transparent 70%),
                radial-gradient(ellipse 40% 60% at 10% 80%,
                rgba(129,140,248,0.05) 0%, transparent 60%);
    pointer-events: none;
}

.header-logo {
    font-size  : 2.2rem;
    font-weight: 700;
    line-height: 1.15;
    margin-bottom: 4px;
}

/* Emoji rendered normally — gradient clip breaks emoji rendering */
.logo-icon {
    display             : inline-block;
    -webkit-text-fill-color: initial;
    background          : none;
}

/* Only the text word gets the shimmer gradient */
.logo-text {
    background          : linear-gradient(110deg, #60a5fa 20%, #a78bfa 55%, #60a5fa 90%);
    background-size     : 200% 100%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip     : text;
    animation           : shimmer 5s linear infinite;
}

@keyframes shimmer {
    0%   { background-position: 100% 0; }
    100% { background-position:  -100% 0; }
}

.header-sub {
    font-size  : 0.9rem;
    color      : var(--text-mid);
    margin     : 0 0 18px;
    font-weight: 400;
}

.badge-row { display: flex; gap: 8px; flex-wrap: wrap; }

.badge {
    display      : inline-flex;
    align-items  : center;
    gap          : 5px;
    padding      : 4px 11px;
    border-radius: 20px;
    font-size    : 11.5px;
    font-weight  : 500;
    letter-spacing: 0.02em;
    user-select  : none;
}
.badge-b { background: rgba(59,130,246,0.14); border: 1px solid rgba(59,130,246,0.3); color: #93c5fd; }
.badge-g { background: rgba(52,211,153,0.12); border: 1px solid rgba(52,211,153,0.3); color: #6ee7b7; }
.badge-v { background: rgba(129,140,248,0.13); border: 1px solid rgba(129,140,248,0.3); color: #c4b5fd; }
.badge-o { background: rgba(251,191,36,0.11); border: 1px solid rgba(251,191,36,0.28); color: #fde68a; }

/* ─────────────────────── Chat panel ──────────────────────── */
#policyai-chat {
    background   : var(--bg-panel) !important;
    border       : 1px solid var(--border) !important;
    border-radius: var(--radius-lg) !important;
    padding      : 6px !important;
}

/* User bubble — container + all text */
#policyai-chat .message.user,
#policyai-chat [data-testid="user-message"],
#policyai-chat .user-row .message-bubble-border {
    background   : linear-gradient(135deg, #1d4ed8, #2563eb) !important;
    border-radius: 16px 16px 4px 16px !important;
    box-shadow   : 0 4px 18px rgba(37,99,235,0.3) !important;
    border       : none !important;
    padding      : 12px 16px !important;
}

#policyai-chat .message.user,
#policyai-chat .message.user *,
#policyai-chat [data-testid="user-message"],
#policyai-chat [data-testid="user-message"] * {
    color: #ffffff !important;
}

/* Bot bubble — container */
#policyai-chat .message.bot,
#policyai-chat [data-testid="bot-message"],
#policyai-chat .bot-row .message-bubble-border {
    background   : #1a2744 !important;
    border       : 1px solid rgba(99,130,188,0.22) !important;
    border-radius: 16px 16px 16px 4px !important;
    box-shadow   : 0 2px 14px rgba(0,0,0,0.3) !important;
    padding      : 12px 16px !important;
}

/* Bot bubble — force all text visible */
#policyai-chat .message.bot,
#policyai-chat .message.bot p,
#policyai-chat .message.bot span,
#policyai-chat .message.bot li,
#policyai-chat .message.bot ul,
#policyai-chat .message.bot ol,
#policyai-chat .message.bot strong,
#policyai-chat .message.bot em,
#policyai-chat .message.bot code,
#policyai-chat .message.bot a,
#policyai-chat .message.bot h1,
#policyai-chat .message.bot h2,
#policyai-chat .message.bot h3,
#policyai-chat [data-testid="bot-message"],
#policyai-chat [data-testid="bot-message"] * {
    color: #dde6f5 !important;
}

/* ─────────────────────── Input bar ────────────────────────── */
#policyai-input-row {
    display      : flex !important;
    align-items  : flex-end !important;
    gap          : 10px !important;
    background   : var(--bg-panel) !important;
    border       : 1px solid var(--border-lit) !important;
    border-radius: var(--radius-lg) !important;
    padding      : 10px 12px !important;
    margin-top   : 10px !important;
    transition   : border-color .2s !important;
}

#policyai-input-row:focus-within {
    border-color : var(--accent) !important;
    box-shadow   : 0 0 0 3px var(--accent-dim) !important;
}

#policyai-msg textarea {
    background   : transparent !important;
    border       : none !important;
    box-shadow   : none !important;
    color        : var(--text-hi) !important;
    font-family  : var(--font) !important;
    font-size    : 14.5px !important;
    line-height  : 1.55 !important;
    resize       : none !important;
    padding      : 4px 0 !important;
}

#policyai-msg textarea::placeholder { color: var(--text-lo) !important; }
#policyai-msg .wrap { background: transparent !important; border: none !important; }

/* ─────────────────────── Send button ─────────────────────── */
#policyai-send {
    background   : linear-gradient(135deg, #2563eb, #1d4ed8) !important;
    border       : none !important;
    border-radius: var(--radius-md) !important;
    color        : #fff !important;
    font-family  : var(--font) !important;
    font-size    : 13.5px !important;
    font-weight  : 600 !important;
    padding      : 10px 20px !important;
    min-width    : 78px !important;
    cursor       : pointer !important;
    transition   : all .2s ease !important;
    box-shadow   : 0 4px 14px rgba(37,99,235,0.4) !important;
    flex-shrink  : 0 !important;
}

#policyai-send:hover {
    background   : linear-gradient(135deg, #3b82f6, #2563eb) !important;
    transform    : translateY(-1px) !important;
    box-shadow   : 0 6px 22px rgba(59,130,246,0.5) !important;
}

#policyai-send:active { transform: translateY(0) !important; }

/* ─────────────────────── Clear button ────────────────────── */
#policyai-clear {
    background   : rgba(239,68,68,0.08) !important;
    border       : 1px solid rgba(239,68,68,0.2) !important;
    border-radius: var(--radius-md) !important;
    color        : #f87171 !important;
    font-size    : 13px !important;
    font-weight  : 500 !important;
    padding      : 10px 14px !important;
    flex-shrink  : 0 !important;
    transition   : all .2s ease !important;
}

#policyai-clear:hover {
    background   : rgba(239,68,68,0.16) !important;
    border-color : rgba(239,68,68,0.45) !important;
}

/* ─────────────────────── Right panel ─────────────────────── */
.panel-section {
    background   : var(--bg-panel);
    border       : 1px solid var(--border);
    border-radius: var(--radius-lg);
    overflow     : hidden;
    margin-bottom: 12px;
}

.panel-title {
    font-size    : 10.5px;
    font-weight  : 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color        : var(--text-lo);
    padding      : 14px 16px 10px;
    border-bottom: 1px solid var(--border);
}

.panel-body { padding: 10px 10px 12px; }

/* Question buttons */
.q-btn button {
    background   : transparent !important;
    border       : 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color        : #7da8e0 !important;
    font-family  : var(--font) !important;
    font-size    : 13px !important;
    font-weight  : 400 !important;
    text-align   : left !important;
    padding      : 9px 13px !important;
    width        : 100% !important;
    margin-bottom: 5px !important;
    transition   : all .18s ease !important;
    line-height  : 1.4 !important;
    white-space  : normal !important;
}

.q-btn button:hover {
    background   : var(--accent-dim) !important;
    border-color : rgba(59,130,246,0.4) !important;
    color        : #bfdbfe !important;
    padding-left : 17px !important;
}

/* ─────────────────────── Sources box ─────────────────────── */
#policyai-sources textarea {
    background   : transparent !important;
    border       : none !important;
    box-shadow   : none !important;
    color        : #6b8aad !important;
    font-family  : var(--mono) !important;
    font-size    : 11.5px !important;
    line-height  : 1.65 !important;
    padding      : 14px 16px !important;
    resize       : none !important;
}
#policyai-sources textarea::placeholder { color: var(--text-lo) !important; }
#policyai-sources .wrap { background: transparent !important; border: none !important; }

/* ─────────────────────── App footer ──────────────────────── */
#policyai-footer {
    text-align  : center;
    font-size   : 11.5px;
    color       : var(--text-lo);
    padding     : 14px 0 2px;
    border-top  : 1px solid var(--border);
    margin-top  : 6px;
}

#policyai-footer a { color: #3d546e; text-decoration: none; transition: color .15s; }
#policyai-footer a:hover { color: var(--accent); }
#policyai-footer .sep { margin: 0 8px; opacity: .4; }

/* ─────────────────────── Scrollbar ────────────────────────── */
::-webkit-scrollbar { width: 3px; height: 3px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(99,130,188,0.2); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(99,130,188,0.4); }
"""

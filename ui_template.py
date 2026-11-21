"""Self-contained Claude-style dark conversational UI with Interactive Question Cards for RedTape Navigator.
Zero external CDN dependencies for reliable offline/hackathon-WiFi rendering.
"""


def render_ui() -> str:
    return r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>RedTape</title>
  <link rel="icon" type="image/png" href="/static/favicon.png">
  <style>
    :root {
      --bg-main: #212121;
      --bg-sidebar: #171717;
      --bg-composer: #2f2f2f;
      --bg-card: #262522;
      --bg-card-hover: #2f2e2a;
      --bg-elevated: #2a2a2a;
      --bg-artifact: #1a1a1a;
      --border-subtle: rgba(255, 255, 255, 0.08);
      --border-strong: rgba(255, 255, 255, 0.13);
      --text-primary: #ececec;
      --text-secondary: #a8a6a1;
      --text-muted: #787671;
      --accent: #d97757;
      --accent-hover: #c96848;
      --accent-soft: rgba(217, 119, 87, 0.15);
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      background: var(--bg-main);
      color: var(--text-primary);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      height: 100vh;
      width: 100vw;
      overflow: hidden;
      display: flex;
      -webkit-font-smoothing: antialiased;
    }

    .serif { font-family: Georgia, Cambria, "Times New Roman", Times, serif; }

    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.14); border-radius: 999px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(255, 255, 255, 0.24); }

    .hidden { display: none !important; }

    /* Sidebar */
    .sidebar {
      width: 260px;
      flex-shrink: 0;
      background: var(--bg-sidebar);
      border-right: 1px solid var(--border-subtle);
      display: flex;
      flex-direction: column;
      user-select: none;
    }
    .sidebar-top {
      height: 56px;
      padding: 0 12px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .brand-btn {
      display: flex;
      align-items: center;
      gap: 10px;
      background: transparent;
      border: none;
      color: var(--text-primary);
      padding: 6px 8px;
      border-radius: 8px;
      cursor: pointer;
    }
    .brand-btn:hover { background: rgba(255, 255, 255, 0.06); }
    .brand-icon {
      width: 26px;
      height: 26px;
      border-radius: 7px;
      background: var(--accent-soft);
      border: 1px solid rgba(217, 119, 87, 0.35);
      color: var(--accent);
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .brand-title { font-size: 19px; letter-spacing: -0.02em; font-weight: 400; }
    .icon-btn {
      width: 32px;
      height: 32px;
      border-radius: 8px;
      background: transparent;
      border: none;
      color: var(--text-secondary);
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
    }
    .icon-btn:hover { background: rgba(255, 255, 255, 0.06); color: var(--text-primary); }
    .new-chat-wrap { padding: 0 12px 12px; }
    .new-chat-btn {
      width: 100%;
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 9px 12px;
      border-radius: 9px;
      background: transparent;
      border: none;
      color: var(--text-primary);
      font-size: 13.5px;
      font-weight: 500;
      cursor: pointer;
    }
    .new-chat-btn:hover { background: rgba(255, 255, 255, 0.06); }
    .plus-circle {
      width: 20px;
      height: 20px;
      border-radius: 50%;
      background: var(--accent);
      color: #fff;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 14px;
      line-height: 1;
    }
    .recents-wrap { flex: 1; overflow-y: auto; padding: 0 10px 12px; }
    .recents-label { padding: 6px 10px; font-size: 11px; font-weight: 600; color: var(--text-muted); letter-spacing: 0.05em; text-transform: uppercase; }
    .session-item {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 9px 10px;
      border-radius: 8px;
      font-size: 13px;
      color: #b5b3ad;
      cursor: pointer;
      margin-bottom: 3px;
      border-left: 2.5px solid transparent;
      transition: background 0.12s ease, border-color 0.12s ease, color 0.12s ease;
    }
    .session-item:hover { background: rgba(255, 255, 255, 0.05); color: var(--text-primary); }
    .session-item.active {
      background: rgba(217, 119, 87, 0.13);
      border-left-color: var(--accent);
      color: #ffffff;
    }
    .session-left { display: flex; align-items: center; gap: 9px; min-width: 0; flex: 1; }
    .session-icon { flex-shrink: 0; color: #787671; }
    .session-item.active .session-icon { color: var(--accent); }
    .session-text-wrap { min-width: 0; display: flex; flex-direction: column; gap: 1px; }
    .session-title { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: 12.5px; font-weight: 500; }
    .session-meta { font-size: 11px; color: #787671; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .session-del {
      background: transparent;
      border: none;
      color: var(--text-muted);
      cursor: pointer;
      opacity: 0;
      font-size: 13px;
      padding: 2px 6px;
      border-radius: 4px;
      transition: all 0.14s ease;
      flex-shrink: 0;
    }
    .session-item:hover .session-del { opacity: 0.7; }
    .session-del:hover { opacity: 1 !important; color: #ef4444; background: rgba(239, 68, 68, 0.15); }
    .sidebar-footer {
      padding: 12px;
      border-top: 1px solid var(--border-subtle);
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .user-pill { display: flex; align-items: center; gap: 10px; min-width: 0; }
    .avatar {
      width: 28px;
      height: 28px;
      border-radius: 50%;
      background: #363532;
      color: var(--text-primary);
      font-size: 11px;
      font-weight: 600;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }
    .user-name { font-size: 13px; font-weight: 500; color: var(--text-primary); }
    .user-sub { font-size: 11px; color: var(--text-muted); }

    /* Main Split Container */
    .workspace { flex: 1; display: flex; min-width: 0; height: 100%; }
    .chat-column { flex: 1; display: flex; flex-direction: column; min-width: 0; height: 100%; background: var(--bg-main); }
    .topbar { height: 56px; padding: 0 16px; display: flex; align-items: center; justify-content: space-between; flex-shrink: 0; }
    .topbar-left { display: flex; align-items: center; gap: 8px; min-width: 0; }
    .header-title { font-size: 14px; font-weight: 500; color: #d4d2cd; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .topbar-new-chat-btn {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 5px 10px;
      border-radius: 8px;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--border-subtle);
      color: #d4d2cd;
      font-size: 12px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.15s ease;
      white-space: nowrap;
      margin-left: 6px;
    }
    .topbar-new-chat-btn:hover {
      background: rgba(255, 255, 255, 0.09);
      border-color: rgba(255, 255, 255, 0.18);
      color: #fff;
    }
    .welcome-suggestions {
      width: 100%;
      margin-top: 24px;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    .suggestions-label {
      font-size: 11.5px;
      font-weight: 500;
      color: var(--text-muted);
      letter-spacing: 0.04em;
      text-transform: uppercase;
      text-align: center;
    }
    .suggestion-chips {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 10px;
      width: 100%;
    }
    .suggestion-chip {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 11px 14px;
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      border-radius: 12px;
      color: #d4d2cd;
      font-size: 13px;
      text-align: left;
      cursor: pointer;
      transition: all 0.15s ease;
    }
    .suggestion-chip:hover {
      background: var(--bg-card-hover);
      border-color: rgba(255, 255, 255, 0.16);
      color: #ffffff;
      transform: translateY(-1px);
    }
    .chip-icon { font-size: 16px; flex-shrink: 0; }
    .chip-text { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .topbar-right { display: flex; align-items: center; gap: 10px; }
    .model-switcher-wrap { position: relative; }
    .model-pill-btn {
      display: inline-flex;
      align-items: center;
      gap: 7px;
      padding: 5px 11px;
      border-radius: 8px;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--border-subtle);
      color: #d4d2cd;
      font-size: 12px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.15s ease;
    }
    .model-pill-btn:hover { background: rgba(255, 255, 255, 0.09); border-color: rgba(255, 255, 255, 0.18); color: #fff; }
    .ollama-dot { width: 7px; height: 7px; border-radius: 50%; background: #10b981; box-shadow: 0 0 6px rgba(16, 185, 129, 0.6); }
    .model-dropdown {
      position: absolute;
      top: calc(100% + 6px);
      right: 0;
      width: 290px;
      background: #1e1e1e;
      border: 1px solid var(--border-strong);
      border-radius: 12px;
      padding: 6px;
      box-shadow: 0 12px 32px rgba(0, 0, 0, 0.55);
      z-index: 100;
    }
    .model-option {
      padding: 8px 10px;
      border-radius: 8px;
      cursor: pointer;
      transition: background 0.12s;
    }
    .model-option:hover { background: rgba(255, 255, 255, 0.06); }
    .model-option.active { background: rgba(217, 119, 87, 0.15); border: 1px solid rgba(217, 119, 87, 0.3); }
    .model-opt-title { font-size: 12.5px; font-weight: 500; color: #fff; display: flex; align-items: center; justify-content: space-between; }
    .model-opt-sub { font-size: 11px; color: #8e8c86; margin-top: 3px; line-height: 1.35; }
    .model-rec-tag { font-size: 10px; background: rgba(16, 185, 129, 0.15); color: #34d399; padding: 1px 6px; border-radius: 4px; font-weight: 500; }
    .model-fast-tag { font-size: 10px; background: rgba(59, 130, 246, 0.15); color: #60a5fa; padding: 1px 6px; border-radius: 4px; font-weight: 500; }
    .artifact-toggle-btn {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 6px 12px;
      border-radius: 8px;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--border-subtle);
      color: var(--text-primary);
      font-size: 12.5px;
      font-weight: 500;
      cursor: pointer;
    }
    .artifact-toggle-btn:hover { background: rgba(255, 255, 255, 0.09); }
    .artifact-count { color: var(--text-secondary); font-size: 11.5px; }

    /* Welcome View */
    .welcome-view { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 0 20px 72px; }
    .welcome-inner { width: 100%; max-width: 680px; display: flex; flex-direction: column; align-items: center; }
    .greeting-row { display: flex; align-items: center; gap: 14px; margin-bottom: 28px; }
    .greeting-text { font-size: 36px; font-weight: 400; letter-spacing: -0.02em; color: var(--text-primary); }

    /* Composer */
    .composer-box {
      width: 100%;
      background: var(--bg-composer);
      border: 1px solid var(--border-strong);
      border-radius: 16px;
      padding: 14px 16px 12px;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
    }
    .composer-box:focus-within { border-color: rgba(255, 255, 255, 0.24); }
    .composer-textarea {
      width: 100%;
      background: transparent;
      border: none;
      color: var(--text-primary);
      font-family: inherit;
      font-size: 15px;
      line-height: 1.55;
      resize: none;
      outline: none;
    }
    .composer-textarea::placeholder { color: #8e8c86; }
    .composer-footer { display: flex; align-items: center; justify-content: space-between; padding-top: 10px; margin-top: 4px; }
    .model-tag { font-size: 12px; color: #9b9994; padding: 4px 8px; border-radius: 6px; }
    .send-btn {
      width: 32px;
      height: 32px;
      border-radius: 8px;
      background: var(--accent);
      border: none;
      color: #fff;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
    }
    .send-btn:hover { background: var(--accent-hover); }
    .send-btn:disabled { opacity: 0.45; cursor: not-allowed; }

    /* Active Chat Stream */
    .chat-view { flex: 1; display: flex; flex-direction: column; min-height: 0; }
    .chat-stream { flex: 1; overflow-y: auto; padding: 8px 24px 32px; }
    .chat-inner { max-width: 740px; margin: 0 auto; display: flex; flex-direction: column; gap: 24px; }
    .user-row { display: flex; justify-content: flex-end; }
    .user-bubble {
      max-width: 82%;
      background: #141414;
      border: 1px solid rgba(255, 255, 255, 0.06);
      color: var(--text-primary);
      padding: 12px 16px;
      border-radius: 16px;
      font-size: 14.5px;
      line-height: 1.6;
      white-space: pre-wrap;
    }

    .assistant-block { display: flex; flex-direction: column; gap: 10px; }

    /* Claude Single-Line Thinking Summary Toggle */
    .thought-toggle {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: transparent;
      border: none;
      color: #9b9994;
      font-size: 13px;
      padding: 3px 0;
      cursor: pointer;
      width: fit-content;
    }
    .thought-toggle:hover { color: var(--text-primary); }
    .thought-list {
      margin-top: 4px;
      margin-bottom: 4px;
      padding: 6px 0 6px 14px;
      border-left: 1.5px solid rgba(255, 255, 255, 0.12);
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    .thought-step-title { font-size: 12.5px; font-weight: 500; color: #d4d2cd; }
    .thought-step-url { color: var(--accent); text-decoration: none; font-size: 11.5px; margin-left: 6px; }
    .thought-step-url:hover { text-decoration: underline; }
    .thought-step-detail { font-size: 12px; color: #8e8c86; line-height: 1.5; margin-top: 2px; }

    @keyframes pulseDot { 0%, 100% { opacity: 0.4; } 50% { opacity: 1; } }
    .live-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--accent); animation: pulseDot 1.3s ease-in-out infinite; }

    /* Quick Action Pill */
    .quick-gen-pill {
      font-size: 11.5px;
      color: #f0b097;
      background: var(--accent-soft);
      border: 1px solid rgba(217, 119, 87, 0.35);
      padding: 4px 10px;
      border-radius: 6px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.15s ease;
    }
    .quick-gen-pill:hover {
      background: rgba(217, 119, 87, 0.28);
      color: #fff;
    }

    /* Prose */
    .prose p { margin: 0 0 12px; line-height: 1.68; font-size: 15px; color: var(--text-primary); }
    .prose p:last-child { margin-bottom: 0; }
    .prose ul { margin: 4px 0 12px 20px; }
    .prose li { margin-bottom: 6px; line-height: 1.6; font-size: 14.5px; color: #e2e1dc; }
    .prose strong { color: #ffffff; font-weight: 600; }
    .prose code {
      background: rgba(255, 255, 255, 0.07);
      border: 1px solid rgba(255, 255, 255, 0.08);
      padding: 1px 6px;
      border-radius: 5px;
      font-size: 12.5px;
      color: #f0b097;
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
    }

    /* Inline Artifact Card */
    .artifact-card {
      margin-top: 8px;
      padding: 13px 15px;
      border-radius: 12px;
      background: var(--bg-elevated);
      border: 1px solid var(--border-strong);
      display: flex;
      align-items: center;
      justify-content: space-between;
      max-width: 460px;
      cursor: pointer;
    }
    .artifact-card:hover { background: #313131; }
    .artifact-card-left { display: flex; align-items: center; gap: 12px; min-width: 0; }
    .artifact-card-icon {
      width: 36px;
      height: 36px;
      border-radius: 9px;
      background: var(--accent-soft);
      border: 1px solid rgba(217, 119, 87, 0.35);
      color: var(--accent);
      font-size: 11px;
      font-weight: 700;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }
    .artifact-card-title { font-size: 13.5px; font-weight: 500; color: var(--text-primary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .artifact-card-sub { font-size: 12px; color: #8e8c86; margin-top: 2px; }

    /* Bottom Composer Area */
    .bottom-bar { flex-shrink: 0; padding: 8px 24px 16px; background: linear-gradient(to top, var(--bg-main) 80%, transparent); }
    .bottom-inner { max-width: 740px; margin: 0 auto; }
    .disclaimer { text-align: center; font-size: 11px; color: var(--text-muted); margin-top: 8px; }

    /* Right Artifacts Split Panel */
    .artifacts-panel {
      width: 48%;
      max-width: 680px;
      min-width: 380px;
      height: 100%;
      background: var(--bg-artifact);
      border-left: 1px solid var(--border-subtle);
      display: flex;
      flex-direction: column;
      flex-shrink: 0;
    }
    .artifacts-header {
      height: 56px;
      padding: 0 16px;
      border-bottom: 1px solid var(--border-subtle);
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-shrink: 0;
    }
    .artifacts-title { font-size: 13.5px; font-weight: 500; color: var(--text-primary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .tab-group { display: flex; background: #262626; padding: 3px; border-radius: 8px; border: 1px solid var(--border-subtle); }
    .tab-btn { padding: 4px 10px; border-radius: 6px; border: none; background: transparent; color: var(--text-secondary); font-size: 12px; cursor: pointer; }
    .tab-btn.active { background: #363636; color: var(--text-primary); font-weight: 500; }

    .pdf-bar { padding: 10px 16px; border-bottom: 1px solid var(--border-subtle); display: flex; gap: 8px; overflow-x: auto; flex-shrink: 0; }
    .pdf-pill {
      padding: 6px 11px;
      border-radius: 8px;
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid var(--border-subtle);
      color: var(--text-secondary);
      font-size: 12px;
      white-space: nowrap;
      cursor: pointer;
    }
    .pdf-pill.active { background: var(--accent-soft); border-color: rgba(217, 119, 87, 0.45); color: #f0b097; font-weight: 500; }
    .pdf-meta {
      padding: 8px 16px;
      background: var(--bg-main);
      border-bottom: 1px solid var(--border-subtle);
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 12px;
      color: var(--text-secondary);
      flex-shrink: 0;
    }
    .pdf-link { color: var(--accent); text-decoration: none; font-weight: 500; }
    .pdf-link:hover { text-decoration: underline; }
    .pdf-viewer-wrap { flex: 1; background: #141414; position: relative; }
    .pdf-object { width: 100%; height: 100%; border: none; }

    .panel-scroll { flex: 1; overflow-y: auto; padding: 18px; }
    .review-pre {
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      font-size: 12.5px;
      line-height: 1.6;
      color: #d4d2cd;
      white-space: pre-wrap;
      background: var(--bg-main);
      border: 1px solid var(--border-subtle);
      border-radius: 12px;
      padding: 16px;
    }
    .portal-card { padding: 14px 16px; border-radius: 12px; background: var(--bg-main); border: 1px solid var(--border-subtle); margin-bottom: 12px; }
    .portal-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
    .portal-name { font-size: 13.5px; font-weight: 500; color: var(--text-primary); }
    .portal-badge { font-size: 11px; padding: 2px 8px; border-radius: 999px; background: rgba(255,255,255,0.06); color: #c8c6c0; }
    .portal-links { display: flex; gap: 16px; font-size: 12px; }
  </style>
</head>
<body>

  <!-- LEFT SIDEBAR -->
  <aside id="sidebar" class="sidebar">
    <div class="sidebar-top">
      <button onclick="startNewChat()" class="brand-btn">
        <span class="brand-icon">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round">
            <path d="M12 2v20M2 12h20M4.93 4.93l14.14 14.14M19.07 4.93L4.93 19.07"/>
          </svg>
        </span>
        <span class="brand-title serif">RedTape</span>
      </button>
      <button onclick="toggleSidebar()" title="Close sidebar" class="icon-btn">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
          <rect x="3" y="3" width="18" height="18" rx="2"/><line x1="9" y1="3" x2="9" y2="21"/>
        </svg>
      </button>
    </div>

    <div class="new-chat-wrap">
      <button onclick="startNewChat()" class="new-chat-btn">
        <span class="plus-circle">+</span>
        <span>New chat</span>
      </button>
    </div>

    <div class="recents-wrap">
      <div class="recents-label">Recents</div>
      <div id="sessions-list"></div>
    </div>

    <div class="sidebar-footer">
      <div class="user-pill" title="Better Auth & Neon Connected">
        <div class="avatar" style="background:#d97757; color:#fff; font-weight:700;">TG</div>
        <div style="min-width:0;">
          <div class="user-name" style="display:flex; align-items:center; gap:5px;">
            <span>Tamajit Ghosh</span>
            <span style="font-size:9px; background:rgba(34,197,94,0.18); color:#4ade80; border:1px solid rgba(34,197,94,0.3); border-radius:4px; padding:1px 4px; font-weight:600;">VERIFIED</span>
          </div>
          <div class="user-sub" style="font-size:10.5px; color:#8e8c86;">Citizen #WB-700144 · Baruipur</div>
        </div>
      </div>
      <a href="https://console.neon.tech" target="_blank" title="Neon Database & pgvector" class="icon-btn" style="text-decoration:none;">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <ellipse cx="12" cy="5" rx="9" ry="3"></ellipse>
          <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path>
          <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path>
        </svg>
      </a>
    </div>
  </aside>

  <!-- MAIN WORKSPACE -->
  <div class="workspace">
    <main class="chat-column">
      <header class="topbar">
        <div class="topbar-left">
          <button id="open-sidebar-btn" onclick="toggleSidebar()" title="Open sidebar" class="icon-btn hidden">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
              <rect x="3" y="3" width="18" height="18" rx="2"/><line x1="9" y1="3" x2="9" y2="21"/>
            </svg>
          </button>
          <span id="chat-header-title" class="header-title"></span>
          <button onclick="startNewChat()" class="topbar-new-chat-btn" title="Start a fresh consultation">
            <span class="plus-circle" style="width:16px;height:16px;font-size:12px;">+</span>
            <span>New Chat</span>
          </button>
          <div style="margin-left:8px; display:inline-flex; align-items:center; gap:6px; font-size:11px; padding:3px 8px; border-radius:6px; background:rgba(217,119,87,0.1); border:1px solid rgba(217,119,87,0.25); color:#d97757;">
            <span style="width:6px; height:6px; border-radius:50%; background:#22c55e;"></span>
            <span>Better Auth & pgvector Active</span>
          </div>
        </div>
        <div class="topbar-right">
          <div class="model-switcher-wrap">
            <button id="model-pill" onclick="toggleModelDropdown(event)" class="model-pill-btn" title="Switch local Ollama model">
              <span class="ollama-dot"></span>
              <span id="active-model-name">llama3.1:8b</span>
              <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="6 9 12 15 18 9"/></svg>
            </button>
            <div id="model-dropdown" class="model-dropdown hidden">
              <!-- populated dynamically from /api/model -->
            </div>
          </div>
          <button id="header-artifact-btn" onclick="toggleArtifactsPanel()" class="artifact-toggle-btn hidden">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#d97757" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/>
            </svg>
            <span>Artifacts</span>
            <span id="artifact-count-pill" class="artifact-count">0</span>
          </button>
        </div>
      </header>

      <!-- WELCOME VIEW -->
      <section id="welcome-view" class="welcome-view">
        <div class="welcome-inner">
          <div class="greeting-row">
            <span style="color:var(--accent); display:flex;">
              <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
                <path d="M12 2v20M2 12h20M4.93 4.93l14.14 14.14M19.07 4.93L4.93 19.07"/>
              </svg>
            </span>
            <h1 id="welcome-greeting" class="greeting-text serif">Good evening</h1>
          </div>

          <div class="composer-box">
            <textarea id="welcome-input" rows="3" placeholder="How can I help you today? (e.g. I wanna open a restaurant in Beleghata, Kolkata)" class="composer-textarea" onkeydown="handleComposerKeydown(event, 'welcome')"></textarea>
            <div class="composer-footer">
              <span class="model-tag" id="welcome-model-tag">RedTape · llama3.1:8b</span>
              <button onclick="sendFromComposer('welcome')" class="send-btn" title="Send">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
                  <line x1="12" y1="19" x2="12" y2="5"/><polyline points="5 12 12 5 19 12"/>
                </svg>
              </button>
            </div>
          </div>

          <div class="welcome-suggestions">
            <div class="suggestions-label">Explore official regulatory filings in West Bengal:</div>
            <div class="suggestion-chips">
              <button onclick="fillAndSendGoal('i wanna have a house colour painting shop in baruipur, west bengal')" class="suggestion-chip">
                <span class="chip-icon">🎨</span>
                <span class="chip-text">Paint Shop in Baruipur, WB</span>
              </button>
              <button onclick="fillAndSendGoal('i wanna open a restaurant in beleghata, kolkata')" class="suggestion-chip">
                <span class="chip-icon">🍽️</span>
                <span class="chip-text">Restaurant in Beleghata, Kolkata</span>
              </button>
              <button onclick="fillAndSendGoal('open a stationary book stall in sodpur')" class="suggestion-chip">
                <span class="chip-icon">📚</span>
                <span class="chip-text">Stationery Stall in Sodpur</span>
              </button>
              <button onclick="fillAndSendGoal('open a clothes shop in barrackpore')" class="suggestion-chip">
                <span class="chip-icon">👗</span>
                <span class="chip-text">Clothes Shop in Barrackpore</span>
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- ACTIVE CHAT VIEW -->
      <section id="chat-view" class="chat-view hidden">
        <div id="chat-stream" class="chat-stream">
          <div id="chat-messages-inner" class="chat-inner"></div>
        </div>

        <div class="bottom-bar">
          <div class="bottom-inner">
            <div class="composer-box">
              <textarea id="chat-input" rows="2" placeholder="Reply to RedTape..." class="composer-textarea" onkeydown="handleComposerKeydown(event, 'chat')"></textarea>
              <div class="composer-footer">
                <div style="display:flex; align-items:center; gap:8px;">
                  <span class="model-tag" id="chat-model-tag">RedTape · llama3.1:8b</span>
                  <button onclick="finalizeAndGeneratePacks()" class="quick-gen-pill" title="Generate filled official PDFs now">⚡ Generate Forms</button>
                </div>
                <button id="chat-send-btn" onclick="sendFromComposer('chat')" class="send-btn" title="Send">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="12" y1="19" x2="12" y2="5"/><polyline points="5 12 12 5 19 12"/>
                  </svg>
                </button>
              </div>
            </div>
            <div class="disclaimer">Autonomous Administrative Intelligence for West Bengal · Powered by local Ollama & Neon PostgreSQL</div>
          </div>
        </div>
      </section>
    </main>

    <!-- RIGHT SLIDE-OUT ARTIFACTS PANEL -->
    <aside id="artifacts-panel" class="artifacts-panel hidden">
      <div class="artifacts-header">
        <div id="artifact-panel-title" class="artifacts-title">Compliance Pack</div>
        <div style="display:flex; align-items:center; gap:8px;">
          <div class="tab-group">
            <button id="art-tab-pdfs" onclick="switchArtifactTab('pdfs')" class="tab-btn active">PDFs</button>
            <button id="art-tab-review" onclick="switchArtifactTab('review')" class="tab-btn">Review</button>
            <button id="art-tab-portals" onclick="switchArtifactTab('portals')" class="tab-btn">Portals</button>
          </div>
          <button onclick="closeArtifactsPanel()" title="Close" class="icon-btn">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
              <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
      </div>

      <!-- PDFs Tab -->
      <div id="art-body-pdfs" style="flex:1; display:flex; flex-direction:column; min-height:0;">
        <div id="pdf-selector-bar" class="pdf-bar"></div>
        <div class="pdf-meta">
          <span id="pdf-meta-status"></span>
          <a id="pdf-download-link" href="#" target="_blank" class="pdf-link">Open / Download PDF ↗</a>
        </div>
        <div class="pdf-viewer-wrap">
          <object id="pdf-preview-obj" type="application/pdf" class="pdf-object"></object>
        </div>
      </div>

      <!-- Review Tab -->
      <div id="art-body-review" class="panel-scroll hidden">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
          <span style="font-size:12px; color:#8e8c86; font-family:monospace;">review.md</span>
          <button onclick="copyReview()" class="pdf-pill">Copy</button>
        </div>
        <pre id="review-md-content" class="review-pre"></pre>
      </div>

      <!-- Portals Tab -->
      <div id="art-body-portals" class="panel-scroll hidden">
        <div id="portals-list"></div>
      </div>
    </aside>
  </div>

  <script>
    let appState = null;
    let isBusy = false;
    let activePdfIndex = 0;

    function setTimeGreeting() {
      const hr = new Date().getHours();
      const greet = hr < 12 ? 'Good morning' : hr < 17 ? 'Good afternoon' : 'Good evening';
      const el = document.getElementById('welcome-greeting');
      if (el) el.textContent = greet;
    }

    function toggleSidebar() {
      const sb = document.getElementById('sidebar');
      const openBtn = document.getElementById('open-sidebar-btn');
      const isHidden = sb.classList.toggle('hidden');
      openBtn.classList.toggle('hidden', !isHidden);
    }

    function openArtifactsPanel(tab = 'pdfs') {
      document.getElementById('artifacts-panel').classList.remove('hidden');
      switchArtifactTab(tab);
    }

    function closeArtifactsPanel() {
      document.getElementById('artifacts-panel').classList.add('hidden');
    }

    function toggleArtifactsPanel() {
      const p = document.getElementById('artifacts-panel');
      if (p.classList.contains('hidden')) openArtifactsPanel('pdfs');
      else closeArtifactsPanel();
    }

    function switchArtifactTab(tab) {
      ['pdfs', 'review', 'portals'].forEach(t => {
        document.getElementById(`art-tab-${t}`).classList.toggle('active', t === tab);
        document.getElementById(`art-body-${t}`).classList.toggle('hidden', t !== tab);
      });
    }

    function escapeHtml(s) {
      return String(s || '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
    }

    function renderMarkdown(md) {
      if (!md) return '';
      const lines = md.split('\n');
      let html = '';
      let inList = false;
      for (const rawLine of lines) {
        const line = rawLine.trim();
        if (!line) {
          if (inList) { html += '</ul>'; inList = false; }
          continue;
        }
        let fmt = escapeHtml(line)
          .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
          .replace(/`([^`]+)`/g, '<code>$1</code>');
        if (fmt.startsWith('- ') || fmt.startsWith('• ')) {
          if (!inList) { html += '<ul>'; inList = true; }
          html += `<li>${fmt.slice(2)}</li>`;
        } else {
          if (inList) { html += '</ul>'; inList = false; }
          html += `<p>${fmt}</p>`;
        }
      }
      if (inList) html += '</ul>';
      return html;
    }

    function toggleThoughtBlock(id) {
      const body = document.getElementById(id);
      if (body) body.classList.toggle('hidden');
    }

    function handleComposerKeydown(e, source) {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendFromComposer(source);
      }
    }

    function sendFromComposer(source) {
      const el = document.getElementById(source === 'welcome' ? 'welcome-input' : 'chat-input');
      const text = (el.value || '').trim();
      if (!text || isBusy) return;
      el.value = '';
      sendMessage(text);
    }

    function fillAndSendGoal(text) {
      const el = document.getElementById('welcome-input');
      if (el) el.value = text;
      sendMessage(text);
    }

    function isNewGoalText(text) {
      const t = (text || '').toLowerCase().trim();
      const starters = [
        'i wanna open', 'i want to open', 'open a', 'open an', 'opening a', 'opening an',
        'wanna open', 'want to open', 'start a', 'start an', 'starting a', 'starting an',
        'setup a', 'set up a', 'setting up a', 'create a', 'establish a', 'i wanna have', 'i want to have',
        'register a new', '1.', '2.', '3.'
      ];
      if (starters.some(s => t.startsWith(s) || t.includes(' ' + s + ' '))) return true;
      const bizWords = ['bakery', 'restaurant', 'eatery', 'cafe', 'book stall', 'stationery', 'clothes shop', 'garment store', 'painting shop', 'paint shop', 'store', 'shop'];
      const locWords = ['kolkata', 'beleghata', 'sodpur', 'sodepur', 'barrackpore', 'salt lake', 'park circus', 'baruipur', 'howrah', 'durgapur', 'siliguri'];
      return bizWords.some(b => t.includes(b)) && (locWords.some(l => t.includes(l)) || t.includes('open') || t.includes('start') || t.includes('have'));
    }

    function showChatMode() {
      document.getElementById('welcome-view').classList.add('hidden');
      document.getElementById('chat-view').classList.remove('hidden');
    }

    function showWelcomeMode() {
      document.getElementById('welcome-view').classList.remove('hidden');
      document.getElementById('chat-view').classList.add('hidden');
      closeArtifactsPanel();
      document.getElementById('header-artifact-btn').classList.add('hidden');
      document.getElementById('chat-header-title').textContent = '';
      document.getElementById('chat-messages-inner').innerHTML = '';
      const wInput = document.getElementById('welcome-input');
      if (wInput) wInput.value = '';
      const cInput = document.getElementById('chat-input');
      if (cInput) cInput.value = '';
    }

    function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

    async function sendMessage(text) {
      isBusy = true;
      showChatMode();
      const container = document.getElementById('chat-messages-inner');
      const streamEl = document.getElementById('chat-stream');

      // CRITICAL FIX: If starting a fresh chat or a new goal, clear previous messages from DOM!
      if (!appState || appState.is_empty || !appState.session_id || isNewGoalText(text)) {
        container.innerHTML = '';
      }

      const displayTxt = text === '__SKIP__' ? 'Skipped' : text;
      const userDiv = document.createElement('div');
      userDiv.className = 'user-row';
      userDiv.innerHTML = `<div class="user-bubble">${escapeHtml(displayTxt)}</div>`;
      container.appendChild(userDiv);

      const liveId = `live-${Date.now()}`;
      const liveDiv = document.createElement('div');
      liveDiv.id = liveId;
      liveDiv.className = 'assistant-block';
      liveDiv.innerHTML = `
        <div style="display:inline-flex; align-items:center; gap:8px; font-size:13px; color:#a8a6a1;">
          <span class="live-dot"></span>
          <span id="${liveId}-label">Synthesizing statutory context...</span>
        </div>
        <div id="${liveId}-steps" class="thought-list"></div>
      `;
      container.appendChild(liveDiv);
      streamEl.scrollTop = streamEl.scrollHeight;

      try {
        const payload = { message: text };
        if (appState && appState.session_id) {
          payload.session_id = appState.session_id;
        }
        const res = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
        const data = await res.json();
        const thoughts = data.thought_process || [];
        const stepsBox = document.getElementById(`${liveId}-steps`);
        const liveLabel = document.getElementById(`${liveId}-label`);

        for (let i = 0; i < thoughts.length; i++) {
          const step = thoughts[i];
          if (liveLabel) liveLabel.textContent = step.title || 'Reasoning...';
          if (stepsBox) {
            const item = document.createElement('div');
            item.innerHTML = `
              <div class="thought-step-title">✓ ${escapeHtml(step.title)}</div>
              <div class="thought-step-detail">${escapeHtml(step.details || '')}</div>
            `;
            stepsBox.appendChild(item);
            streamEl.scrollTop = streamEl.scrollHeight;
          }
          await sleep(340);
        }

        liveDiv.remove();
        if (data.state) {
          appState = data.state;
          renderApp(appState);
          if (data.open_artifacts && appState.form_artifacts && appState.form_artifacts.length > 0) {
            openArtifactsPanel('pdfs');
          }
        }
        loadSessions();
      } catch (err) {
        console.error(err);
        liveDiv.remove();
      } finally {
        isBusy = false;
      }
    }

    function renderApp(state) {
      if (!state || state.is_empty || !state.chat_history || state.chat_history.length === 0) {
        showWelcomeMode();
        return;
      }
      showChatMode();
      document.getElementById('chat-header-title').textContent = state.title || 'Consultation';
      const container = document.getElementById('chat-messages-inner');
      container.innerHTML = '';

      const history = state.chat_history || [];
      history.forEach((msg, idx) => {
        if (msg.role === 'user') {
          const div = document.createElement('div');
          div.className = 'user-row';
          div.innerHTML = `<div class="user-bubble">${escapeHtml(msg.content)}</div>`;
          container.appendChild(div);
        } else {
          const div = document.createElement('div');
          div.className = 'assistant-block';
          const thoughts = msg.thought_process || [];
          const thoughtId = `tb-${idx}`;
          const summaryLabel = msg.thinking_summary || `Thought for ${msg.duration_seconds || 1.4}s`;

          let thoughtHtml = '';
          if (thoughts.length > 0) {
            const stepsHtml = thoughts.map(t => {
              let host = '';
              if (t.url) { try { host = new URL(t.url).hostname; } catch(e) { host = t.url; } }
              const urlHtml = t.url ? `<a href="${t.url}" target="_blank" class="thought-step-url">${escapeHtml(host)} ↗</a>` : '';
              return `
                <div>
                  <div class="thought-step-title">${escapeHtml(t.title || t.node)}${urlHtml}</div>
                  <div class="thought-step-detail">${escapeHtml(t.details || '')}</div>
                </div>
              `;
            }).join('');
            thoughtHtml = `
              <div>
                <button onclick="toggleThoughtBlock('${thoughtId}')" class="thought-toggle">
                  <span>${escapeHtml(summaryLabel)}</span>
                  <span style="opacity:0.7;">›</span>
                </button>
                <div id="${thoughtId}" class="thought-list hidden">${stepsHtml}</div>
              </div>
            `;
          }

          const proseHtml = msg.content ? `<div class="prose">${renderMarkdown(msg.content)}</div>` : '';

          // Inline Artifact Card
          let artifactCardHtml = '';
          if (msg.has_artifacts && state.form_artifacts && state.form_artifacts.length > 0) {
            const pdfCount = state.form_artifacts.length;
            const portalCount = (state.portal_artifacts || []).length;
            artifactCardHtml = `
              <div onclick="openArtifactsPanel('pdfs')" class="artifact-card">
                <div class="artifact-card-left">
                  <div class="artifact-card-icon">PDF</div>
                  <div style="min-width:0;">
                    <div class="artifact-card-title">${escapeHtml(state.applicant_profile?.entity_name || state.title)} — Official Forms</div>
                    <div class="artifact-card-sub">${pdfCount} Fillable AcroForm PDFs · ${portalCount} Portal Packs · Click to Inspect</div>
                  </div>
                </div>
                <span style="color:#787671;">›</span>
              </div>
            `;
          }

          div.innerHTML = `${thoughtHtml}${proseHtml}${artifactCardHtml}`;
          container.appendChild(div);
        }
      });

      document.getElementById('chat-stream').scrollTop = document.getElementById('chat-stream').scrollHeight;
      renderArtifactsData(state);
    }

    function renderArtifactsData(state) {
      const pdfs = state.form_artifacts || [];
      const portals = state.portal_artifacts || [];
      const total = pdfs.length + portals.length;

      const headerBtn = document.getElementById('header-artifact-btn');
      document.getElementById('artifact-count-pill').textContent = String(total);
      headerBtn.classList.toggle('hidden', total === 0);

      document.getElementById('artifact-panel-title').textContent =
        (state.applicant_profile?.entity_name || state.title || 'Compliance Pack') + ' · Artifacts';

      const selBar = document.getElementById('pdf-selector-bar');
      selBar.innerHTML = '';
      if (pdfs.length > 0) {
        if (activePdfIndex >= pdfs.length) activePdfIndex = 0;
        pdfs.forEach((fa, i) => {
          const btn = document.createElement('button');
          btn.className = 'pdf-pill' + (i === activePdfIndex ? ' active' : '');
          btn.textContent = fa.form_name.replace('.pdf', '').replace(/_/g, ' ');
          btn.onclick = () => { activePdfIndex = i; renderArtifactsData(appState); };
          selBar.appendChild(btn);
        });

        const cur = pdfs[activePdfIndex];
        const rawPath = (cur.pdf_path || cur.file_path || '').replace(/\\/g, '/');
        const relUrl = rawPath.includes('drafts/') ? '/drafts/' + rawPath.split('drafts/')[1] : '/' + rawPath.replace(/^\//, '');
        document.getElementById('pdf-meta-status').textContent = `${cur.form_name} · ${cur.completion_percentage || 0}% filled`;
        document.getElementById('pdf-download-link').href = relUrl;
        document.getElementById('pdf-preview-obj').data = relUrl + '?t=' + Date.now();
      } else {
        selBar.innerHTML = '<span style="font-size:12px; color:#787671;">Complete the interview to generate fillable PDFs.</span>';
      }

      document.getElementById('review-md-content').textContent =
        state.review_md || 'Complete the interview to generate your regulatory review summary.';

      const portalsList = document.getElementById('portals-list');
      portalsList.innerHTML = '';
      if (portals.length === 0) {
        portalsList.innerHTML = '<div style="font-size:13px; color:#787671;">No portal packs generated yet.</div>';
      } else {
        portals.forEach(pa => {
          const rawCs = (pa.copy_sheet_path || '').replace(/\\/g, '/');
          const mdRel = rawCs.includes('drafts/')
            ? '/drafts/' + rawCs.split('drafts/')[1]
            : '#';
          const card = document.createElement('div');
          card.className = 'portal-card';
          card.innerHTML = `
            <div class="portal-row">
              <div class="portal-name">${escapeHtml(pa.portal_name)}</div>
              <span class="portal-badge">${pa.completion_percentage || 0}% ready</span>
            </div>
            <div class="portal-links">
              <a href="${pa.portal_url || '#'}" target="_blank" class="pdf-link">Official Portal ↗</a>
              <a href="${mdRel}" target="_blank" style="color:#a8a6a1; text-decoration:none;">Open Copy-Sheet ↗</a>
            </div>
          `;
          portalsList.appendChild(card);
        });
      }
    }

    function copyReview() {
      navigator.clipboard.writeText(document.getElementById('review-md-content').textContent);
    }

    async function loadSessions() {
      try {
        const res = await fetch('/api/sessions');
        const data = await res.json();
        const list = document.getElementById('sessions-list');
        const sessions = data.sessions || [];
        const activeId = data.active_id || appState?.session_id;
        if (sessions.length === 0) {
          list.innerHTML = '<div style="padding:16px 10px; font-size:12px; color:#6a6864; text-align:center;">No recent chats</div>';
          return;
        }
        list.innerHTML = sessions.map(s => {
          const isActive = s.id === activeId;
          const cls = 'session-item' + (isActive ? ' active' : '');
          const title = s.title || s.goal || 'Consultation';
          const meta = s.updated_at ? `${s.updated_at}` : 'Recently';
          return `
            <div onclick="openSession('${s.id}')" class="${cls}" title="${escapeHtml(title)}">
              <div class="session-left">
                <svg class="session-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                </svg>
                <div class="session-text-wrap">
                  <span class="session-title">${escapeHtml(title)}</span>
                  <span class="session-meta">${escapeHtml(meta)} · ${s.message_count || 1} msgs</span>
                </div>
              </div>
              <button onclick="removeSession('${s.id}', event)" title="Delete consultation" class="session-del">✕</button>
            </div>
          `;
        }).join('');
      } catch (e) { console.error(e); }
    }

    async function openSession(id) {
      try {
        const res = await fetch(`/api/session/${id}`);
        if (!res.ok) return;
        appState = await res.json();
        activePdfIndex = 0;
        document.getElementById('chat-messages-inner').innerHTML = '';
        renderApp(appState);
        loadSessions();
      } catch (e) { console.error(e); }
    }

    async function startNewChat() {
      try {
        const res = await fetch('/api/new_chat', { method: 'POST' });
        appState = await res.json();
        activePdfIndex = 0;
        document.getElementById('chat-messages-inner').innerHTML = '';
        showWelcomeMode();
        loadSessions();
        const el = document.getElementById('welcome-input');
        if (el) {
          el.value = '';
          el.focus();
        }
      } catch (e) { console.error(e); }
    }

    async function removeSession(id, ev) {
      if (ev) ev.stopPropagation();
      try {
        await fetch('/api/session/delete', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ id }),
        });
        if (appState && appState.session_id === id) {
          appState = null;
          showWelcomeMode();
        }
        loadSessions();
      } catch (e) { console.error(e); }
    }

    async function finalizeAndGeneratePacks() {
      await sendMessage('Please finalize my submission packs and generate all official PDFs now.');
    }

    function toggleModelDropdown(e) {
      if (e) e.stopPropagation();
      const dd = document.getElementById('model-dropdown');
      if (dd) dd.classList.toggle('hidden');
    }

    document.addEventListener('click', () => {
      const dd = document.getElementById('model-dropdown');
      if (dd && !dd.classList.contains('hidden')) {
        dd.classList.add('hidden');
      }
    });

    async function switchModel(modelName) {
      try {
        const res = await fetch('/api/model', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ model: modelName })
        });
        const data = await res.json();
        updateModelUI(data.active_model || modelName);
      } catch (e) {
        console.error('Failed to switch model:', e);
      }
      const dd = document.getElementById('model-dropdown');
      if (dd) dd.classList.add('hidden');
    }

    function renderModelDropdown(models, activeModel) {
      const dd = document.getElementById('model-dropdown');
      if (!dd) return;
      dd.innerHTML = models.map(m => `
        <div class="model-opt ${m === activeModel ? 'active' : ''}" onclick="switchModel('${m}')" style="padding: 8px 10px; border-radius: 6px; cursor: pointer; display: flex; flex-direction: column; gap: 2px;">
          <div style="font-weight: 500; font-size: 13px; color: ${m === activeModel ? 'var(--accent)' : 'var(--text-primary)'};">${m}</div>
          <div style="font-size: 11px; color: var(--text-muted);">${m.includes('8b') ? 'Balanced local reasoning & legal extraction' : 'Ultra-fast low-latency local inference'}</div>
        </div>
      `).join('');
    }

    function updateModelUI(modelName) {
      const pillName = document.getElementById('active-model-name');
      if (pillName) pillName.textContent = modelName;
      const wTag = document.getElementById('welcome-model-tag');
      if (wTag) wTag.textContent = `RedTape · ${modelName}`;
      const cTag = document.getElementById('chat-model-tag');
      if (cTag) cTag.textContent = `RedTape · ${modelName}`;

      const dd = document.getElementById('model-dropdown');
      if (dd) {
        dd.querySelectorAll('.model-opt').forEach(el => {
          const title = el.querySelector('div')?.textContent;
          if (title === modelName) {
            el.classList.add('active');
            el.querySelector('div').style.color = 'var(--accent)';
          } else {
            el.classList.remove('active');
            const d = el.querySelector('div');
            if (d) d.style.color = 'var(--text-primary)';
          }
        });
      }
    }

    async function init() {
      setTimeGreeting();
      try {
        const [stRes, mRes] = await Promise.all([
          fetch('/api/state'),
          fetch('/api/model').catch(() => null)
        ]);
        appState = await stRes.json();
        renderApp(appState);
        loadSessions();
        if (mRes && mRes.ok) {
          const mData = await mRes.json();
          if (mData.available_models) {
            renderModelDropdown(mData.available_models, mData.active_model || 'llama3.1:8b');
          }
          if (mData.active_model) updateModelUI(mData.active_model);
        }
      } catch (e) { console.error(e); }
    }

    window.addEventListener('DOMContentLoaded', init);
  </script>
</body>
</html>
"""

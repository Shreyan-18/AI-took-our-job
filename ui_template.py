"""Self-contained Claude-style dark conversational UI with Login/Sign-Up, /chat/:id navigation,
Interactive Question Cards, and live Official PDF Artifacts panel for RedTape Navigator.
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

    /* Auth Screen (/login & /signup) */
    .auth-shell {
      position: fixed;
      inset: 0;
      z-index: 200;
      background: radial-gradient(circle at top center, #2a2521 0%, #171717 55%, #121212 100%);
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 24px;
    }
    .auth-card {
      width: 100%;
      max-width: 420px;
      background: #212121;
      border: 1px solid var(--border-strong);
      border-radius: 20px;
      padding: 32px 28px 28px;
      box-shadow: 0 24px 64px rgba(0, 0, 0, 0.5);
    }
    .auth-brand {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 11px;
      margin-bottom: 10px;
    }
    .auth-brand-icon {
      width: 34px;
      height: 34px;
      border-radius: 10px;
      background: var(--accent-soft);
      border: 1px solid rgba(217, 119, 87, 0.35);
      color: var(--accent);
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .auth-brand-title { font-size: 26px; font-weight: 400; letter-spacing: -0.02em; color: #f5f4f0; }
    .auth-sub { text-align: center; font-size: 13.5px; color: var(--text-secondary); margin-bottom: 22px; line-height: 1.5; }
    .auth-tabs {
      display: grid;
      grid-template-columns: 1fr 1fr;
      background: #171717;
      padding: 4px;
      border-radius: 11px;
      border: 1px solid var(--border-subtle);
      margin-bottom: 20px;
    }
    .auth-tab {
      padding: 8px 12px;
      border: none;
      border-radius: 8px;
      background: transparent;
      color: var(--text-secondary);
      font-size: 13px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.15s ease;
    }
    .auth-tab.active { background: #2c2b28; color: #ffffff; box-shadow: 0 2px 8px rgba(0,0,0,0.25); }
    .auth-field { margin-bottom: 14px; }
    .auth-label { display: block; font-size: 12px; font-weight: 500; color: #c8c6c0; margin-bottom: 6px; }
    .auth-input {
      width: 100%;
      padding: 10px 13px;
      border-radius: 10px;
      background: #181818;
      border: 1px solid var(--border-strong);
      color: var(--text-primary);
      font-size: 14px;
      font-family: inherit;
      outline: none;
      transition: border-color 0.15s ease;
    }
    .auth-input:focus { border-color: var(--accent); }
    .auth-submit {
      width: 100%;
      margin-top: 6px;
      padding: 11px 16px;
      border-radius: 10px;
      border: none;
      background: var(--accent);
      color: #ffffff;
      font-size: 14px;
      font-weight: 500;
      cursor: pointer;
      transition: background 0.15s ease;
    }
    .auth-submit:hover { background: var(--accent-hover); }
    .auth-submit:disabled { opacity: 0.55; cursor: not-allowed; }
    .auth-error {
      margin-bottom: 14px;
      padding: 9px 12px;
      border-radius: 9px;
      background: rgba(239, 68, 68, 0.12);
      border: 1px solid rgba(239, 68, 68, 0.3);
      color: #fca5a5;
      font-size: 12.5px;
    }
    .auth-demo-box {
      margin-top: 18px;
      padding-top: 14px;
      border-top: 1px solid var(--border-subtle);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      font-size: 12px;
      color: var(--text-muted);
    }
    .auth-demo-btn {
      padding: 5px 10px;
      border-radius: 7px;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--border-subtle);
      color: #d4d2cd;
      font-size: 11.5px;
      cursor: pointer;
      white-space: nowrap;
    }
    .auth-demo-btn:hover { background: rgba(255, 255, 255, 0.09); color: #ffffff; }

    /* App Shell */
    .app-shell { display: flex; width: 100%; height: 100%; min-width: 0; }

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
      gap: 8px;
    }
    .user-pill { display: flex; align-items: center; gap: 10px; min-width: 0; flex: 1; }
    .avatar {
      width: 28px;
      height: 28px;
      border-radius: 50%;
      background: var(--accent);
      color: #fff;
      font-size: 11px;
      font-weight: 700;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }
    .user-name { font-size: 13px; font-weight: 500; color: var(--text-primary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .user-sub { font-size: 11px; color: var(--text-muted); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

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

    /* Welcome View (Home /) */
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

    /* Active Chat Stream (/chat/:id) */
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

    @keyframes logoThrob {
      0%, 100% { transform: scale(1); opacity: 0.82; filter: drop-shadow(0 0 0px rgba(217, 119, 87, 0)); }
      50% { transform: scale(1.16); opacity: 1; filter: drop-shadow(0 0 10px rgba(217, 119, 87, 0.72)); }
    }
    .logo-img { display: block; object-fit: contain; background: transparent; }
    .logo-throbbing { animation: logoThrob 1.25s ease-in-out infinite; }
    .live-logo { width: 22px; height: 22px; flex-shrink: 0; }

    /* Claude Interactive Question Card */
    .qcard {
      background: var(--bg-card);
      border: 1px solid rgba(255, 255, 255, 0.11);
      border-radius: 16px;
      padding: 18px 20px 16px;
      box-shadow: 0 12px 32px rgba(0, 0, 0, 0.28);
      width: 100%;
    }
    .qcard-header { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; margin-bottom: 14px; }
    .qcard-title { font-family: Georgia, Cambria, "Times New Roman", serif; font-size: 18px; font-weight: 400; color: #f2f1ed; line-height: 1.4; }
    .qcard-nav { display: flex; align-items: center; gap: 12px; font-size: 12.5px; color: #8e8c86; white-space: nowrap; padding-top: 3px; }
    .qcard-options { display: flex; flex-direction: column; }
    .qcard-option {
      display: flex; align-items: center; gap: 14px; padding: 12px 8px;
      background: transparent; border: none; border-bottom: 1px solid rgba(255, 255, 255, 0.06);
      color: #d6d5cf; font-size: 14px; text-align: left; cursor: pointer; border-radius: 8px;
      transition: background 0.14s ease, color 0.14s ease;
    }
    .qcard-option:last-child { border-bottom: none; }
    .qcard-option:hover { background: rgba(255, 255, 255, 0.05); color: #ffffff; }
    .qcard-num {
      width: 24px; height: 24px; border-radius: 6px; background: rgba(255, 255, 255, 0.07);
      border: 1px solid rgba(255, 255, 255, 0.08); color: #a8a6a1; font-size: 12px; font-weight: 500;
      display: flex; align-items: center; justify-content: center; flex-shrink: 0;
    }
    .qcard-option:hover .qcard-num { background: var(--accent-soft); border-color: rgba(217, 119, 87, 0.4); color: #f0b097; }
    .qcard-custom-row {
      margin-top: 12px; display: flex; align-items: center; gap: 10px;
      background: #1d1c1a; border: 1px solid rgba(255, 255, 255, 0.09); border-radius: 12px; padding: 7px 8px 7px 14px;
    }
    .qcard-custom-row:focus-within { border-color: rgba(255, 255, 255, 0.22); }
    .qcard-custom-input { flex: 1; background: transparent; border: none; color: var(--text-primary); font-size: 13.5px; font-family: inherit; outline: none; min-width: 0; }
    .qcard-custom-input::placeholder { color: #787671; }
    .qcard-btn-group { display: flex; align-items: center; gap: 8px; flex-shrink: 0; }
    .qcard-skip-btn {
      padding: 6px 13px; border-radius: 8px; background: transparent;
      border: 1px solid rgba(255, 255, 255, 0.14); color: #b5b3ad; font-size: 12.5px;
      font-weight: 500; cursor: pointer; transition: background 0.15s ease, color 0.15s ease, border-color 0.15s ease;
    }
    .qcard-skip-btn:hover { background: rgba(255, 255, 255, 0.08); color: #ffffff; border-color: rgba(255, 255, 255, 0.25); }
    .qcard-send-btn {
      padding: 6px 15px; border-radius: 8px; background: var(--accent);
      border: 1px solid var(--accent); color: #ffffff; font-size: 12.5px;
      font-weight: 500; cursor: pointer; display: inline-flex; align-items: center; gap: 6px;
      transition: background 0.15s ease, transform 0.1s ease, opacity 0.15s ease;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
    }
    .qcard-send-btn:hover { background: var(--accent-hover); border-color: var(--accent-hover); }
    .qcard-send-btn:active { transform: scale(0.97); }
    .qcard-send-btn:disabled, .qcard-skip-btn:disabled { opacity: 0.5; cursor: not-allowed; }

    /* Rich Human-Readable Prose */
    .prose h2 { font-size: 18px; font-weight: 600; color: #ffffff; margin: 18px 0 10px; letter-spacing: -0.01em; }
    .prose h3 { font-size: 16px; font-weight: 600; color: #f5f4f0; margin: 16px 0 8px; letter-spacing: -0.01em; }
    .prose h4 { font-size: 14.5px; font-weight: 600; color: #e2e1dc; margin: 14px 0 6px; }
    .prose p { margin: 0 0 11px; line-height: 1.68; font-size: 14.5px; color: var(--text-primary); }
    .prose p:last-child { margin-bottom: 0; }
    .prose ul, .prose ol { margin: 4px 0 12px 20px; }
    .prose li { margin-bottom: 6px; line-height: 1.6; font-size: 14.5px; color: #e2e1dc; }
    .prose strong { color: #ffffff; font-weight: 600; }
    .prose em { color: #c8c6c0; font-style: italic; }
    .prose a { color: #e89172; text-decoration: none; border-bottom: 1px solid rgba(232, 145, 114, 0.35); }
    .prose a:hover { color: #f5b49c; border-bottom-color: #f5b49c; }
    .prose hr { border: none; border-top: 1px solid rgba(255, 255, 255, 0.09); margin: 16px 0; }
    .prose blockquote {
      margin: 10px 0 14px; padding: 10px 14px; border-left: 3px solid var(--accent);
      background: rgba(217, 119, 87, 0.08); border-radius: 0 10px 10px 0; font-size: 13.5px; color: #dedcd6;
    }
    .prose table { width: 100%; border-collapse: collapse; margin: 12px 0 16px; font-size: 13px; border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; overflow: hidden; }
    .prose th { text-align: left; padding: 9px 11px; background: rgba(255,255,255,0.05); color: #f2f1ed; font-weight: 600; border-bottom: 1px solid rgba(255,255,255,0.1); }
    .prose td { padding: 8px 11px; border-bottom: 1px solid rgba(255,255,255,0.06); color: #d6d5cf; vertical-align: top; }
    .prose tr:last-child td { border-bottom: none; }
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
      max-width: 480px;
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

  <!-- AUTH VIEW (/login & /signup) — Name, Email & Password ONLY -->
  <div id="auth-view" class="auth-shell hidden">
    <div class="auth-card">
      <div class="auth-brand">
        <span class="auth-brand-icon" style="background:transparent; border:none; width:38px; height:38px;">
          <img src="/static/redtape-logo.png" alt="RedTape" class="logo-img" width="38" height="38" />
        </span>
        <span class="auth-brand-title serif">RedTape</span>
      </div>
      <div class="auth-sub">Sign in to navigate municipal & state compliance and auto-fill official government PDFs.</div>

      <div class="auth-tabs">
        <button id="tab-login" type="button" onclick="setAuthMode('login')" class="auth-tab active">Sign In</button>
        <button id="tab-signup" type="button" onclick="setAuthMode('signup')" class="auth-tab">Create Account</button>
      </div>

      <div id="auth-error" class="auth-error hidden"></div>

      <form id="auth-form" onsubmit="submitAuth(event)">
        <div id="auth-name-group" class="auth-field hidden">
          <label class="auth-label" for="auth-name">Full Name</label>
          <input id="auth-name" type="text" class="auth-input" placeholder="e.g. Tamajit Ghosh" autocomplete="name" />
        </div>
        <div class="auth-field">
          <label class="auth-label" for="auth-email">Email</label>
          <input id="auth-email" type="email" class="auth-input" placeholder="you@example.com" autocomplete="email" required />
        </div>
        <div class="auth-field">
          <label class="auth-label" for="auth-password">Password</label>
          <input id="auth-password" type="password" class="auth-input" placeholder="Enter your password" autocomplete="current-password" required />
        </div>
        <button id="auth-submit-btn" type="submit" class="auth-submit">Continue</button>
      </form>

      <div class="auth-demo-box">
        <span>Demo: <strong style="color:#d4d2cd;">tamajit@redtape.app</strong> / <strong style="color:#d4d2cd;">redtape123</strong></span>
        <button type="button" onclick="fillDemoLogin()" class="auth-demo-btn">Use Demo</button>
      </div>
    </div>
  </div>

  <!-- MAIN APP SHELL (Home / & /chat/:id) -->
  <div id="app-shell" class="app-shell hidden">
    <!-- LEFT SIDEBAR -->
    <aside id="sidebar" class="sidebar">
      <div class="sidebar-top">
        <button onclick="navigateHome()" class="brand-btn" title="Home">
          <span class="brand-icon" style="background:transparent; border:none; width:28px; height:28px;">
            <img id="sidebar-brand-logo" src="/static/redtape-logo.png" alt="RedTape" class="logo-img" width="28" height="28" />
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
        <div class="user-pill">
          <div id="sidebar-user-avatar" class="avatar">U</div>
          <div style="min-width:0;">
            <div id="sidebar-user-name" class="user-name">User</div>
            <div id="sidebar-user-email" class="user-sub">user@redtape.app</div>
          </div>
        </div>
        <button onclick="handleLogout()" title="Sign out" class="icon-btn">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/>
          </svg>
        </button>
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
          </div>
          <div class="topbar-right">
            <div class="model-switcher-wrap">
              <button id="model-pill" onclick="toggleModelDropdown(event)" class="model-pill-btn" title="Switch local Ollama model">
                <span class="ollama-dot"></span>
                <span id="active-model-name">llama3.1:8b</span>
                <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="6 9 12 15 18 9"/></svg>
              </button>
              <div id="model-dropdown" class="model-dropdown hidden"></div>
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

        <!-- HOME / WELCOME VIEW (/) -->
        <section id="welcome-view" class="welcome-view">
          <div class="welcome-inner">
            <div class="greeting-row">
              <span style="display:flex; align-items:center; justify-content:center;">
                <img src="/static/redtape-logo.png" alt="RedTape" class="logo-img" width="44" height="44" />
              </span>
              <h1 id="welcome-greeting" class="greeting-text serif">Good evening</h1>
            </div>

            <div class="composer-box">
              <textarea id="welcome-input" rows="3" placeholder="How can I help you today? (e.g. Open a bakery shop in Park Circus, Kolkata)" class="composer-textarea" onkeydown="handleComposerKeydown(event, 'welcome')"></textarea>
              <div class="composer-footer">
                <span class="model-tag" id="welcome-model-tag">RedTape · llama3.1:8b</span>
                <button onclick="sendFromComposer('welcome')" class="send-btn" title="Send">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="12" y1="19" x2="12" y2="5"/><polyline points="5 12 12 5 19 12"/>
                  </svg>
                </button>
              </div>
            </div>


          </div>
        </section>

        <!-- ACTIVE CHAT VIEW (/chat/:id) -->
        <section id="chat-view" class="chat-view hidden">
          <div id="chat-stream" class="chat-stream">
            <div id="chat-messages-inner" class="chat-inner"></div>
          </div>

          <div class="bottom-bar">
            <div class="bottom-inner">
              <div class="composer-box">
                <textarea id="chat-input" rows="2" placeholder="Reply to RedTape..." class="composer-textarea" onkeydown="handleComposerKeydown(event, 'chat')"></textarea>
                <div class="composer-footer">
                  <span class="model-tag" id="chat-model-tag">RedTape · llama3.1:8b</span>
                  <button id="chat-send-btn" onclick="sendFromComposer('chat')" class="send-btn" title="Send">
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
                      <line x1="12" y1="19" x2="12" y2="5"/><polyline points="5 12 12 5 19 12"/>
                    </svg>
                  </button>
                </div>
              </div>
              <div class="disclaimer">RedTape Navigator · Verifies official government forms and fills PDFs locally</div>
            </div>
          </div>
        </section>
      </main>

      <!-- RIGHT SLIDE-OUT ARTIFACTS PANEL -->
      <aside id="artifacts-panel" class="artifacts-panel hidden">
        <div class="artifacts-header">
          <div id="artifact-panel-title" class="artifacts-title">Official Forms</div>
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
  </div>

  <script>
    let currentUser = null;
    let authMode = 'login';
    let appState = null;
    let isBusy = false;
    let activePdfIndex = 0;

    function pushRoute(path) {
      if (window.location.pathname !== path) {
        window.history.pushState({}, '', path);
      }
    }

    function getChatIdFromPath() {
      const m = window.location.pathname.match(/^\/chat\/([^/]+)$/);
      return m ? decodeURIComponent(m[1]) : null;
    }

    function getInitials(name) {
      const parts = String(name || 'U').trim().split(/\s+/);
      if (parts.length >= 2) return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
      return String(name || 'U').slice(0, 2).toUpperCase();
    }

    function setTimeGreeting() {
      const hr = new Date().getHours();
      const greet = hr < 12 ? 'Good morning' : hr < 17 ? 'Good afternoon' : 'Good evening';
      const first = currentUser?.name ? `, ${currentUser.name.split(' ')[0]}` : '';
      const el = document.getElementById('welcome-greeting');
      if (el) el.textContent = greet + first;
    }

    function updateUserChrome(user) {
      currentUser = user;
      if (!user) return;
      document.getElementById('sidebar-user-avatar').textContent = getInitials(user.name);
      document.getElementById('sidebar-user-name').textContent = user.name || 'User';
      document.getElementById('sidebar-user-email').textContent = user.email || '';
      setTimeGreeting();
    }

    function showAuthScreen(mode = 'login', updateUrl = true) {
      document.getElementById('auth-view').classList.remove('hidden');
      document.getElementById('app-shell').classList.add('hidden');
      setAuthMode(mode, updateUrl);
    }

    function showAppShell() {
      document.getElementById('auth-view').classList.add('hidden');
      document.getElementById('app-shell').classList.remove('hidden');
    }

    function setAuthMode(mode, updateUrl = true) {
      authMode = mode === 'signup' ? 'signup' : 'login';
      document.getElementById('tab-login').classList.toggle('active', authMode === 'login');
      document.getElementById('tab-signup').classList.toggle('active', authMode === 'signup');
      document.getElementById('auth-name-group').classList.toggle('hidden', authMode !== 'signup');
      document.getElementById('auth-submit-btn').textContent = authMode === 'signup' ? 'Create Account' : 'Sign In';
      const errBox = document.getElementById('auth-error');
      errBox.classList.add('hidden');
      errBox.textContent = '';
      if (updateUrl) pushRoute(authMode === 'signup' ? '/signup' : '/login');
    }

    function fillDemoLogin() {
      setAuthMode('login', false);
      document.getElementById('auth-email').value = 'tamajit@redtape.app';
      document.getElementById('auth-password').value = 'redtape123';
    }

    async function submitAuth(e) {
      e.preventDefault();
      const errBox = document.getElementById('auth-error');
      const btn = document.getElementById('auth-submit-btn');
      errBox.classList.add('hidden');
      btn.disabled = true;

      const email = document.getElementById('auth-email').value.trim();
      const password = document.getElementById('auth-password').value;
      const name = document.getElementById('auth-name').value.trim();

      const url = authMode === 'signup' ? '/api/auth/signup' : '/api/auth/login';
      const body = authMode === 'signup' ? { name, email, password } : { email, password };

      try {
        const res = await fetch(url, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
        });
        const data = await res.json();
        if (!res.ok || !data.authenticated) {
          errBox.textContent = data.error || 'Authentication failed. Please check your details.';
          errBox.classList.remove('hidden');
          return;
        }
        updateUserChrome(data.user);
        showAppShell();
        pushRoute('/');
        await bootWorkspace();
      } catch (err) {
        errBox.textContent = 'Could not reach the server. Please try again.';
        errBox.classList.remove('hidden');
      } finally {
        btn.disabled = false;
      }
    }

    async function handleLogout() {
      try {
        await fetch('/api/auth/logout', { method: 'POST' });
      } catch (e) {}
      currentUser = null;
      appState = null;
      showAuthScreen('login', true);
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

    function formatInlineMd(str) {
      let s = escapeHtml(str);
      s = s.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>');
      s = s.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
      s = s.replace(/\*([^*]+)\*/g, '<em>$1</em>');
      s = s.replace(/`([^`]+)`/g, '<code>$1</code>');
      return s;
    }

    function renderMarkdown(md) {
      if (!md) return '';
      const lines = md.split('\n');
      let html = '';
      let inUl = false, inOl = false, inQuote = false, inTable = false;

      const closeAll = () => {
        if (inUl) { html += '</ul>'; inUl = false; }
        if (inOl) { html += '</ol>'; inOl = false; }
        if (inQuote) { html += '</blockquote>'; inQuote = false; }
        if (inTable) { html += '</tbody></table>'; inTable = false; }
      };

      for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();
        if (!line) { closeAll(); continue; }

        if (/^---+$/.test(line)) { closeAll(); html += '<hr />'; continue; }

        if (line.startsWith('|') && line.endsWith('|')) {
          if (inUl) { html += '</ul>'; inUl = false; }
          if (inOl) { html += '</ol>'; inOl = false; }
          if (inQuote) { html += '</blockquote>'; inQuote = false; }
          const cells = line.slice(1, -1).split('|').map(c => c.trim());
          if (cells.every(c => /^:?-{2,}:?$/.test(c))) continue;
          if (!inTable) {
            html += '<table><thead><tr>' + cells.map(c => `<th>${formatInlineMd(c)}</th>`).join('') + '</tr></thead><tbody>';
            inTable = true;
          } else {
            html += '<tr>' + cells.map(c => `<td>${formatInlineMd(c)}</td>`).join('') + '</tr>';
          }
          continue;
        } else if (inTable) {
          html += '</tbody></table>'; inTable = false;
        }

        if (line.startsWith('>')) {
          if (inUl) { html += '</ul>'; inUl = false; }
          if (inOl) { html += '</ol>'; inOl = false; }
          let qtxt = line.replace(/^>+\s*/, '').replace(/^\[!(NOTE|TIP|IMPORTANT|WARNING)\]\s*/i, '');
          if (!qtxt) continue;
          if (!inQuote) { html += '<blockquote>'; inQuote = true; }
          else { html += '<br />'; }
          html += formatInlineMd(qtxt);
          continue;
        } else if (inQuote) {
          html += '</blockquote>'; inQuote = false;
        }

        const hm = line.match(/^(#{2,4})\s+(.+)$/);
        if (hm) {
          closeAll();
          const lvl = hm[1].length;
          html += `<h${lvl}>${formatInlineMd(hm[2])}</h${lvl}>`;
          continue;
        }

        if (line.startsWith('- ') || line.startsWith('• ') || line.startsWith('* ')) {
          if (inOl) { html += '</ol>'; inOl = false; }
          if (!inUl) { html += '<ul>'; inUl = true; }
          html += `<li>${formatInlineMd(line.slice(2))}</li>`;
          continue;
        }

        const olm = line.match(/^\d+\.\s+(.+)$/);
        if (olm) {
          if (inUl) { html += '</ul>'; inUl = false; }
          if (!inOl) { html += '<ol>'; inOl = true; }
          html += `<li>${formatInlineMd(olm[1])}</li>`;
          continue;
        }

        closeAll();
        html += `<p>${formatInlineMd(line)}</p>`;
      }
      closeAll();
      return html;
    }

    function sendQCardCustom(inputId) {
      if (isBusy) return;
      const el = document.getElementById(inputId);
      const val = (el?.value || '').trim();
      if (!val) {
        if (el) {
          el.focus();
          el.placeholder = 'Please type your answer here...';
        }
        return;
      }
      sendMessage(val);
    }

    function handleQCardKeydown(e, inputId) {
      if (e.key === 'Enter') {
        e.preventDefault();
        sendQCardCustom(inputId);
      }
    }
    function selectQCardOption(text) { if (!isBusy) sendMessage(text); }
    function skipQCard() { if (!isBusy) sendMessage('__SKIP__'); }

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
      const sbLogo = document.getElementById('sidebar-brand-logo');
      if (sbLogo) sbLogo.classList.add('logo-throbbing');
      showChatMode();
      const container = document.getElementById('chat-messages-inner');
      const streamEl = document.getElementById('chat-stream');

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
        <div style="display:inline-flex; align-items:center; gap:9px; font-size:13px; color:#a8a6a1;">
          <img src="/static/redtape-logo.png" alt="RedTape" class="logo-img live-logo logo-throbbing" />
          <span id="${liveId}-label">Researching statutory requirements...</span>
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
          await sleep(280);
        }

        liveDiv.remove();
        if (data.state) {
          appState = data.state;
          if (appState.session_id) {
            pushRoute(`/chat/${encodeURIComponent(appState.session_id)}`);
          }
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
        if (sbLogo) sbLogo.classList.remove('logo-throbbing');
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

          // Claude Interactive Question Card (shown on latest active interview step)
          let qcardHtml = '';
          const isLast = idx === history.length - 1;
          const turn = msg.interview_turn;
          if (isLast && turn && !turn.complete && turn.question) {
            const opts = turn.options || turn.quick_replies || [];
            const optsHtml = opts.map((opt, i) => `
              <button onclick='selectQCardOption(${JSON.stringify(opt)})' class="qcard-option">
                <span class="qcard-num">${i + 1}</span>
                <span>${escapeHtml(opt)}</span>
              </button>
            `).join('');
            const inputId = `qcard-custom-${idx}`;
            qcardHtml = `
              <div class="qcard">
                <div class="qcard-header">
                  <div class="qcard-title">${escapeHtml(turn.question)}</div>
                  <div class="qcard-nav">
                    <span>‹</span>
                    <span>${turn.step || 1} of ${turn.total_steps || 4}</span>
                    <span>›</span>
                    <button onclick="skipQCard()" title="Skip" style="background:none;border:none;color:#8e8c86;cursor:pointer;font-size:15px;line-height:1;">✕</button>
                  </div>
                </div>
                <div class="qcard-options">${optsHtml}</div>
                <div class="qcard-custom-row">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#8e8c86" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink:0;">
                    <path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/>
                  </svg>
                  <input id="${inputId}" type="text" class="qcard-custom-input" placeholder="${escapeHtml(turn.custom_placeholder || 'Something else')}" onkeydown="handleQCardKeydown(event, '${inputId}')" />
                  <div class="qcard-btn-group">
                    <button onclick="skipQCard()" class="qcard-skip-btn" title="Skip this field">Skip</button>
                    <button onclick="sendQCardCustom('${inputId}')" class="qcard-send-btn" title="Send answer">
                      <span>Send</span>
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
                        <line x1="22" y1="2" x2="11" y2="13"></line>
                        <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            `;
          }

          // Inline Artifact Card
          let artifactCardHtml = '';
          if (msg.has_artifacts && state.form_artifacts && state.form_artifacts.length > 0) {
            const pdfCount = state.form_artifacts.length;
            const officialCount = state.form_artifacts.filter(f => f.is_official_pdf).length;
            const portalCount = (state.portal_artifacts || []).length;
            const subText = officialCount > 0
              ? `${officialCount} Official Govt PDFs Filled · ${pdfCount} Total PDFs · ${portalCount} Portal Packs`
              : `${pdfCount} Filled PDFs · ${portalCount} Portal Packs · Click to Inspect`;
            artifactCardHtml = `
              <div onclick="openArtifactsPanel('pdfs')" class="artifact-card">
                <div class="artifact-card-left">
                  <div class="artifact-card-icon">PDF</div>
                  <div style="min-width:0;">
                    <div class="artifact-card-title">${escapeHtml(state.applicant_profile?.entity_name || state.title)} — Official Forms</div>
                    <div class="artifact-card-sub">${subText}</div>
                  </div>
                </div>
                <span style="color:#787671;">›</span>
              </div>
            `;
          }

          div.innerHTML = `${thoughtHtml}${proseHtml}${qcardHtml}${artifactCardHtml}`;
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
        (state.applicant_profile?.entity_name || state.title || 'Official Forms') + ' · Artifacts';

      const selBar = document.getElementById('pdf-selector-bar');
      selBar.innerHTML = '';
      if (pdfs.length > 0) {
        if (activePdfIndex >= pdfs.length) activePdfIndex = 0;
        pdfs.forEach((fa, i) => {
          const btn = document.createElement('button');
          btn.className = 'pdf-pill' + (i === activePdfIndex ? ' active' : '');
          const badge = fa.is_official_pdf ? '🏛 ' : '';
          btn.textContent = badge + fa.form_name.replace('.pdf', '').replace(/_/g, ' ');
          btn.onclick = () => { activePdfIndex = i; renderArtifactsData(appState); };
          selBar.appendChild(btn);
        });

        const cur = pdfs[activePdfIndex];
        const rawPath = cur.pdf_path || cur.file_path || '';
        const relUrl = rawPath.includes('drafts/') ? '/drafts/' + rawPath.split('drafts/')[1] : '/' + rawPath;
        const kindLabel = cur.is_official_pdf ? 'Official Govt PDF' : 'AcroForm Draft';
        document.getElementById('pdf-meta-status').textContent = `${cur.form_name} · ${kindLabel} · ${cur.completion_percentage || 0}% filled`;
        document.getElementById('pdf-download-link').href = relUrl;
        document.getElementById('pdf-preview-obj').data = relUrl + '?t=' + Date.now();
      } else {
        selBar.innerHTML = '<span style="font-size:12px; color:#787671;">Complete the interview to fill official PDFs.</span>';
      }

      document.getElementById('review-md-content').textContent =
        state.review_md || 'Complete the interview to generate your regulatory review summary.';

      const portalsList = document.getElementById('portals-list');
      portalsList.innerHTML = '';
      if (portals.length === 0) {
        portalsList.innerHTML = '<div style="font-size:13px; color:#787671;">No portal packs generated yet.</div>';
      } else {
        portals.forEach(pa => {
          const mdRel = pa.copy_sheet_path && pa.copy_sheet_path.includes('drafts/')
            ? '/drafts/' + pa.copy_sheet_path.split('drafts/')[1]
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
        const activeId = appState?.session_id || getChatIdFromPath();
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

    async function openSession(id, updateUrl = true) {
      try {
        const res = await fetch(`/api/session/${encodeURIComponent(id)}`);
        if (!res.ok) return;
        appState = await res.json();
        activePdfIndex = 0;
        if (updateUrl) pushRoute(`/chat/${encodeURIComponent(id)}`);
        document.getElementById('chat-messages-inner').innerHTML = '';
        renderApp(appState);
        loadSessions();
      } catch (e) { console.error(e); }
    }

    function navigateHome() {
      startNewChat();
    }

    async function startNewChat(updateUrl = true) {
      try {
        const res = await fetch('/api/new_chat', { method: 'POST' });
        appState = await res.json();
        activePdfIndex = 0;
        if (updateUrl) pushRoute('/');
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
          pushRoute('/');
          showWelcomeMode();
        }
        loadSessions();
      } catch (e) { console.error(e); }
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

    function populateModelDropdown(models, activeModel) {
      const dd = document.getElementById('model-dropdown');
      if (!dd) return;
      if (!models || models.length === 0) {
        models = ['llama3.1:8b', 'llama3.2:3b'];
      }
      dd.innerHTML = models.map(m => {
        const isActive = m === activeModel;
        const tag = m.includes('8b') ? '<span class="model-rec-tag">Recommended</span>' : (m.includes('3b') ? '<span class="model-fast-tag">Fast</span>' : '');
        const desc = m.includes('8b')
          ? 'Deep legal & compliance reasoning on local Ollama'
          : (m.includes('3b') ? 'Fast token generation for rapid consultation' : 'Local Ollama endpoint model');
        return `
          <div class="model-option ${isActive ? 'active' : ''}" onclick="switchModel('${m}')">
            <div class="model-opt-title">
              <span>${m}</span>
              ${tag}
            </div>
            <div class="model-opt-sub">${desc}</div>
          </div>
        `;
      }).join('');
    }

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

    function updateModelUI(modelName) {
      const pillName = document.getElementById('active-model-name');
      if (pillName) pillName.textContent = modelName;
      const wTag = document.getElementById('welcome-model-tag');
      if (wTag) wTag.textContent = `RedTape · ${modelName}`;
      const cTag = document.getElementById('chat-model-tag');
      if (cTag) cTag.textContent = `RedTape · ${modelName}`;

      const dd = document.getElementById('model-dropdown');
      if (dd && dd.children.length > 0) {
        Array.from(dd.children).forEach(el => {
          const titleSpan = el.querySelector('.model-opt-title span');
          if (titleSpan && titleSpan.textContent.trim() === modelName) {
            el.classList.add('active');
          } else {
            el.classList.remove('active');
          }
        });
      }
    }

    async function bootWorkspace() {
      setTimeGreeting();
      const chatId = getChatIdFromPath();
      const [mRes] = await Promise.all([
        fetch('/api/model').catch(() => null),
        loadSessions(),
      ]);
      if (mRes && mRes.ok) {
        const mData = await mRes.json();
        if (mData.available_models) populateModelDropdown(mData.available_models, mData.active_model);
        if (mData.active_model) updateModelUI(mData.active_model);
      }
      if (chatId) {
        await openSession(chatId, false);
      } else {
        appState = null;
        showWelcomeMode();
      }
    }

    async function syncRoute() {
      const path = window.location.pathname;
      if (!currentUser) {
        showAuthScreen(path === '/signup' ? 'signup' : 'login', false);
        return;
      }
      if (path === '/login' || path === '/signup') {
        showAppShell();
        pushRoute('/');
        appState = null;
        showWelcomeMode();
        return;
      }
      showAppShell();
      const chatId = getChatIdFromPath();
      if (chatId) {
        await openSession(chatId, false);
      } else {
        appState = null;
        showWelcomeMode();
        loadSessions();
      }
    }

    async function init() {
      try {
        const res = await fetch('/api/auth/me');
        const data = await res.json();
        const path = window.location.pathname;
        if (data && data.authenticated && data.user) {
          updateUserChrome(data.user);
          showAppShell();
          if (path === '/login' || path === '/signup') {
            pushRoute('/');
          }
          await bootWorkspace();
        } else {
          showAuthScreen(path === '/signup' ? 'signup' : 'login', path !== '/login' && path !== '/signup');
        }
      } catch (e) {
        console.error(e);
        showAuthScreen('login', false);
      }
    }

    window.addEventListener('popstate', syncRoute);
    window.addEventListener('DOMContentLoaded', init);
  </script>
</body>
</html>
"""

INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Ruhvaan AI | Ultimate</title>
    <meta name="api-base" content="">
    
    <!-- External Libraries -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@200;300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css">

    <style>
        /* --- CORE VARIABLES --- */
        :root {
            --bg-deep: #000000;
            --bg-panel: #09090b;
            --bg-chat: #050505;
            --primary: #3b82f6;      /* Electric Blue */
            --primary-dim: rgba(59, 130, 246, 0.1);
            --primary-glow: rgba(59, 130, 246, 0.6);
            --accent: #8b5cf6;       /* Violet */
            --text-main: #ffffff;
            --text-muted: #94a3b8;
            --border: rgba(255, 255, 255, 0.08);
            --success: #10b981;
            --chat-padding-inline: clamp(24px, 10vw, 180px);
            
            --shadow-sm: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            --shadow-lg: 0 20px 25px -5px rgba(0, 0, 0, 0.5);
            --font-main: 'Outfit', sans-serif;
            --font-code: 'JetBrains Mono', monospace;
        }

        /* --- GLOBAL RESET --- */
        * { box-sizing: border-box; margin: 0; padding: 0; outline: none; -webkit-tap-highlight-color: transparent; }
        
        body {
            background: radial-gradient(circle at 20% 0%, rgba(59, 130, 246, 0.16), transparent 40%),
                radial-gradient(circle at 80% 20%, rgba(139, 92, 246, 0.12), transparent 45%),
                var(--bg-deep);
            color: var(--text-main);
            font-family: var(--font-main);
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 24px;
            overflow: hidden;
            font-size: 16px;
        }

        .app-shell {
            width: min(1400px, 100%);
            height: calc(100vh - 48px);
            display: flex;
            background: rgba(2, 2, 8, 0.88);
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 20px;
            box-shadow: 0 30px 60px rgba(0, 0, 0, 0.55);
            overflow: hidden;
            position: relative;
        }
        .app-shell::after {
            content: '';
            position: absolute;
            inset: 0;
            border-radius: 20px;
            border: 1px solid rgba(59, 130, 246, 0.18);
            box-shadow: inset 0 0 40px rgba(59, 130, 246, 0.12);
            pointer-events: none;
        }

        /* Scrollbar Styling */
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: var(--bg-panel); }
        ::-webkit-scrollbar-thumb { background: #333; border-radius: 10px; }
        ::-webkit-scrollbar-thumb:hover { background: var(--primary); }

        /* --- 3D LOGO ENGINE --- */
        .scene {
            width: 50px; height: 50px;
            perspective: 600px;
            margin: 0 auto 25px auto;
        }
        .cube {
            width: 100%; height: 100%;
            position: relative;
            transform-style: preserve-3d;
            animation: rotateCube 10s infinite linear;
        }
        .cube-face {
            position: absolute; width: 50px; height: 50px;
            border: 2px solid var(--primary);
            background: rgba(59, 130, 246, 0.15);
            box-shadow: 0 0 15px var(--primary-dim);
            backface-visibility: visible;
        }
        .cube-face.front  { transform: rotateY(0deg) translateZ(25px); }
        .cube-face.back   { transform: rotateY(180deg) translateZ(25px); }
        .cube-face.right  { transform: rotateY(90deg) translateZ(25px); }
        .cube-face.left   { transform: rotateY(-90deg) translateZ(25px); }
        .cube-face.top    { transform: rotateX(90deg) translateZ(25px); }
        .cube-face.bottom { transform: rotateX(-90deg) translateZ(25px); }
        
        @keyframes rotateCube { 
            0% { transform: rotateX(-20deg) rotateY(0deg); } 
            100% { transform: rotateX(-20deg) rotateY(360deg); } 
        }

        /* --- SIDEBAR --- */
        .sidebar {
            width: 300px;
            background: var(--bg-panel);
            border-right: 1px solid var(--border);
            display: flex; flex-direction: column;
            padding: 24px;
            z-index: 50;
            transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .brand-section { text-align: center; margin-bottom: 30px; }
        .brand-name { 
            font-size: 22px; font-weight: 800; letter-spacing: 1px;
            background: linear-gradient(135deg, #fff 0%, var(--primary) 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }

        .action-btn {
            background: var(--primary); color: #fff;
            border: none; padding: 14px; border-radius: 12px;
            font-weight: 600; cursor: pointer; 
            display: flex; align-items: center; justify-content: center; gap: 10px;
            transition: all 0.2s; position: relative; overflow: hidden;
            box-shadow: 0 4px 15px var(--primary-glow);
        }
        .action-btn:hover { transform: translateY(-2px); box-shadow: 0 8px 25px var(--primary-glow); }
        .action-btn:active { transform: scale(0.98); }
        .mobile-back-btn {
            display: none;
            margin-bottom: 16px;
            background: rgba(255,255,255,0.05);
            border: 1px solid var(--border);
            color: #fff;
            padding: 10px 12px;
            border-radius: 10px;
            font-size: 14px;
            cursor: pointer;
            align-items: center;
            gap: 8px;
        }

        /* animated ripple for actions */
        .action-btn.animating::after {
            content: '';
            position: absolute;
            left: 50%; top: 50%;
            width: 8px; height: 8px;
            background: rgba(255,255,255,0.15);
            border-radius: 50%;
            transform: translate(-50%,-50%) scale(1);
            animation: ripple 800ms ease-out forwards;
            pointer-events: none;
        }
        @keyframes ripple {
            0% { transform: translate(-50%,-50%) scale(1); opacity: 1; }
            100% { transform: translate(-50%,-50%) scale(18); opacity: 0; }
        }

        .menu-list { flex: 1; margin-top: 30px; overflow-y: auto; }
        .menu-item {
            padding: 12px 16px; border-radius: 10px;
            color: var(--text-muted); cursor: pointer;
            display: flex; align-items: center; gap: 12px;
            transition: 0.2s; font-size: 15px; margin-bottom: 5px;
            position: relative;
        }
        .menu-item:hover { background: rgba(255,255,255,0.05); color: #fff; }
        .menu-item.active { background: var(--primary-dim); color: var(--primary); border: 1px solid rgba(59,130,246,0.2); }
        .coming-soon {
            margin-left: auto;
            padding: 2px 8px;
            font-size: 10px;
            letter-spacing: 0.4px;
            text-transform: uppercase;
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid rgba(255, 255, 255, 0.12);
            color: var(--text-muted);
        }

        /* temporary animated indicator inside menu item */
        .menu-item .module-anim {
            width: 12px; height: 12px; border-radius: 50%;
            background: linear-gradient(90deg, var(--primary), var(--accent));
            box-shadow: 0 0 8px rgba(59,130,246,0.6);
            margin-left: auto;
            transform: scale(0);
            animation: moduleBounce 1000ms ease-out forwards;
        }
        @keyframes moduleBounce {
            0% { transform: scale(0); opacity: 0; }
            30% { transform: scale(1.2); opacity: 1; }
            60% { transform: scale(0.9); }
            100% { transform: scale(1); opacity: 1; }
        }

        .user-menu {
            position: relative;
        }
        .user-menu-btn {
            display: flex;
            align-items: center;
            gap: 8px;
            background: rgba(255,255,255,0.04);
            border: 1px solid var(--border);
            color: #fff;
            padding: 8px 12px;
            border-radius: 12px;
            cursor: pointer;
        }
        .user-menu-btn img {
            width: 26px;
            height: 26px;
            border-radius: 50%;
            object-fit: cover;
            border: 1px solid rgba(255,255,255,0.2);
        }
        .user-menu-dropdown {
            position: absolute;
            right: 0;
            top: 46px;
            min-width: 220px;
            background: #121218;
            border: 1px solid var(--border);
            border-radius: 12px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.5);
            display: none;
            flex-direction: column;
            z-index: 90;
            padding: 8px;
        }
        .user-menu-dropdown.active { display: flex; }
        .user-menu-item {
            padding: 10px 12px;
            border-radius: 10px;
            color: #fff;
            display: flex;
            align-items: center;
            gap: 10px;
            cursor: pointer;
            font-size: 14px;
        }
        .user-menu-item:hover { background: rgba(255,255,255,0.05); }
        .user-menu-divider {
            height: 1px;
            background: var(--border);
            margin: 6px 0;
        }
        .profile-avatar {
            width: 72px;
            height: 72px;
            border-radius: 50%;
            object-fit: cover;
            border: 2px solid rgba(255,255,255,0.2);
            margin: 0 auto 12px;
            display: block;
        }
        .profile-upload {
            text-align: center;
            margin-bottom: 12px;
        }
        .profile-upload label {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            cursor: pointer;
            font-size: 13px;
            color: var(--primary);
        }
        .profile-actions {
            display: flex;
            gap: 10px;
            margin-top: 8px;
        }
        .profile-actions button {
            flex: 1;
            border-radius: 10px;
            padding: 10px 12px;
            border: none;
            cursor: pointer;
            font-weight: 600;
        }

        .tg-card {
            margin-top: 20px; padding: 16px; 
            background: linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01));
            border: 1px solid var(--border); border-radius: 16px;
            text-align: center;
        }
        .tg-link {
            display: block; margin-top: 12px; padding: 10px;
            background: #229ED9; color: white; border-radius: 8px;
            text-decoration: none; font-weight: 600; font-size: 14px;
            transition: 0.2s;
        }
        .tg-link:hover { transform: scale(1.05); box-shadow: 0 0 15px rgba(34, 158, 217, 0.4); }

        /* --- MAIN INTERFACE --- */
        .main-wrapper {
            flex: 1; display: flex; flex-direction: column;
            background: radial-gradient(circle at 50% -20%, #0f172a 0%, #000000 60%);
            position: relative;
        }

        .header {
            height: 70px; display: flex; align-items: center; justify-content: space-between;
            padding: 0 30px; border-bottom: 1px solid var(--border);
            background: rgba(0,0,0,0.7); backdrop-filter: blur(20px);
            z-index: 40;
        }
        .header-title { font-weight: 700; font-size: 18px; letter-spacing: 0.5px; }
        .status-badge {
            font-size: 12px; color: var(--success); font-weight: 600;
            display: flex; align-items: center; gap: 6px;
            background: rgba(16, 185, 129, 0.1); padding: 5px 12px; border-radius: 20px;
            border: 1px solid rgba(16, 185, 129, 0.2);
        }
        .auth-pill {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 12px;
            padding: 6px 10px;
            border-radius: 999px;
            border: 1px solid var(--border);
            background: rgba(255, 255, 255, 0.04);
            color: var(--text-muted);
            cursor: pointer;
        }
        .auth-pill strong { color: #fff; font-weight: 600; }
        .status-dot { width: 6px; height: 6px; background: var(--success); border-radius: 50%; box-shadow: 0 0 8px var(--success); }

        /* Chat Area */
        .chat-container {
            flex: 1; overflow-y: auto; padding: 40px var(--chat-padding-inline);
            display: flex; flex-direction: column; gap: 24px;
            scroll-behavior: auto; /* Managed by JS for smooth scroll */
            position: relative;
        }
        
        .msg-row { display: flex; gap: 16px; opacity: 0; animation: fadeIn 0.4s forwards; }
        .msg-row.user { flex-direction: row-reverse; }
        
        @keyframes fadeIn { to { opacity: 1; } }

        .avatar {
            width: 38px; height: 38px; border-radius: 12px; flex-shrink: 0;
            display: flex; align-items: center; justify-content: center;
            font-size: 18px; box-shadow: var(--shadow-sm);
        }
        .bot .avatar { background: #18181b; border: 1px solid var(--border); color: var(--primary); }
        .user .avatar { background: var(--primary); color: #fff; box-shadow: 0 0 15px var(--primary-glow); }

        .bubble {
            max-width: 85%; padding: 16px 22px; border-radius: 20px;
            font-size: 16px; line-height: 1.7; position: relative;
            box-shadow: var(--shadow-sm); transition: transform 0.2s;
        }
        .bot .bubble { 
            background: rgba(255,255,255,0.03); 
            border: 1px solid var(--border); 
            border-top-left-radius: 4px;
        }
        .user .bubble { 
            background: linear-gradient(135deg, var(--primary), var(--accent)); 
            color: #fff; 
            border-top-right-radius: 4px;
        }

        /* Code Block Enhancement */
        pre {
            background: #1e1e1e !important;
            padding: 15px; border-radius: 10px;
            overflow-x: auto; margin: 10px 0;
            border: 1px solid #333; font-family: var(--font-code);
            font-size: 14px; position: relative;
        }
        code { font-family: var(--font-code); }

        /* Input Area */
        .input-section {
            padding: 30px; 
            background: linear-gradient(to top, #000 40%, transparent);
            display: flex; justify-content: center;
        }
        
        .input-wrapper {
            width: 100%; max-width: 900px;
            background: rgba(20,20,25,0.9); border: 1px solid var(--border);
            border-radius: 16px; padding: 10px;
            display: flex; align-items: flex-end; gap: 12px;
            box-shadow: var(--shadow-lg); transition: 0.3s;
            backdrop-filter: blur(10px);
        }
        .upload-btn {
            width: 44px; height: 44px; border-radius: 12px;
            border: 1px solid var(--border);
            background: rgba(255,255,255,0.04);
            color: #fff; cursor: pointer;
            display: flex; align-items: center; justify-content: center;
            transition: 0.2s;
        }
        .upload-btn:hover { border-color: var(--primary); color: var(--primary); }
        .upload-btn:disabled { opacity: 0.5; cursor: not-allowed; }
        .input-wrapper:focus-within {
            border-color: var(--primary);
            box-shadow: 0 0 30px rgba(59, 130, 246, 0.15);
        }

        textarea {
            flex: 1; background: transparent; border: none; color: #fff;
            font-size: 16px; padding: 12px; resize: none;
            max-height: 200px; height: 50px; font-family: var(--font-main);
        }
        textarea::placeholder { color: #555; }

        .send-btn {
            width: 50px; height: 50px; border-radius: 12px;
            border: none; background: var(--text-main); color: #000;
            font-size: 20px; cursor: pointer; transition: 0.3s;
            display: flex; align-items: center; justify-content: center;
            flex-shrink: 0;
        }
        .send-btn:hover { background: var(--primary); color: #fff; transform: scale(1.1) rotate(-10deg); }
        .send-btn:disabled { opacity: 0.5; cursor: not-allowed; transform: none; background: #333; color: #555; }

        .modal-overlay {
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.7);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 80;
            padding: 20px;
        }
        .modal-overlay.active { display: flex; }
        .modal {
            width: min(420px, 100%);
            background: #0b0b10;
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 22px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.5);
        }
        .modal-title { display: flex; align-items: center; justify-content: space-between; }
        .modal h3 { margin-bottom: 8px; }
        .modal p { color: var(--text-muted); font-size: 14px; margin-bottom: 16px; }
        .modal-close {
            border: none;
            background: transparent;
            color: var(--text-muted);
            font-size: 16px;
            cursor: pointer;
            padding: 4px;
            line-height: 1;
        }
        .modal-close:hover { color: #fff; }
        .modal input {
            width: 100%;
            background: rgba(255,255,255,0.04);
            border: 1px solid var(--border);
            color: #fff;
            padding: 10px 12px;
            border-radius: 10px;
            margin-bottom: 10px;
        }
        .password-field {
            position: relative;
        }
        .password-toggle {
            position: absolute;
            right: 10px;
            top: 50%;
            transform: translateY(-50%);
            border: none;
            background: transparent;
            color: var(--text-muted);
            cursor: pointer;
            font-size: 14px;
        }
        .modal-actions {
            display: flex;
            gap: 10px;
            margin-top: 8px;
        }
        .modal-actions button {
            flex: 1;
            border-radius: 10px;
            padding: 10px 12px;
            border: none;
            cursor: pointer;
            font-weight: 600;
        }
        .modal-actions .primary { background: var(--primary); color: #fff; }
        .modal-actions .secondary { background: rgba(255,255,255,0.06); color: #fff; border: 1px solid var(--border); }
        .modal-link {
            margin-top: 12px;
            text-align: center;
            font-size: 13px;
            color: var(--text-muted);
        }
        .modal-link button {
            background: transparent;
            border: none;
            color: var(--primary);
            cursor: pointer;
            font-weight: 600;
        }
        .modal-switch {
            margin-top: 12px;
            text-align: center;
            font-size: 13px;
            color: var(--text-muted);
        }
        .modal-switch button {
            background: transparent;
            border: none;
            color: var(--primary);
            cursor: pointer;
            font-weight: 600;
        }
        .plans-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-top: 16px;
        }
        .plan-card {
            background: rgba(255,255,255,0.03);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 16px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.5);
            transform: perspective(700px) rotateX(4deg);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .plan-card:hover {
            transform: perspective(700px) rotateX(0deg) translateY(-4px);
            box-shadow: 0 30px 50px rgba(0,0,0,0.6);
        }
        .plan-card h4 { margin-bottom: 8px; }
        .plan-price { font-size: 22px; font-weight: 700; margin-bottom: 8px; }
        .plan-benefits { font-size: 13px; color: var(--text-muted); line-height: 1.6; }
        .feature-stack {
            margin-top: 20px;
            padding: 16px;
            border-radius: 16px;
            border: 1px solid var(--border);
            background: rgba(255,255,255,0.02);
        }
        .feature-group { margin-bottom: 16px; }
        .feature-group:last-child { margin-bottom: 0; }
        .feature-group h4 {
            margin-bottom: 8px;
            font-size: 15px;
            letter-spacing: 0.2px;
        }
        .feature-list {
            list-style: none;
            display: grid;
            gap: 8px;
            font-size: 13px;
            color: var(--text-muted);
        }
        .feature-list li {
            display: flex;
            gap: 8px;
        }
        .feature-list li::before {
            content: "•";
            color: var(--primary);
        }
        .feature-note {
            margin-top: 12px;
            font-size: 12px;
            color: var(--text-muted);
        }
        .feature-note strong { color: #fff; }
        /* Mascot (small character inside chatbox) */
        .mascot {
            position: absolute;
            left: calc(var(--chat-padding-inline) - 8px);
            bottom: 36px;
            width: 46px; height: 46px;
            background: linear-gradient(180deg, #2b2b2f, #111);
            border-radius: 12px;
            border: 1px solid var(--border);
            display: flex; align-items: center; justify-content: center;
            box-shadow: 0 6px 18px rgba(0,0,0,0.6), 0 0 8px rgba(59,130,246,0.08);
            cursor: pointer;
            z-index: 30;
            transition: transform 250ms ease;
        }
        .mascot .eyes {
            width: 20px; height: 10px; display: flex; gap: 6px; align-items: center;
        }
        .mascot .eyes span {
            width: 6px; height: 6px; background: #fff; border-radius: 50%;
            display: inline-block; transform-origin: center;
        }
        .mascot.bounce { animation: mascotBounce 900ms ease; }
        @keyframes mascotBounce {
            0% { transform: translateY(0) scale(1); }
            30% { transform: translateY(-8px) scale(1.05); }
            60% { transform: translateY(0) scale(0.98); }
            100% { transform: translateY(0) scale(1); }
        }
        .mascot .tooltip {
            position: absolute;
            bottom: 56px; left: 50%; transform: translateX(-50%);
            background: rgba(255,255,255,0.05); color: #fff;
            font-size: 12px; padding: 6px 8px; border-radius: 10px;
            border: 1px solid var(--border); white-space: nowrap;
            opacity: 0; pointer-events: none; transition: opacity 180ms;
        }
        .mascot.show-tooltip .tooltip { opacity: 1; }

        /* Mobile Responsive */
        @media (max-width: 850px) {
            body { padding: 0; }
            .app-shell { width: 100%; height: 100vh; border-radius: 0; }
            .sidebar { position: absolute; height: 100%; transform: translateX(-100%); }
            .sidebar.active { transform: translateX(0); }
            :root { --chat-padding-inline: 5%; }
            .chat-container { padding: 20px var(--chat-padding-inline); }
            .input-section { padding: 20px 10px; }
            .header { padding: 0 20px; }
            .mobile-menu-btn { display: block !important; }
            .mascot { left: calc(var(--chat-padding-inline) + 4px); bottom: 110px; } /* avoid input area on small screens */
            .mobile-back-btn { display: flex; }
        }
        .mobile-menu-btn { 
            display: none; font-size: 20px; margin-right: 15px; cursor: pointer; color: #fff;
        }

    </style>
</head>
<body>
    <div class="app-shell">
        <!-- SIDEBAR NAVIGATION -->
        <div class="sidebar" id="sidebar">
        <button class="mobile-back-btn" onclick="document.getElementById('sidebar').classList.remove('active')">
            <i class="fas fa-arrow-left"></i> Back to Chat
        </button>
        <!-- 3D Logo Scene -->
        <div class="scene">
            <div class="cube">
                <div class="cube-face front"></div>
                <div class="cube-face back"></div>
                <div class="cube-face right"></div>
                <div class="cube-face left"></div>
                <div class="cube-face top"></div>
                <div class="cube-face bottom"></div>
            </div>
        </div>
        
        <div class="brand-section">
            <div class="brand-name">RUHVAAN AI</div>
            <div style="font-size:12px; color:#666; margin-top:5px;">Advanced Neural Core</div>
        </div>

        <button class="action-btn" id="newChatBtn" onclick="animateAction(this); resetChat()">
            <i class="fas fa-plus"></i> Start New Chat
        </button>

        <div class="menu-list">
            <div class="menu-item active">
                <i class="fas fa-comment-alt"></i> Chat Interface
            </div>
            <div class="menu-item" onclick="triggerModuleAnim(this, 'Generate Images')">
                <i class="fas fa-image"></i> Generate Images
                <span class="coming-soon">Coming Soon</span>
            </div>
            <div class="menu-item" onclick="triggerModuleAnim(this, 'Voice Mode')">
                <i class="fas fa-microphone"></i> Voice Mode
                <span class="coming-soon">Coming Soon</span>
            </div>
            <div class="menu-item" onclick="showPlansModal()">
                <i class="fas fa-tags"></i> Plans & Pricing
            </div>
            <div class="menu-item" onclick="clearStorage()">
                <i class="fas fa-trash"></i> Clear Memory
            </div>
        </div>

        <div class="tg-card">
            <div style="font-size:12px; color:#aaa; margin-bottom:5px;">Developer Access</div>
            <a href="https://t.me/Ruhvaan" target="_blank" class="tg-link">
                <i class="fab fa-telegram"></i> @Ruhvaan
            </a>
        </div>
        </div>

    <!-- MAIN CHAT INTERFACE -->
        <div class="main-wrapper">
        <div class="header">
            <div style="display:flex; align-items:center;">
                <div class="mobile-menu-btn" onclick="document.getElementById('sidebar').classList.toggle('active')">
                    <i class="fas fa-bars"></i>
                </div>
                <div class="header-title">Ruhvaan Core v1.0</div>
            </div>
            <div style="display:flex; align-items:center; gap:10px;">
                <div class="status-badge">
                    <span class="status-dot"></span> ONLINE
                </div>
                <div class="user-menu">
                    <button class="user-menu-btn" id="userMenuBtn" type="button">
                        <img id="userMenuAvatar" src="https://i.imgur.com/8Km9tLL.png" alt="Profile" />
                        <span>Profile</span>
                        <i class="fas fa-chevron-down" style="font-size:12px;"></i>
                    </button>
                    <div class="user-menu-dropdown" id="userMenuDropdown">
                        <div class="user-menu-item" id="menuUpgrade">
                            <i class="fas fa-arrow-up-right-dots"></i> Upgrade plan
                        </div>
                        <div class="user-menu-item" id="menuPersonalize">
                            <i class="fas fa-sliders"></i> Personalization
                        </div>
                        <div class="user-menu-item" id="menuSettings">
                            <i class="fas fa-gear"></i> Settings
                        </div>
                        <div class="user-menu-divider"></div>
                        <div class="user-menu-item" id="menuHelp">
                            <i class="fas fa-circle-question"></i> Help
                        </div>
                        <div class="user-menu-item" id="menuLogout">
                            <i class="fas fa-right-from-bracket"></i> Log out
                        </div>
                    </div>
                </div>
                <div class="auth-pill" id="authPill">
                    <i class="fas fa-user"></i>
                    <span id="authPillText">Guest</span>
                </div>
            </div>
        </div>

        <div class="chat-container" id="chatContainer">
            <!-- Messages will appear here -->

            <!-- Small decorative mascot/character inside chatbox -->
            <div class="mascot" id="mascot" title="Ruhvaan">
                <div class="eyes" aria-hidden="true">
                    <span></span><span></span>
                </div>
                <div class="tooltip">Hi! I'm Ruhvaan 🙂</div>
            </div>
        </div>

        <div class="input-section">
            <div class="input-wrapper">
                <button id="pdfBtn" class="upload-btn" title="Upload PDF (Coming Soon)">
                    <i class="fas fa-file-pdf"></i>
                </button>
                <input type="file" id="pdfInput" accept="application/pdf" style="display:none" />
                <textarea id="userInput" placeholder="Ask Ruhvaan anything..." rows="1"></textarea>
                <button id="sendBtn" class="send-btn" title="Send Message">
                    <i class="fas fa-arrow-up"></i>
                </button>
            </div>
        </div>
        </div>
    </div>

    <!-- AUDIO ELEMENTS -->
    <audio id="snd-send" src="https://assets.mixkit.co/active_storage/sfx/2571/2571-preview.mp3"></audio>
    <audio id="snd-receive" src="https://assets.mixkit.co/active_storage/sfx/2572/2572-preview.mp3"></audio>

    <div class="modal-overlay" id="loginModal">
        <div class="modal">
            <div class="modal-title">
                <h3>Login</h3>
            </div>
            <p>Login to continue chatting and upload PDFs.</p>
            <input type="email" id="loginEmail" placeholder="Email (@gmail.com)" />
            <div class="password-field">
                <input type="password" id="loginPassword" placeholder="Password" />
                <button class="password-toggle" id="togglePassword" type="button">
                    <i class="fas fa-eye"></i>
                </button>
            </div>
            <div class="modal-actions">
                <button class="secondary" id="closeLogin">Cancel</button>
                <button class="primary" id="loginBtn">Login</button>
            </div>
            <div class="modal-link">
                <button id="openForgot">Forgot password?</button>
            </div>
            <p id="loginError" style="color:#f87171; margin-top:10px; display:none;"></p>
            <div class="modal-switch">
                New here? <button id="openSignup">Create an account</button>
            </div>
        </div>
    </div>

    <div class="modal-overlay" id="signupModal">
        <div class="modal">
            <div class="modal-title">
                <h3>Signup</h3>
                <button class="modal-close" id="closeSignupIcon" aria-label="Close signup">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <p>Create your account with Gmail verification.</p>
            <input type="email" id="signupEmail" placeholder="Email (@gmail.com)" />
            <div class="password-field">
                <input type="password" id="signupPassword" placeholder="Password" />
                <button class="password-toggle" id="toggleSignupPassword" type="button">
                    <i class="fas fa-eye"></i>
                </button>
            </div>
            <input type="text" id="signupCode" placeholder="4-digit verification code" />
            <div class="modal-actions">
                <button class="secondary" id="closeSignup">Cancel</button>
                <button class="primary" id="sendCodeBtn">Send Code</button>
            </div>
            <div class="modal-actions">
                <button class="secondary" id="signupBtn">Create Account</button>
            </div>
            <p id="signupError" style="color:#f87171; margin-top:10px; display:none;"></p>
            <div class="modal-switch">
                Already have an account? <button id="openLogin">Login</button>
            </div>
        </div>
    </div>

    <div class="modal-overlay" id="forgotModal">
        <div class="modal">
            <div class="modal-title">
                <h3>Reset Password</h3>
                <button class="modal-close" id="closeForgotIcon" aria-label="Close reset">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <p>Use OTP to reset your password.</p>
            <input type="email" id="forgotEmail" placeholder="Email (@gmail.com)" />
            <div class="password-field">
                <input type="password" id="forgotPassword" placeholder="New password" />
                <button class="password-toggle" id="toggleForgotPassword" type="button">
                    <i class="fas fa-eye"></i>
                </button>
            </div>
            <input type="text" id="forgotCode" placeholder="4-digit verification code" />
            <div class="modal-actions">
                <button class="secondary" id="closeForgot">Cancel</button>
                <button class="primary" id="forgotSendCodeBtn">Send Code</button>
            </div>
            <div class="modal-actions">
                <button class="secondary" id="forgotResetBtn">Update Password</button>
            </div>
            <p id="forgotError" style="color:#f87171; margin-top:10px; display:none;"></p>
        </div>
    </div>

    <div class="modal-overlay" id="profileModal">
        <div class="modal">
            <div class="modal-title">
                <h3>Profile</h3>
                <button class="modal-close" id="closeProfileIcon" aria-label="Close profile">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <img id="profileAvatar" class="profile-avatar" src="https://i.imgur.com/8Km9tLL.png" alt="Profile avatar" />
            <div class="profile-upload">
                <label>
                    <i class="fas fa-camera"></i> Change DP
                    <input type="file" id="profileAvatarInput" accept="image/*" style="display:none" />
                </label>
            </div>
            <input type="text" id="profileName" placeholder="Full name" />
            <input type="text" id="profilePhone" placeholder="Phone number" />
            <input type="text" id="profileClass" placeholder="Class / Year" />
            <input type="text" id="profileTarget" placeholder="Target exam" />
            <input type="text" id="profileCity" placeholder="City" />
            <div class="profile-actions">
                <button class="secondary" id="profileSaveBtn">Save</button>
                <button class="primary" id="profileResetBtn">Reset Password</button>
            </div>
        </div>
    </div>

    <div class="modal-overlay" id="plansModal">
        <div class="modal">
            <div class="modal-title">
                <h3>Plans & Pricing</h3>
                <div style="display:flex; align-items:center; gap:10px;">
                    <span class="coming-soon">Coming Soon</span>
                    <button class="modal-close" id="closePlansIcon" aria-label="Close plans">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
            <div class="plans-grid">
                <div class="plan-card">
                    <h4>Minor</h4>
                    <div class="plan-price">₹0</div>
                    <div class="plan-benefits">Basic chat, 3 guest questions, community support.</div>
                </div>
                <div class="plan-card">
                    <h4>Major</h4>
                    <div class="plan-price">₹199/mo</div>
                    <div class="plan-benefits">Unlimited chat, PDF Q&A, faster responses.</div>
                </div>
                <div class="plan-card">
                    <h4>Pro</h4>
                    <div class="plan-price">₹499/mo</div>
                    <div class="plan-benefits">Priority queue, advanced reasoning, analytics.</div>
                </div>
                <div class="plan-card">
                    <h4>Plus</h4>
                    <div class="plan-price">₹799/mo</div>
                    <div class="plan-benefits">Team sharing, extended memory, premium models.</div>
                </div>
                <div class="plan-card">
                    <h4>Advance</h4>
                    <div class="plan-price">₹1299/mo</div>
                    <div class="plan-benefits">Dedicated support, custom tools, SLA access.</div>
                </div>
            </div>
            <div class="feature-stack">
                <div class="feature-group">
                    <h4>JEE Superpowers</h4>
                    <ul class="feature-list">
                        <li>Doubt Predictor: past chats analyze → weak topics predict → personalized PYQs/micro-lessons.</li>
                        <li>Adaptive Mock Tests: JEE pattern, real-time difficulty adjust, error heatmap + one-click revise.</li>
                        <li>Voice Tutor: Hindi/English voice input, emotion detect → motivation + guided solving.</li>
                    </ul>
                </div>
                <div class="feature-group">
                    <h4>Developer Tools</h4>
                    <ul class="feature-list">
                        <li>Codebase Analyzer: GitHub link → bugs/security scan + Sonar research → optimization suggestions.</li>
                        <li>Live Debugger: error paste → step-by-step trace + sandbox run → proven fixes.</li>
                        <li>Project Blueprint: “Quiz app banao” → complete Flask + SQL + Render deploy ready.</li>
                    </ul>
                </div>
                <div class="feature-group">
                    <h4>Magic Features</h4>
                    <ul class="feature-list">
                        <li>Emotional Coach: stress detect → motivational quotes + smart study breaks.</li>
                        <li>Cross-Platform Sync: Telegram ↔ Web context carry over.</li>
                        <li>Secret Commands: /nano (10-sec answers), /guru (strict mode).</li>
                    </ul>
                </div>
                <p class="feature-note"><strong>Priority:</strong> Doubt Predictor → Voice Tutor → Code Analyzer.</p>
                <p class="feature-note"><strong>Edge:</strong> No gamification, pure productivity + personalization.</p>
            </div>
            <div class="modal-actions">
                <button class="secondary" onclick="hidePlansModal()">Close</button>
            </div>
        </div>
    </div>

    <script>
        /**
         * RUHVAAN AI ENGINE v1.0 (Modified)
         * - Removed intrusive alert popups on sidebar menu items.
         * - Added subtle animated feedback for module clicks & action button.
         * - Added a small mascot character inside the chatbox (decorative + interactive).
         */
        
        // --- CONFIGURATION ---
        const API_URL = (() => {
            const metaBase = document.querySelector('meta[name="api-base"]')?.content?.trim();
            if (metaBase) return metaBase;
            if (window.location.hostname.endsWith('github.io')) {
                return 'https://ruhvaan.vercel.app';
            }
            return window.location.origin;
        })();
        
        // DOM Elements
        const chatContainer = document.getElementById('chatContainer');
        const userInput = document.getElementById('userInput');
        const sendBtn = document.getElementById('sendBtn');
        const sndSend = document.getElementById('snd-send');
        const sndReceive = document.getElementById('snd-receive');
        const mascot = document.getElementById('mascot');
        const newChatBtn = document.getElementById('newChatBtn');
        const pdfBtn = document.getElementById('pdfBtn');
        const pdfInput = document.getElementById('pdfInput');
        const authPill = document.getElementById('authPill');
        const authPillText = document.getElementById('authPillText');
        const loginModal = document.getElementById('loginModal');
        const signupModal = document.getElementById('signupModal');
        const plansModal = document.getElementById('plansModal');
        const forgotModal = document.getElementById('forgotModal');
        const profileModal = document.getElementById('profileModal');
        const closePlansIcon = document.getElementById('closePlansIcon');
        const closeProfileIcon = document.getElementById('closeProfileIcon');
        const loginEmail = document.getElementById('loginEmail');
        const loginPassword = document.getElementById('loginPassword');
        const loginBtn = document.getElementById('loginBtn');
        const sendCodeBtn = document.getElementById('sendCodeBtn');
        const signupBtn = document.getElementById('signupBtn');
        const forgotSendCodeBtn = document.getElementById('forgotSendCodeBtn');
        const forgotResetBtn = document.getElementById('forgotResetBtn');
        const closeLogin = document.getElementById('closeLogin');
        const closeForgot = document.getElementById('closeForgot');
        const closeForgotIcon = document.getElementById('closeForgotIcon');
        const loginError = document.getElementById('loginError');
        const togglePassword = document.getElementById('togglePassword');
        const signupEmail = document.getElementById('signupEmail');
        const signupPassword = document.getElementById('signupPassword');
        const signupCode = document.getElementById('signupCode');
        const toggleSignupPassword = document.getElementById('toggleSignupPassword');
        const forgotEmail = document.getElementById('forgotEmail');
        const forgotPassword = document.getElementById('forgotPassword');
        const forgotCode = document.getElementById('forgotCode');
        const toggleForgotPassword = document.getElementById('toggleForgotPassword');
        const profileName = document.getElementById('profileName');
        const profilePhone = document.getElementById('profilePhone');
        const profileClass = document.getElementById('profileClass');
        const profileTarget = document.getElementById('profileTarget');
        const profileCity = document.getElementById('profileCity');
        const profileAvatar = document.getElementById('profileAvatar');
        const profileAvatarInput = document.getElementById('profileAvatarInput');
        const profileSaveBtn = document.getElementById('profileSaveBtn');
        const profileResetBtn = document.getElementById('profileResetBtn');
        const closeSignup = document.getElementById('closeSignup');
        const closeSignupIcon = document.getElementById('closeSignupIcon');
        const signupError = document.getElementById('signupError');
        const forgotError = document.getElementById('forgotError');
        const openSignup = document.getElementById('openSignup');
        const openLogin = document.getElementById('openLogin');
        const openForgot = document.getElementById('openForgot');
        const userMenuBtn = document.getElementById('userMenuBtn');
        const userMenuAvatar = document.getElementById('userMenuAvatar');
        const userMenuDropdown = document.getElementById('userMenuDropdown');
        const menuUpgrade = document.getElementById('menuUpgrade');
        const menuPersonalize = document.getElementById('menuPersonalize');
        const menuSettings = document.getElementById('menuSettings');
        const menuHelp = document.getElementById('menuHelp');
        const menuLogout = document.getElementById('menuLogout');

        // State
        let isGenerating = false;
        let shouldOfferPdfDownload = false;

        // Initialize
        window.onload = () => {
            loadHistory();
            refreshAuthUI();
            loadProfile();
        };

        // --- CORE FUNCTIONS ---

        // 1. Send Message Logic
        async function handleSend() {
            const text = userInput.value.trim();
            if (!text || isGenerating) return;
            if (!isLoggedIn() && getGuestCount() >= 3) {
                showLoginModal("Please login to continue chatting.");
                return;
            }

            shouldOfferPdfDownload = /(\bpdf\b|download)/i.test(text);

            // UI Updates
            isGenerating = true;
            userInput.value = '';
            resizeTextarea();
            userInput.focus();
            playSound('send');

            // Add User Message
            addMessageToUI(text, 'user');
            saveToHistory(text, 'user');

            // Show Loading Indicator
            const loadingId = addLoadingIndicator();

            try {
                // API Call
                const headers = { 'Content-Type': 'application/json' };
                const token = getAuthToken();
                if (token) headers.Authorization = `Bearer ${token}`;
                const response = await fetch(`${API_URL}/chat`, {
                    method: 'POST',
                    headers,
                    body: JSON.stringify({ message: text })
                });

                if (!response.ok) throw new Error("Server Error");

                const data = await response.json();
                
                // Remove Loading & Show Reply
                removeElement(loadingId);
                await typeWriterEffect(data.reply); // Typing Effect
                
                saveToHistory(data.reply, 'bot');
                if (!isLoggedIn()) incrementGuestCount();
                playSound('receive');

            } catch (error) {
                removeElement(loadingId);
                shouldOfferPdfDownload = false;
                addMessageToUI("⚠️ Error: Server connection failed. Please check internet.", 'bot');
            } finally {
                isGenerating = false;
            }
        }

        // 2. Add Message to UI
        function addMessageToUI(text, sender) {
            const div = document.createElement('div');
            div.className = `msg-row ${sender}`;
            const messageIndex = sender === 'user'
                ? `Q${document.querySelectorAll('.msg-row.user').length + 1}: `
                : '';
            
            // Markdown Parsing (Basic)
            let formattedText = text
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/\\*\\*(.*?)\\*\\*/g, '<b>$1</b>')
                .replace(/`([^`]+)`/g, '<code style="background:#222; padding:2px 5px; border-radius:4px; color:#ff79c6">$1</code>');

            // Code Block Detection
            if (formattedText.includes('```')) {
                formattedText = formattedText.replace(/```(\\w+)?\\n([\\s\\S]*?)```/g, 
                    '<pre><code class="language-$1">$2</code></pre>');
            } else {
                formattedText = formattedText.replace(/\\n/g, '<br>');
            }

            const shouldShowDownload = sender === 'bot' && shouldOfferPdfDownload;
            const downloadButton = shouldShowDownload
                ? `<button class="upload-btn" style="margin-top:10px;" onclick="downloadPdf(${JSON.stringify(text)})">
                        <i class="fas fa-file-pdf"></i> Download PDF
                   </button>`
                : '';
            div.innerHTML = `
                <div class="avatar">
                    ${sender === 'bot' ? '<i class="fas fa-cube"></i>' : '<i class="fas fa-user"></i>'}
                </div>
                <div class="bubble">
                    ${messageIndex}${formattedText}
                    ${downloadButton}
                </div>
            `;
            
            chatContainer.appendChild(div);
            if (shouldShowDownload) {
                shouldOfferPdfDownload = false;
            }
            
            // Highlight Code Blocks
            div.querySelectorAll('pre code').forEach((block) => {
                hljs.highlightElement(block);
            });

            scrollToBottom();
        }

        // 3. Typing Effect (ChatGPT Style)
        function typeWriterEffect(text) {
            return new Promise(resolve => {
                const div = document.createElement('div');
                div.className = 'msg-row bot';
                div.innerHTML = `
                    <div class="avatar"><i class="fas fa-cube"></i></div>
                    <div class="bubble"></div>
                `;
                chatContainer.appendChild(div);
                const bubble = div.querySelector('.bubble');
                
                // If code block, skip typing effect (it breaks HTML)
                if (text.includes('```')) {
                    div.remove();
                    addMessageToUI(text, 'bot');
                    resolve();
                    return;
                }

                let i = 0;
                const speed = 10; // Typing speed in ms

                function type() {
                    if (i < text.length) {
                        bubble.textContent += text.charAt(i);
                        i++;
                        scrollToBottom();
                        setTimeout(type, speed);
                    } else {
                        // After typing, replace textContent with HTML to render Markdown
                        bubble.innerHTML = text.replace(/\\n/g, '<br>').replace(/\\*\\*(.*?)\\*\\*/g, '<b>$1</b>');
                        resolve();
                    }
                }
                type();
            });
        }

        // 4. Loading Indicator
        function addLoadingIndicator() {
            const id = 'loading-' + Date.now();
            const div = document.createElement('div');
            div.className = 'msg-row bot';
            div.id = id;
            div.innerHTML = `
                <div class="avatar"><i class="fas fa-circle-notch fa-spin"></i></div>
                <div class="bubble" style="color:#777; font-style:italic">Thinking...</div>
            `;
            chatContainer.appendChild(div);
            scrollToBottom();
            return id;
        }

        // --- UTILITIES ---

        function removeElement(id) {
            const el = document.getElementById(id);
            if(el) el.remove();
        }

        function scrollToBottom() {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        function playSound(type) {
            if(type === 'send') { sndSend.currentTime = 0; sndSend.volume=0.2; sndSend.play().catch(e=>{}); }
            if(type === 'receive') { sndReceive.currentTime = 0; sndReceive.volume=0.2; sndReceive.play().catch(e=>{}); }
        }

        function resizeTextarea() {
            userInput.style.height = 'auto';
            userInput.style.height = (userInput.scrollHeight) + 'px';
            if(userInput.value === '') userInput.style.height = '50px';
        }

        // --- MEMORY MANAGEMENT (Local Storage) ---
        function saveToHistory(text, sender) {
            const history = JSON.parse(localStorage.getItem('ruhvaan_chat') || '[]');
            history.push({ text, sender });
            localStorage.setItem('ruhvaan_chat', JSON.stringify(history));
        }

        function loadHistory() {
            const history = JSON.parse(localStorage.getItem('ruhvaan_chat') || '[]');
            if(history.length === 0) {
                // Default Welcome Message
                addMessageToUI("**Hello! Main Ruhvaan hoon.**\\nSystem online and ready. Main aapki kya madad karoon?", 'bot');
            } else {
                history.forEach(msg => addMessageToUI(msg.text, msg.sender));
            }
        }

        function resetChat() {
            if(confirm("Start new chat? Purani chat delete ho jayegi.")) {
                localStorage.removeItem('ruhvaan_chat');
                chatContainer.innerHTML = '';
                // re-insert mascot so it remains visible after clearing
                chatContainer.appendChild(mascot);
                addMessageToUI("Chat reset successful. Starting fresh!", 'bot');
            }
        }
        
        function clearStorage() {
            localStorage.clear();
            alert("Memory Cleared!");
            location.reload();
        }

        function getGuestCount() {
            return parseInt(localStorage.getItem('ruhvaan_guest_count') || '0', 10);
        }

        function incrementGuestCount() {
            const next = getGuestCount() + 1;
            localStorage.setItem('ruhvaan_guest_count', String(next));
            if (next >= 3) {
                showLoginModal("You have reached the guest limit. Please login.");
            }
        }

        function getAuthToken() {
            return localStorage.getItem('ruhvaan_token') || '';
        }

        function isLoggedIn() {
            return Boolean(getAuthToken());
        }

        function setAuth(token, email) {
            localStorage.setItem('ruhvaan_token', token);
            localStorage.setItem('ruhvaan_email', email);
            localStorage.removeItem('ruhvaan_guest_count');
            refreshAuthUI();
        }

        function clearAuth() {
            localStorage.removeItem('ruhvaan_token');
            localStorage.removeItem('ruhvaan_email');
            refreshAuthUI();
        }

        function refreshAuthUI() {
            const email = localStorage.getItem('ruhvaan_email');
            if (email) {
                authPillText.innerHTML = `<strong>${email}</strong>`;
                authPill.title = "Click to logout";
            } else {
                authPillText.textContent = "Guest";
                authPill.title = "Click to login";
            }
        }

        function showLoginModal(message) {
            if (message) {
                loginError.style.display = 'block';
                loginError.textContent = message;
            } else {
                loginError.style.display = 'none';
            }
            loginModal.classList.add('active');
            signupModal.classList.remove('active');
            forgotModal.classList.remove('active');
            profileModal.classList.remove('active');
        }

        function hideLoginModal() {
            loginModal.classList.remove('active');
            loginError.style.display = 'none';
        }

        function showSignupModal(message) {
            if (message) {
                signupError.style.display = 'block';
                signupError.textContent = message;
            } else {
                signupError.style.display = 'none';
            }
            signupModal.classList.add('active');
            loginModal.classList.remove('active');
            forgotModal.classList.remove('active');
            profileModal.classList.remove('active');
        }

        function hideSignupModal() {
            signupModal.classList.remove('active');
            signupError.style.display = 'none';
        }

        function showForgotModal(message) {
            if (message) {
                forgotError.style.display = 'block';
                forgotError.textContent = message;
            } else {
                forgotError.style.display = 'none';
            }
            forgotModal.classList.add('active');
            signupModal.classList.remove('active');
            loginModal.classList.remove('active');
        }

        function hideForgotModal() {
            forgotModal.classList.remove('active');
            forgotError.style.display = 'none';
        }

        function showProfileModal() {
            loadProfile();
            profileModal.classList.add('active');
        }

        function hideProfileModal() {
            profileModal.classList.remove('active');
        }

        function loadProfile() {
            profileName.value = localStorage.getItem('ruhvaan_profile_name') || '';
            profilePhone.value = localStorage.getItem('ruhvaan_profile_phone') || '';
            profileClass.value = localStorage.getItem('ruhvaan_profile_class') || '';
            profileTarget.value = localStorage.getItem('ruhvaan_profile_target') || '';
            profileCity.value = localStorage.getItem('ruhvaan_profile_city') || '';
            const avatar = localStorage.getItem('ruhvaan_profile_avatar') || 'https://i.imgur.com/8Km9tLL.png';
            profileAvatar.src = avatar;
            userMenuAvatar.src = avatar;
        }

        function saveProfile() {
            localStorage.setItem('ruhvaan_profile_name', profileName.value.trim());
            localStorage.setItem('ruhvaan_profile_phone', profilePhone.value.trim());
            localStorage.setItem('ruhvaan_profile_class', profileClass.value.trim());
            localStorage.setItem('ruhvaan_profile_target', profileTarget.value.trim());
            localStorage.setItem('ruhvaan_profile_city', profileCity.value.trim());
            showTinyToast("Profile saved.");
        }

        function startOtpTimer(button) {
            if (!button) return;
            if (button.dataset.timerId) {
                clearInterval(Number(button.dataset.timerId));
            }
            const defaultLabel = button.dataset.defaultLabel || button.textContent.trim();
            button.dataset.defaultLabel = defaultLabel;
            let remaining = 30;
            button.disabled = true;
            button.textContent = `Resend in ${remaining}s`;
            const timerId = setInterval(() => {
                remaining -= 1;
                if (remaining <= 0) {
                    clearInterval(timerId);
                    button.disabled = false;
                    button.textContent = 'Resend OTP';
                    button.dataset.timerId = '';
                } else {
                    button.textContent = `Resend in ${remaining}s`;
                }
            }, 1000);
            button.dataset.timerId = String(timerId);
        }

        function showPlansModal() {
            plansModal.classList.add('active');
        }

        function hidePlansModal() {
            plansModal.classList.remove('active');
        }

        // --- NEW: Non-blocking module animation (replaces alert popups) ---
        function triggerModuleAnim(el, moduleName) {
            // create small animated dot inside the menu item to show feedback
            // remove any existing anim node first
            const existing = el.querySelector('.module-anim');
            if (existing) existing.remove();

            const dot = document.createElement('span');
            dot.className = 'module-anim';
            el.appendChild(dot);

            // briefly animate the action button too for feedback
            animateAction(newChatBtn);

            // optional: show a small ephemeral toast near header (non-blocking)
            const comingSoonModules = new Set(['Generate Images', 'Voice Mode']);
            const toastMessage = comingSoonModules.has(moduleName)
                ? `${moduleName} coming soon...`
                : `${moduleName} loading...`;
            showTinyToast(toastMessage);

            // remove the dot after animation
            setTimeout(() => {
                dot.remove();
            }, 1200);
        }

        // animateAction: adds ripple effect to a button
        function animateAction(btn) {
            if(!btn) return;
            btn.classList.add('animating');
            setTimeout(() => btn.classList.remove('animating'), 900);
        }

        // small non-blocking toast (fades away)
        function showTinyToast(text) {
            const toast = document.createElement('div');
            toast.textContent = text;
            toast.style.position = 'fixed';
            toast.style.right = '26px';
            toast.style.bottom = '26px';
            toast.style.padding = '10px 14px';
            toast.style.background = 'rgba(255,255,255,0.04)';
            toast.style.border = '1px solid var(--border)';
            toast.style.borderRadius = '10px';
            toast.style.color = '#ddd';
            toast.style.zIndex = 60;
            toast.style.fontSize = '13px';
            toast.style.boxShadow = '0 6px 18px rgba(0,0,0,0.6)';
            document.body.appendChild(toast);
            setTimeout(()=> { toast.style.transition = 'opacity 300ms'; toast.style.opacity = '0'; }, 1100);
            setTimeout(()=> { toast.remove(); }, 1500);
        }

        // --- Mascot interactions ---
        // mascot bounces and shows small tooltip when clicked
        if (mascot) {
            mascot.addEventListener('click', () => {
                mascot.classList.remove('bounce');
                // retrigger animation
                void mascot.offsetWidth;
                mascot.classList.add('bounce');
                mascot.classList.add('show-tooltip');
                setTimeout(()=> mascot.classList.remove('show-tooltip'), 1600);
            });

            // small idle blink for eyes
            setInterval(() => {
                const eyes = mascot.querySelectorAll('.eyes span');
                eyes.forEach(e => e.style.transform = 'scaleY(0.25)');
                setTimeout(() => eyes.forEach(e => e.style.transform = 'scaleY(1)'), 140);
            }, 4200);
        }

        // --- EVENT LISTENERS ---
        
        sendBtn.addEventListener('click', handleSend);

        userInput.addEventListener('input', resizeTextarea);

        if (pdfBtn && pdfInput) {
            pdfBtn.addEventListener('click', () => pdfInput.click());
            pdfInput.addEventListener('change', async () => {
                const file = pdfInput.files?.[0];
                if (!file) return;
                if (!isLoggedIn()) {
                    pdfInput.value = '';
                    showLoginModal("Login required to upload PDFs.");
                    return;
                }
                const formData = new FormData();
                formData.append('file', file);
                addMessageToUI(`📎 Uploaded: ${file.name}`, 'user');
                const loadingId = addLoadingIndicator();
                try {
                    const token = getAuthToken();
                    const response = await fetch(`${API_URL}/upload`, {
                        method: 'POST',
                        headers: token ? { Authorization: `Bearer ${token}` } : {},
                        body: formData
                    });
                    if (!response.ok) throw new Error('Upload failed');
                    const data = await response.json();
                    removeElement(loadingId);
                    addMessageToUI(data.reply || 'PDF received. Processing soon.', 'bot');
                } catch (error) {
                    removeElement(loadingId);
                    addMessageToUI("⚠️ PDF upload failed. Please try again.", 'bot');
                } finally {
                    pdfInput.value = '';
                }
            });
        }

        if (authPill) {
            authPill.addEventListener('click', () => {
                if (isLoggedIn()) {
                    clearAuth();
                    showTinyToast("Logged out");
                } else {
                    showLoginModal();
                }
            });
        }

        if (closeLogin) {
            closeLogin.addEventListener('click', hideLoginModal);
        }
        if (closeForgot) {
            closeForgot.addEventListener('click', hideForgotModal);
        }
        if (closeSignup) {
            closeSignup.addEventListener('click', hideSignupModal);
        }
        if (closeSignupIcon) {
            closeSignupIcon.addEventListener('click', hideSignupModal);
        }
        if (closeForgotIcon) {
            closeForgotIcon.addEventListener('click', hideForgotModal);
        }
        if (closeProfileIcon) {
            closeProfileIcon.addEventListener('click', hideProfileModal);
        }
        if (closePlansIcon) {
            closePlansIcon.addEventListener('click', hidePlansModal);
        }
        if (openSignup) {
            openSignup.addEventListener('click', () => showSignupModal());
        }
        if (openLogin) {
            openLogin.addEventListener('click', () => showLoginModal());
        }
        if (openForgot) {
            openForgot.addEventListener('click', () => showForgotModal());
        }
        if (profileSaveBtn) {
            profileSaveBtn.addEventListener('click', () => {
                saveProfile();
                hideProfileModal();
            });
        }
        if (profileResetBtn) {
            profileResetBtn.addEventListener('click', () => {
                hideProfileModal();
                showForgotModal();
            });
        }
        if (profileAvatarInput) {
            profileAvatarInput.addEventListener('change', () => {
                const file = profileAvatarInput.files?.[0];
                if (!file) return;
                const reader = new FileReader();
                reader.onload = () => {
                    const dataUrl = String(reader.result || '');
                    if (dataUrl) {
                        localStorage.setItem('ruhvaan_profile_avatar', dataUrl);
                        profileAvatar.src = dataUrl;
                        userMenuAvatar.src = dataUrl;
                    }
                };
                reader.readAsDataURL(file);
            });
        }
        if (userMenuBtn && userMenuDropdown) {
            userMenuBtn.addEventListener('click', (event) => {
                event.stopPropagation();
                userMenuDropdown.classList.toggle('active');
            });
        }
        document.addEventListener('click', () => {
            if (userMenuDropdown) {
                userMenuDropdown.classList.remove('active');
            }
        });
        if (menuUpgrade) {
            menuUpgrade.addEventListener('click', () => {
                userMenuDropdown.classList.remove('active');
                showPlansModal();
            });
        }
        if (menuPersonalize) {
            menuPersonalize.addEventListener('click', () => {
                userMenuDropdown.classList.remove('active');
                showProfileModal();
            });
        }
        if (menuSettings) {
            menuSettings.addEventListener('click', () => {
                userMenuDropdown.classList.remove('active');
                showProfileModal();
            });
        }
        if (menuHelp) {
            menuHelp.addEventListener('click', () => {
                userMenuDropdown.classList.remove('active');
                window.open('https://t.me/Ruhvaan', '_blank');
            });
        }
        if (menuLogout) {
            menuLogout.addEventListener('click', () => {
                userMenuDropdown.classList.remove('active');
                clearAuth();
                showTinyToast('Logged out');
            });
        }

        if (loginBtn) {
            loginBtn.addEventListener('click', async () => {
                try {
                    const response = await fetch(`${API_URL}/auth/login`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            email: loginEmail.value.trim(),
                            password: loginPassword.value
                        })
                    });
                    if (!response.ok) {
                        const errorData = await response.json().catch(() => ({}));
                        throw new Error(errorData.detail || 'Login failed');
                    }
                    const data = await response.json();
                    setAuth(data.token, data.email);
                    hideLoginModal();
                    showTinyToast("Logged in");
                } catch (error) {
                    showLoginModal(error.message || "Login failed. Check email/password.");
                }
            });
        }

        if (signupBtn) {
            signupBtn.addEventListener('click', async () => {
                try {
                    const response = await fetch(`${API_URL}/auth/register`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            email: signupEmail.value.trim(),
                            password: signupPassword.value,
                            code: signupCode.value.trim()
                        })
                    });
                    if (!response.ok) {
                        const errorData = await response.json().catch(() => ({}));
                        throw new Error(errorData.detail || 'Signup failed');
                    }
                    const data = await response.json();
                    setAuth(data.token, data.email);
                    hideSignupModal();
                    showTinyToast("Account created.");
                } catch (error) {
                    showSignupModal(error.message || "Signup failed. Try a different email.");
                }
            });
        }

        if (togglePassword) {
            togglePassword.addEventListener('click', () => {
                const isHidden = loginPassword.type === 'password';
                loginPassword.type = isHidden ? 'text' : 'password';
                togglePassword.innerHTML = isHidden
                    ? '<i class="fas fa-eye-slash"></i>'
                    : '<i class="fas fa-eye"></i>';
            });
        }

        if (sendCodeBtn) {
            sendCodeBtn.addEventListener('click', async () => {
                try {
                    const response = await fetch(`${API_URL}/auth/request-code`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ email: signupEmail.value.trim() })
                    });
                    if (!response.ok) {
                        const errorData = await response.json().catch(() => ({}));
                        throw new Error(errorData.detail || 'Failed to send code');
                    }
                    const data = await response.json();
                    showTinyToast(data.message || "Verification code sent.");
                    startOtpTimer(sendCodeBtn);
                } catch (error) {
                    showSignupModal(error.message || "Failed to send code.");
                }
            });
        }

        if (toggleSignupPassword) {
            toggleSignupPassword.addEventListener('click', () => {
                const isHidden = signupPassword.type === 'password';
                signupPassword.type = isHidden ? 'text' : 'password';
                toggleSignupPassword.innerHTML = isHidden
                    ? '<i class="fas fa-eye-slash"></i>'
                    : '<i class="fas fa-eye"></i>';
            });
        }

        if (toggleForgotPassword) {
            toggleForgotPassword.addEventListener('click', () => {
                const isHidden = forgotPassword.type === 'password';
                forgotPassword.type = isHidden ? 'text' : 'password';
                toggleForgotPassword.innerHTML = isHidden
                    ? '<i class="fas fa-eye-slash"></i>'
                    : '<i class="fas fa-eye"></i>';
            });
        }

        if (forgotSendCodeBtn) {
            forgotSendCodeBtn.addEventListener('click', async () => {
                try {
                    const response = await fetch(`${API_URL}/auth/request-reset-code`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ email: forgotEmail.value.trim() })
                    });
                    if (!response.ok) {
                        const errorData = await response.json().catch(() => ({}));
                        throw new Error(errorData.detail || 'Failed to send code');
                    }
                    const data = await response.json();
                    showTinyToast(data.message || "Verification code sent.");
                    startOtpTimer(forgotSendCodeBtn);
                } catch (error) {
                    showForgotModal(error.message || "Failed to send code.");
                }
            });
        }

        if (forgotResetBtn) {
            forgotResetBtn.addEventListener('click', async () => {
                try {
                    const response = await fetch(`${API_URL}/auth/reset-password`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            email: forgotEmail.value.trim(),
                            password: forgotPassword.value,
                            code: forgotCode.value.trim()
                        })
                    });
                    if (!response.ok) {
                        const errorData = await response.json().catch(() => ({}));
                        throw new Error(errorData.detail || 'Password reset failed');
                    }
                    const data = await response.json();
                    hideForgotModal();
                    showTinyToast(data.message || "Password updated.");
                } catch (error) {
                    showForgotModal(error.message || "Password reset failed.");
                }
            });
        }

        function downloadPdf(text) {
            const { jsPDF } = window.jspdf;
            const doc = new jsPDF();
            const lines = doc.splitTextToSize(text, 180);
            doc.text(lines, 10, 10);
            doc.save('ruhvaan-answer.pdf');
        }
        
        userInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSend();
            }
        });

    </script>
</body>
</html>
"""

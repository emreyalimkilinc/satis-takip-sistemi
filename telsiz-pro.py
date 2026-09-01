from flask import Flask, render_template_string

app = Flask(__name__)

HTML_CONTENT = """<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>WebTelsiz Pro - Mobil Telsiz Sistemi</title>
    <style>
        :root {
            --bg-color: #0f141c;
            --radio-case: #1e2634;
            --radio-case-dark: #151b24;
            --accent-yellow: #f39c12;
            --accent-green: #27ae60;
            --accent-red: #c0392b;
            --text-main: #ecf0f1;
            --text-muted: #95a5a6;
            --lcd-bg: #9bca3e;
            --lcd-text: #1b2611;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            -webkit-tap-highlight-color: transparent;
        }

        body {
            background-color: var(--bg-color);
            color: var(--text-main);
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            overflow: hidden;
        }

        #app {
            width: 100%;
            max-width: 420px;
            height: 100%;
            max-height: 850px;
            background: var(--bg-color);
            display: flex;
            flex-direction: column;
            position: relative;
            box-shadow: 0 10px 30px rgba(0,0,0,0.8);
        }

        @media (min-width: 480px) {
            #app {
                border-radius: 36px;
                border: 8px solid #2c3e50;
                height: 92vh;
            }
        }

        .screen {
            display: none;
            flex: 1;
            flex-direction: column;
            padding: 20px;
            overflow-y: auto;
            position: relative;
        }

        .screen.active {
            display: flex;
        }

        .auth-container {
            justify-content: center;
            align-items: center;
            text-align: center;
            background: linear-gradient(135deg, #141a23, #1e293b);
            padding: 30px;
        }

        .auth-logo {
            font-size: 50px;
            margin-bottom: 10px;
        }

        .auth-title {
            font-size: 24px;
            font-weight: 800;
            color: var(--text-main);
            margin-bottom: 5px;
        }

        .auth-subtitle {
            font-size: 14px;
            color: var(--text-muted);
            margin-bottom: 30px;
        }

        .form-group {
            width: 100%;
            margin-bottom: 15px;
            text-align: left;
        }

        .form-group label {
            display: block;
            font-size: 12px;
            color: var(--text-muted);
            margin-bottom: 5px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .form-control {
            width: 100%;
            padding: 14px 16px;
            background: #0b0f17;
            border: 1px solid #2a3447;
            border-radius: 12px;
            color: #fff;
            font-size: 16px;
            outline: none;
            transition: border-color 0.2s;
        }

        .form-control:focus {
            border-color: var(--accent-yellow);
        }

        .btn {
            width: 100%;
            padding: 14px;
            border: none;
            border-radius: 12px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.1s, opacity 0.2s;
        }

        .btn:active {
            transform: scale(0.98);
        }

        .btn-primary {
            background: var(--accent-yellow);
            color: #111;
            margin-top: 10px;
        }

        .btn-secondary {
            background: transparent;
            color: var(--text-muted);
            border: 1px solid #2a3447;
            margin-top: 10px;
        }

        .link-text {
            margin-top: 20px;
            font-size: 14px;
            color: var(--text-muted);
        }

        .link-text span {
            color: var(--accent-yellow);
            cursor: pointer;
            font-weight: bold;
        }

        .radio-body {
            background: linear-gradient(145deg, var(--radio-case), var(--radio-case-dark));
            border-radius: 24px;
            padding: 16px;
            display: flex;
            flex-direction: column;
            flex: 1;
            box-shadow: inset 0 2px 5px rgba(255,255,255,0.08), 0 10px 25px rgba(0,0,0,0.5);
            border: 2px solid #2a3447;
            position: relative;
        }

        .radio-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0 10px 15px 10px;
            border-bottom: 2px dashed #141a23;
        }

        .antenna {
            width: 12px;
            height: 50px;
            background: linear-gradient(90deg, #111, #333, #111);
            border-radius: 4px;
            position: absolute;
            top: -30px;
            left: 35px;
            box-shadow: 0 -2px 5px rgba(0,0,0,0.5);
        }

        .knob-container {
            display: flex;
            gap: 15px;
        }

        .knob {
            width: 40px;
            height: 40px;
            background: #111;
            border-radius: 50%;
            border: 3px solid #333;
            position: relative;
            box-shadow: 0 4px 8px rgba(0,0,0,0.5);
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .knob::after {
            content: '';
            width: 3px;
            height: 14px;
            background: var(--accent-yellow);
            position: absolute;
            top: 2px;
            border-radius: 2px;
        }

        .top-info-badge {
            font-size: 11px;
            color: var(--text-muted);
            background: #111;
            padding: 4px 8px;
            border-radius: 6px;
            border: 1px solid #333;
        }

        .radio-lcd {
            background-color: var(--lcd-bg);
            color: var(--lcd-text);
            border-radius: 8px;
            padding: 12px;
            margin: 15px 0;
            font-family: monospace;
            border: 3px solid #2b3b14;
            box-shadow: inset 0 2px 5px rgba(0,0,0,0.3);
        }

        .lcd-row {
            display: flex;
            justify-content: space-between;
            font-size: 13px;
            font-weight: bold;
            margin-bottom: 4px;
        }

        .lcd-channel {
            font-size: 20px;
            font-weight: 900;
            letter-spacing: 1px;
        }

        .lcd-status {
            font-size: 12px;
            background: rgba(0,0,0,0.1);
            padding: 2px 6px;
            border-radius: 4px;
            display: inline-block;
            margin-top: 5px;
        }

        .speaker-grille {
            display: flex;
            flex-direction: column;
            gap: 5px;
            padding: 10px 30px;
            margin: 5px 0 15px 0;
        }

        .speaker-line {
            height: 4px;
            background: #141a23;
            border-radius: 2px;
            box-shadow: inset 0 1px 2px rgba(0,0,0,0.8);
        }

        .ptt-container {
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            position: relative;
        }

        .ptt-btn {
            width: 140px;
            height: 140px;
            border-radius: 50%;
            background: linear-gradient(145deg, #e74c3c, #c0392b);
            border: 6px solid #2a3447;
            color: white;
            font-size: 18px;
            font-weight: 900;
            letter-spacing: 1px;
            cursor: pointer;
            box-shadow: 0 10px 25px rgba(192, 57, 43, 0.5), inset 0 4px 10px rgba(255,255,255,0.2);
            transition: all 0.1s ease;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 5px;
            user-select: none;
        }

        .ptt-btn span {
            font-size: 11px;
            font-weight: normal;
            opacity: 0.8;
        }

        .ptt-btn.active {
            background: linear-gradient(145deg, #2ecc71, #27ae60);
            box-shadow: 0 4px 10px rgba(39, 174, 96, 0.6), inset 0 4px 10px rgba(0,0,0,0.2);
            transform: scale(0.96);
            border-color: #1e3a29;
        }

        .radio-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: #141a23;
            padding: 10px 15px;
            border-radius: 12px;
            border: 1px solid #2a3447;
            margin-top: 10px;
        }

        .nav-icon-btn {
            background: none;
            border: none;
            color: var(--text-muted);
            font-size: 12px;
            cursor: pointer;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 2px;
        }

        .nav-icon-btn.active {
            color: var(--accent-yellow);
        }

        .nav-icon-btn i {
            font-size: 18px;
        }

        .admin-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            border-bottom: 1px solid #2a3447;
            padding-bottom: 10px;
        }

        .admin-title {
            font-size: 18px;
            font-weight: bold;
            color: var(--accent-yellow);
        }

        .admin-card {
            background: #141a23;
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 15px;
            border: 1px solid #2a3447;
        }

        .user-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid #1e2634;
        }

        .user-info div:first-child {
            font-weight: bold;
            font-size: 14px;
        }

        .user-info div:last-child {
            font-size: 11px;
            color: var(--text-muted);
        }

        .badge {
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 10px;
            font-weight: bold;
            text-transform: uppercase;
        }

        .badge-admin { background: #d35400; color: #fff; }
        .badge-user { background: #2980b9; color: #fff; }
        .badge-banned { background: #c0392b; color: #fff; }

        .action-btns {
            display: flex;
            gap: 5px;
        }

        .btn-sm {
            padding: 5px 10px;
            font-size: 11px;
            border-radius: 6px;
            border: none;
            cursor: pointer;
            font-weight: bold;
        }

        .btn-danger { background: #c0392b; color: #fff; }
        .btn-success { background: #27ae60; color: #fff; }
        .btn-warning { background: #f39c12; color: #111; }

        .channel-list {
            display: flex;
            flex-direction: column;
            gap: 8px;
            margin-top: 10px;
        }

        .channel-pill {
            background: #0b0f17;
            padding: 12px 15px;
            border-radius: 10px;
            border: 1px solid #2a3447;
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
        }

        .channel-pill.active {
            border-color: var(--accent-yellow);
            background: #1e2634;
        }

        .back-link {
            color: var(--accent-yellow);
            font-size: 13px;
            cursor: pointer;
            margin-bottom: 15px;
            display: inline-block;
        }
    </style>
</head>
<body>

<div id="app">
    <div id="loginScreen" class="screen auth-container active">
        <div class="auth-logo">📻</div>
        <div class="auth-title">WEB TELSİZ PRO</div>
        <div class="auth-subtitle">Mobil Uyumlu Gerçek Zamanlı Telsiz Sistemi</div>

        <div class="form-group">
            <label>Kullanıcı Adı</label>
            <input type="text" id="loginUsername" class="form-control" placeholder="Kullanıcı adınızı girin">
        </div>
        <div class="form-group">
            <label>Şifre</label>
            <input type="password" id="loginPassword" class="form-control" placeholder="Şifrenizi girin">
        </div>

        <button class="btn btn-primary" onclick="handleLogin()">GİRİŞ YAP</button>
        <div class="link-text">Hesabınız yok mu? <span onclick="switchScreen('registerScreen')">Kayıt Ol</span></div>
    </div>

    <div id="registerScreen" class="screen auth-container">
        <div class="auth-logo">📝</div>
        <div class="auth-title">KAYIT OL</div>
        <div class="auth-subtitle">Yeni bir telsiz hesabı oluşturun</div>

        <div class="form-group">
            <label>Kullanıcı Adı</label>
            <input type="text" id="regUsername" class="form-control" placeholder="Kullanıcı adı seçin">
        </div>
        <div class="form-group">
            <label>Şifre</label>
            <input type="password" id="regPassword" class="form-control" placeholder="Güçlü bir şifre girin">
        </div>

        <button class="btn btn-primary" onclick="handleRegister()">KAYIT OL</button>
        <div class="link-text">Zaten hesabınız var mı? <span onclick="switchScreen('loginScreen')">Giriş Yap</span></div>
    </div>

    <div id="radioScreen" class="screen">
        <div class="antenna"></div>
        <div class="radio-body">
            <div class="radio-top">
                <div class="knob-container">
                    <div class="knob" title="Ses Seviyesi"></div>
                    <div class="knob" title="Kanal Seçici"></div>
                </div>
                <div class="top-info-badge" id="userBadgeRole">KULLANICI</div>
            </div>

            <div class="radio-lcd">
                <div class="lcd-row">
                    <span>KANAL:</span>
                    <span id="lcdChannelName" class="lcd-channel">GENEL-1</span>
                </div>
                <div class="lcd-row">
                    <span>DURUM:</span>
                    <span id="lcdStatusText">BEKLEMEDE</span>
                </div>
                <div class="lcd-status" id="lcdSignalStatus">📶 BAĞLI (Simüle)</div>
            </div>

            <div class="speaker-grille">
                <div class="speaker-line"></div>
                <div class="speaker-line"></div>
                <div class="speaker-line"></div>
                <div class="speaker-line"></div>
                <div class="speaker-line"></div>
            </div>

            <div class="ptt-container">
                <button id="pttButton" class="ptt-btn" 
                    ontouchstart="startTransmission(event)" ontouchend="stopTransmission(event)"
                    onmousedown="startTransmission(event)" onmouseup="stopTransmission(event)">
                    BAS & KONUŞ
                    <span>PTT BUTTON</span>
                </button>
            </div>

            <div class="radio-footer">
                <button class="nav-icon-btn active" onclick="switchScreen('radioScreen')">
                    <i>📻</i> Telsiz
                </button>
                <button class="nav-icon-btn" onclick="switchScreen('channelScreen')">
                    <i>📡</i> Kanallar
                </button>
                <button class="nav-icon-btn" id="adminNavBtn" style="display:none;" onclick="openAdminPanel()">
                    <i>⚙️</i> Admin
                </button>
                <button class="nav-icon-btn" onclick="handleLogout()">
                    <i>🚪</i> Çıkış
                </button>
            </div>
        </div>
    </div>

    <div id="channelScreen" class="screen auth-container" style="justify-content: flex-start; text-align: left;">
        <span class="back-link" onclick="switchScreen('radioScreen')">&larr; Telsize Dön</span>
        <div class="auth-title" style="margin-top: 10px;">KANALLAR</div>
        <div class="auth-subtitle">Aktif telsiz frekansları</div>

        <div class="channel-list" id="channelListContainer"></div>

        <div style="margin-top: 20px;">
            <div class="form-group">
                <label>Yeni Kanal Oluştur</label>
                <input type="text" id="newChannelName" class="form-control" placeholder="Örn: Acil-Durum">
            </div>
            <button class="btn btn-secondary" onclick="createChannel()">KANAL EKLE</button>
        </div>
    </div>

    <div id="adminScreen" class="screen" style="background: var(--bg-color);">
        <span class="back-link" onclick="switchScreen('radioScreen')">&larr; Telsize Dön</span>
        <div class="admin-header">
            <div class="admin-title">⚙️ ADMIN KONTROL PANELİ</div>
            <span class="badge badge-admin">YETKİLİ</span>
        </div>

        <div class="admin-card">
            <div style="font-weight: bold; margin-bottom: 10px; font-size: 14px;">Kullanıcı Yönetimi</div>
            <div id="adminUserList"></div>
        </div>

        <div class="admin-card">
            <div style="font-weight: bold; margin-bottom: 10px; font-size: 14px;">Sistem Bilgisi</div>
            <div style="font-size: 12px; color: var(--text-muted); line-height: 1.6;">
                <div>Toplam Kullanıcı: <span id="statTotalUsers" style="color:#fff; font-weight:bold;">0</span></div>
                <div>Aktif Kanal: <span id="statActiveChannel" style="color:#fff; font-weight:bold;">GENEL-1</span></div>
                <div>Sunucu Durumu: <span style="color:var(--accent-green); font-weight:bold;">Çevrimiçi (WebRTC Ready)</span></div>
            </div>
        </div>
    </div>
</div>

<script>
    function initDatabase() {
        if (!localStorage.getItem('wt_users')) {
            const defaultUsers = [
                { username: 'admin', password: '123', role: 'admin', isBanned: false },
                { username: 'user1', password: '123', role: 'user', isBanned: false }
            ];
            localStorage.setItem('wt_users', JSON.stringify(defaultUsers));
        }
        if (!localStorage.getItem('wt_channels')) {
            const defaultChannels = ['GENEL-1', 'OPERASYON-ALPHA', 'SAHA-DESTEK', 'ACIL-DURUM'];
            localStorage.setItem('wt_channels', JSON.stringify(defaultChannels));
        }
        if (!localStorage.getItem('wt_currentChannel')) {
            localStorage.setItem('wt_currentChannel', 'GENEL-1');
        }
    }
    initDatabase();

    let currentUser = JSON.parse(localStorage.getItem('wt_loggedUser')) || null;

    window.onload = function() {
        if (currentUser) {
            if (currentUser.isBanned) {
                alert('Hesabınız yasaklanmıştır!');
                handleLogout();
                return;
            }
            enterRadioApp();
        } else {
            switchScreen('loginScreen');
        }
    };

    function switchScreen(screenId) {
        document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
        document.getElementById(screenId).classList.add('active');
        if (screenId === 'channelScreen') renderChannels();
        if (screenId === 'adminScreen') renderAdminPanel();
    }

    function handleLogin() {
        const u = document.getElementById('loginUsername').value.trim();
        const p = document.getElementById('loginPassword').value.trim();

        if (!u || !p) {
            alert('Lütfen tüm alanları doldurun!');
            return;
        }

        let users = JSON.parse(localStorage.getItem('wt_users'));
        let found = users.find(x => x.username === u && x.password === p);

        if (found) {
            if (found.isBanned) {
                alert('Bu hesap yasaklanmıştır!');
                return;
            }
            currentUser = found;
            localStorage.setItem('wt_loggedUser', JSON.stringify(currentUser));
            enterRadioApp();
        } else {
            alert('Hatalı kullanıcı adı veya şifre!');
        }
    }

    function handleRegister() {
        const u = document.getElementById('regUsername').value.trim();
        const p = document.getElementById('regPassword').value.trim();

        if (!u || !p) {
            alert('Lütfen tüm alanları doldurun!');
            return;
        }

        let users = JSON.parse(localStorage.getItem('wt_users'));
        if (users.some(x => x.username === u)) {
            alert('Bu kullanıcı adı zaten alınmış!');
            return;
        }

        users.push({ username: u, password: p, role: 'user', isBanned: false });
        localStorage.setItem('wt_users', JSON.stringify(users));
        alert('Kayıt başarılı! Şimdi giriş yapabilirsiniz.');
        switchScreen('loginScreen');
    }

    function handleLogout() {
        localStorage.removeItem('wt_loggedUser');
        currentUser = null;
        switchScreen('loginScreen');
    }

    function enterRadioApp() {
        document.getElementById('userBadgeRole').innerText = currentUser.role.toUpperCase();
        if (currentUser.role === 'admin') {
            document.getElementById('adminNavBtn').style.display = 'flex';
        } else {
            document.getElementById('adminNavBtn').style.display = 'none';
        }
        updateLCDChannelDisplay();
        switchScreen('radioScreen');
    }

    let mediaRecorder = null;
    let audioChunks = [];

    navigator.mediaDevices?.getUserMedia({ audio: true }).then(stream => {
        mediaRecorder = new MediaRecorder(stream);
        mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
        mediaRecorder.onstop = () => {
            audioChunks = [];
        };
    }).catch(e => console.log("Mikrofon izni alınamadı:", e));

    function startTransmission(e) {
        e.preventDefault();
        const btn = document.getElementById('pttButton');
        const statusText = document.getElementById('lcdStatusText');
        
        btn.classList.add('active');
        statusText.innerText = "YAYINDA (TX)";
        statusText.style.color = "#c0392b";

        if (mediaRecorder && mediaRecorder.state === "inactive") {
            mediaRecorder.start();
        }
        playBeep(800, 100);
    }

    function stopTransmission(e) {
        e.preventDefault();
        const btn = document.getElementById('pttButton');
        const statusText = document.getElementById('lcdStatusText');
        
        btn.classList.remove('active');
        statusText.innerText = "BEKLEMEDE (RX)";
        statusText.style.color = "var(--lcd-text)";

        if (mediaRecorder && mediaRecorder.state === "recording") {
            mediaRecorder.stop();
        }
        playBeep(400, 100);
    }

    function playBeep(freq, duration) {
        try {
            const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.frequency.value = freq;
            osc.connect(gain);
            gain.connect(audioCtx.destination);
            osc.start();
            setTimeout(() => { osc.stop(); audioCtx.close(); }, duration);
        } catch(err) {}
    }

    function updateLCDChannelDisplay() {
        const currentChannel = localStorage.getItem('wt_currentChannel') || 'GENEL-1';
        document.getElementById('lcdChannelName').innerText = currentChannel;
    }

    function renderChannels() {
        const channels = JSON.parse(localStorage.getItem('wt_channels'));
        const currentChannel = localStorage.getItem('wt_currentChannel');
        const container = document.getElementById('channelListContainer');
        container.innerHTML = '';

        channels.forEach(ch => {
            const isCur = ch === currentChannel;
            container.innerHTML += `
                <div class="channel-pill ${isCur ? 'active' : ''}" onclick="selectChannel('${ch}')">
                    <span>📡 ${ch}</span>
                    <span style="font-size:12px; color: ${isCur ? 'var(--accent-yellow)' : 'var(--text-muted)'}">${isCur ? 'Aktif' : 'Bağlan'}</span>
                </div>
            `;
        });
    }

    function selectChannel(chName) {
        localStorage.setItem('wt_currentChannel', chName);
        updateLCDChannelDisplay();
        switchScreen('radioScreen');
    }

    function createChannel() {
        const nameInput = document.getElementById('newChannelName');
        const val = nameInput.value.trim().toUpperCase();
        if (!val) return;

        let channels = JSON.parse(localStorage.getItem('wt_channels'));
        if (channels.includes(val)) {
            alert('Bu kanal zaten mevcut!');
            return;
        }

        channels.push(val);
        localStorage.setItem('wt_channels', JSON.stringify(channels));
        nameInput.value = '';
        renderChannels();
    }

    function openAdminPanel() {
        if (currentUser.role !== 'admin') {
            alert('Yetkiniz yok!');
            return;
        }
        switchScreen('adminScreen');
    }

    function renderAdminPanel() {
        let users = JSON.parse(localStorage.getItem('wt_users'));
        const container = document.getElementById('adminUserList');
        container.innerHTML = '';

        document.getElementById('statTotalUsers').innerText = users.length;
        document.getElementById('statActiveChannel').innerText = localStorage.getItem('wt_currentChannel');

        users.forEach((usr, index) => {
            let badgeClass = usr.role === 'admin' ? 'badge-admin' : 'badge-user';
            if (usr.isBanned) badgeClass = 'badge-banned';

            container.innerHTML += `
                <div class="user-item">
                    <div class="user-info">
                        <div>${usr.username}</div>
                        <div>Rol: <span class="badge ${badgeClass}">${usr.isBanned ? 'YASAKLI' : usr.role}</span></div>
                    </div>
                    <div class="action-btns">
                        ${usr.username !== 'admin' ? `
                            <button class="btn-sm btn-warning" onclick="toggleRole(${index})">Rol Değiş</button>
                            <button class="btn-sm ${usr.isBanned ? 'btn-success' : 'btn-danger'}" onclick="toggleBan(${index})">
                                ${usr.isBanned ? 'Aç' : 'Yasakla'}
                            </button>
                        ` : '<span style="font-size:11px; color:var(--text-muted)">Root</span>'}
                    </div>
                </div>
            `;
        });
    }

    function toggleRole(index) {
        let users = JSON.parse(localStorage.getItem('wt_users'));
        users[index].role = users[index].role === 'admin' ? 'user' : 'admin';
        localStorage.setItem('wt_users', JSON.stringify(users));
        renderAdminPanel();
    }

    function toggleBan(index) {
        let users = JSON.parse(localStorage.getItem('wt_users'));
        users[index].isBanned = !users[index].isBanned;
        localStorage.setItem('wt_users', JSON.stringify(users));
        renderAdminPanel();
    }
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_CONTENT)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
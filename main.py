import os
import sys
import subprocess
import json
import random
import time
import string
import re
from datetime import datetime, timedelta
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
import tls_client
import uvicorn

# --- Auto-Installer for Dependencies ---
def install_and_import(package, import_name=None):
    if import_name is None:
        import_name = package
    try:
        __import__(import_name)
    except ImportError:
        print(f"\033[93m[!] Missing dependency '{package}'. Auto-installing now...\033[0m")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--quiet"])

install_and_import("fastapi")
install_and_import("uvicorn")
install_and_import("tls-client", "tls_client")
install_and_import("pydantic")

app = FastAPI()

# Key management functions
KEYS_FILE = "keys.txt"

def load_keys():
    """Load keys from file"""
    keys = {}
    if os.path.exists(KEYS_FILE):
        with open(KEYS_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if line and '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 2:
                        key = parts[0].strip()
                        duration = parts[1].strip()
                        if len(parts) >= 3:
                            expiry = parts[2].strip()
                            keys[key] = {"duration": duration, "expiry": expiry}
                        else:
                            expiry_date = calculate_expiry(duration)
                            keys[key] = {"duration": duration, "expiry": expiry_date}
    return keys

def save_keys(keys):
    """Save keys to file"""
    with open(KEYS_FILE, 'w') as f:
        for key, data in keys.items():
            f.write(f"{key} | {data['duration']} | {data['expiry']}\n")

def calculate_expiry(duration):
    """Calculate expiry date from duration string (e.g., 1d, 2h, 30m)"""
    now = datetime.now()
    if duration.endswith('d'):
        days = int(duration[:-1])
        expiry = now + timedelta(days=days)
    elif duration.endswith('h'):
        hours = int(duration[:-1])
        expiry = now + timedelta(hours=hours)
    elif duration.endswith('m'):
        minutes = int(duration[:-1])
        expiry = now + timedelta(minutes=minutes)
    else:
        expiry = now + timedelta(days=1)
    return expiry.strftime("%Y-%m-%d %H:%M:%S")

def is_key_valid(key):
    """Check if key exists and is not expired"""
    keys = load_keys()
    if key not in keys:
        return False
    expiry_str = keys[key]["expiry"]
    expiry = datetime.strptime(expiry_str, "%Y-%m-%d %H:%M:%S")
    return datetime.now() < expiry

def create_key(duration):
    """Create a new key"""
    key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
    keys = load_keys()
    expiry = calculate_expiry(duration)
    keys[key] = {"duration": duration, "expiry": expiry}
    save_keys(keys)
    return key, expiry

def delete_key(key):
    """Delete a key"""
    keys = load_keys()
    if key in keys:
        del keys[key]
        save_keys(keys)
        return True
    return False

def list_keys():
    """List all keys with their expiry"""
    keys = load_keys()
    return keys

# ==================== LOGIN HTML ====================
LOGIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>Alone_aaroosh GPT Gen PLUS| Key Verification</title>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Space Grotesk', sans-serif;
            background: #0a0000;
            min-height: 100vh;
            position: relative;
            overflow-x: hidden;
        }

        .bg-animation {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 0;
            overflow: hidden;
        }

        .gradient-sphere {
            position: absolute;
            width: 600px;
            height: 600px;
            border-radius: 50%;
            filter: blur(100px);
            opacity: 0.4;
            animation: float 20s infinite ease-in-out;
        }

        .sphere-1 {
            background: radial-gradient(circle, rgba(220,38,38,0.8), rgba(220,38,38,0));
            top: -200px;
            right: -200px;
            animation-delay: 0s;
        }

        .sphere-2 {
            background: radial-gradient(circle, rgba(185,28,28,0.6), rgba(185,28,28,0));
            bottom: -200px;
            left: -200px;
            animation-delay: -5s;
            width: 500px;
            height: 500px;
        }

        @keyframes float {
            0%, 100% { transform: translate(0, 0) rotate(0deg); }
            33% { transform: translate(30px, -30px) rotate(120deg); }
            66% { transform: translate(-20px, 20px) rotate(240deg); }
        }

        .container {
            position: relative;
            z-index: 1;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        .glass-card {
            max-width: 450px;
            width: 100%;
            background: rgba(10, 0, 0, 0.85);
            backdrop-filter: blur(25px);
            border-radius: 32px;
            border: 1px solid rgba(220,38,38,0.3);
            padding: 45px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.8);
            animation: slideUp 0.8s cubic-bezier(0.16, 1, 0.3, 1);
        }

        @keyframes slideUp {
            from {
                opacity: 0;
                transform: translateY(40px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .header {
            text-align: center;
            margin-bottom: 35px;
        }

        .badge {
            display: inline-block;
            background: linear-gradient(135deg, rgba(220,38,38,0.2), rgba(127,29,29,0.1));
            padding: 8px 18px;
            border-radius: 100px;
            font-size: 11px;
            font-weight: 600;
            color: #ef4444;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 20px;
            border: 1px solid rgba(220,38,38,0.4);
        }

        .header h1 {
            font-size: 42px;
            font-weight: 700;
            background: linear-gradient(135deg, #ffffff 0%, #ef4444 40%, #dc2626 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 12px;
        }

        .header p {
            color: #9ca3af;
            font-size: 14px;
        }

        .form-group {
            margin-bottom: 24px;
        }

        .label {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 12px;
            font-weight: 600;
            color: #d1d5db;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }

        input {
            width: 100%;
            background: rgba(0, 0, 0, 0.5);
            border: 1px solid rgba(220,38,38,0.3);
            border-radius: 16px;
            color: #ffffff;
            padding: 14px 18px;
            font-size: 14px;
            outline: none;
            transition: all 0.3s;
            font-family: monospace;
        }

        input:focus {
            border-color: #ef4444;
            box-shadow: 0 0 0 3px rgba(239,68,68,0.1);
            background: rgba(0, 0, 0, 0.7);
        }

        .btn-submit {
            width: 100%;
            background: linear-gradient(135deg, #dc2626, #991b1b);
            color: white;
            border: none;
            border-radius: 16px;
            padding: 16px;
            font-size: 16px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .btn-submit:hover {
            transform: translateY(-2px);
            box-shadow: 0 20px 30px -12px rgba(220,38,38,0.5);
        }

        .error-msg {
            color: #ef4444;
            font-size: 13px;
            text-align: center;
            margin-top: 16px;
            font-weight: 500;
            display: none;
            padding: 12px;
            background: rgba(239,68,68,0.1);
            border-radius: 12px;
            border: 1px solid rgba(239,68,68,0.3);
        }

        .admin-section {
            margin-top: 30px;
            padding-top: 30px;
            border-top: 1px solid rgba(220,38,38,0.2);
        }

        .admin-title {
            color: #ef4444;
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 15px;
            text-align: center;
        }

        .key-list {
            background: rgba(0, 0, 0, 0.4);
            border-radius: 12px;
            padding: 15px;
            margin-top: 15px;
            max-height: 300px;
            overflow-y: auto;
        }

        .key-item {
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(220,38,38,0.2);
            border-radius: 8px;
            padding: 10px;
            margin-bottom: 8px;
            font-size: 12px;
            font-family: monospace;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .key-code {
            color: #22c55e;
            word-break: break-all;
            flex: 1;
        }

        .key-expiry {
            color: #fbbf24;
            font-size: 10px;
            margin-left: 10px;
        }

        .delete-btn {
            background: rgba(239,68,68,0.2);
            border: 1px solid rgba(239,68,68,0.3);
            color: #ef4444;
            padding: 4px 8px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 11px;
            margin-left: 10px;
        }

        .delete-btn:hover {
            background: rgba(239,68,68,0.4);
        }

        .create-key-area {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }

        .create-key-area select {
            flex: 1;
            background: rgba(0, 0, 0, 0.5);
            border: 1px solid rgba(220,38,38,0.3);
            border-radius: 12px;
            color: white;
            padding: 10px;
        }

        .create-key-area button {
            background: linear-gradient(135deg, #22c55e, #16a34a);
            padding: 10px 20px;
            border: none;
            border-radius: 12px;
            color: white;
            cursor: pointer;
            font-weight: 600;
        }

        .new-key-display {
            background: rgba(34,197,94,0.1);
            border: 1px solid rgba(34,197,94,0.3);
            border-radius: 8px;
            padding: 10px;
            margin-top: 10px;
            display: none;
        }

        hr {
            border-color: rgba(220,38,38,0.2);
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="bg-animation">
        <div class="gradient-sphere sphere-1"></div>
        <div class="gradient-sphere sphere-2"></div>
    </div>

    <div class="container">
        <div class="glass-card">
            <div class="header">
                <div class="badge">🔐 SECURE ACCESS</div>
                <h1>Alone_aaroosh GPT Gen PLUS</h1>
                <p>Enter your license key to continue</p>
            </div>

            <div class="form-group">
                <div class="label">🔑 License Key</div>
                <input type="text" id="licenseKey" placeholder="Enter your 16-digit license key" autocomplete="off">
            </div>

            <button class="btn-submit" onclick="verifyKey()">Verify & Continue</button>
            <div id="errorMsg" class="error-msg"></div>

            <div id="adminPanel" style="display: none;">
                <hr>
                <div class="admin-section">
                    <div class="admin-title">⚙️ ADMIN PANEL</div>
                    
                    <div class="create-key-area">
                        <select id="durationSelect">
                            <option value="1h">1 Hour</option>
                            <option value="6h">6 Hours</option>
                            <option value="12h">12 Hours</option>
                            <option value="1d" selected>1 Day</option>
                            <option value="2d">2 Days</option>
                            <option value="3d">3 Days</option>
                            <option value="5d">5 Days</option>
                            <option value="7d">7 Days</option>
                            <option value="14d">14 Days</option>
                            <option value="30d">30 Days</option>
                        </select>
                        <button onclick="createNewKey()">➕ Create Key</button>
                    </div>
                    <div id="newKeyDisplay" class="new-key-display"></div>
                    
                    <div class="key-list" id="keyList">
                        <div style="text-align: center; color: #666;">Loading keys...</div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        async function verifyKey() {
            const key = document.getElementById('licenseKey').value.trim();
            const errorMsg = document.getElementById('errorMsg');
            
            if (!key) {
                errorMsg.innerText = '❌ Please enter your license key';
                errorMsg.style.display = 'block';
                return;
            }

            errorMsg.style.display = 'none';

            try {
                const response = await fetch('/verify', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ key: key })
                });
                const data = await response.json();

                if (data.success) {
                    sessionStorage.setItem('sparky_key', key);
                    window.location.href = '/generator';
                } else {
                    errorMsg.innerText = '❌ ' + data.error;
                    errorMsg.style.display = 'block';
                }
            } catch (e) {
                errorMsg.innerText = '❌ Connection error';
                errorMsg.style.display = 'block';
            }
        }

        async function loadAdminPanel() {
            const key = document.getElementById('licenseKey').value.trim();
            if (key === 'Alone_aaroosh67') {
                document.getElementById('adminPanel').style.display = 'block';
                loadKeys();
            }
        }

        async function loadKeys() {
            try {
                const response = await fetch('/admin/keys');
                const data = await response.json();
                const keyList = document.getElementById('keyList');
                
                if (data.keys && Object.keys(data.keys).length > 0) {
                    keyList.innerHTML = '';
                    for (const [key, info] of Object.entries(data.keys)) {
                        const keyDiv = document.createElement('div');
                        keyDiv.className = 'key-item';
                        keyDiv.innerHTML = `
                            <span class="key-code">${key}</span>
                            <span class="key-expiry">Expires: ${info.expiry}</span>
                            <button class="delete-btn" onclick="deleteKey('${key}')">Delete</button>
                        `;
                        keyList.appendChild(keyDiv);
                    }
                } else {
                    keyList.innerHTML = '<div style="text-align: center; color: #666;">No keys found</div>';
                }
            } catch (e) {
                console.error('Failed to load keys');
            }
        }

        async function createNewKey() {
            const duration = document.getElementById('durationSelect').value;
            try {
                const response = await fetch('/admin/create', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ duration: duration })
                });
                const data = await response.json();
                
                if (data.success) {
                    const display = document.getElementById('newKeyDisplay');
                    display.innerHTML = `
                        <strong>✅ New Key Created!</strong><br>
                        Key: <code style="color: #22c55e;">${data.key}</code><br>
                        Expires: ${data.expiry}
                    `;
                    display.style.display = 'block';
                    loadKeys();
                    setTimeout(() => {
                        display.style.display = 'none';
                    }, 10000);
                }
            } catch (e) {
                alert('Failed to create key');
            }
        }

        async function deleteKey(key) {
            if (confirm('Delete this key?')) {
                try {
                    const response = await fetch('/admin/delete', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ key: key })
                    });
                    const data = await response.json();
                    if (data.success) {
                        loadKeys();
                    }
                } catch (e) {
                    alert('Failed to delete key');
                }
            }
        }

        document.getElementById('licenseKey').addEventListener('input', function() {
            if (this.value === 'Alone_aaroosh67') {
                loadAdminPanel();
            } else {
                document.getElementById('adminPanel').style.display = 'none';
            }
        });

        async function checkExistingKey() {
            const key = sessionStorage.getItem('sparky_key');
            if (key) {
                try {
                    const response = await fetch('/verify', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ key: key })
                    });
                    const data = await response.json();
                    if (data.success) {
                        window.location.href = '/generator';
                    }
                } catch (e) {}
            }
        }
        checkExistingKey();
    </script>
</body>
</html>
"""

# ==================== GENERATOR HTML ====================
GENERATOR_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>Alone_aaroosh GPT Gen PLUS | Premium gpt+ checkouterr</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://unpkg.com/lucide@latest"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            cursor: none;
        }

        body {
            font-family: 'Space Grotesk', sans-serif;
            background: #0a0000;
            min-height: 100vh;
            position: relative;
            overflow-x: hidden;
        }

        .custom-cursor {
            width: 8px;
            height: 8px;
            background: #ff0000;
            border-radius: 50%;
            position: fixed;
            pointer-events: none;
            z-index: 10000;
            transition: transform 0.1s ease;
            box-shadow: 0 0 15px #ff0000, 0 0 30px rgba(255,0,0,0.5);
            animation: pulse 2s infinite;
        }

        .cursor-glow {
            width: 40px;
            height: 40px;
            background: radial-gradient(circle, rgba(255,0,0,0.3), transparent);
            border-radius: 50%;
            position: fixed;
            pointer-events: none;
            z-index: 9999;
            transition: transform 0.05s ease;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.7; transform: scale(1.2); }
        }

        .bg-animation {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 0;
            overflow: hidden;
        }

        .gradient-sphere {
            position: absolute;
            width: 600px;
            height: 600px;
            border-radius: 50%;
            filter: blur(100px);
            opacity: 0.4;
            animation: float 20s infinite ease-in-out;
        }

        .sphere-1 {
            background: radial-gradient(circle, rgba(220,38,38,0.8), rgba(220,38,38,0));
            top: -200px;
            right: -200px;
            animation-delay: 0s;
        }

        .sphere-2 {
            background: radial-gradient(circle, rgba(185,28,28,0.6), rgba(185,28,28,0));
            bottom: -200px;
            left: -200px;
            animation-delay: -5s;
            width: 500px;
            height: 500px;
        }

        .sphere-3 {
            background: radial-gradient(circle, rgba(127,29,29,0.4), rgba(127,29,29,0));
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 800px;
            height: 800px;
            animation-delay: -10s;
        }

        @keyframes float {
            0%, 100% { transform: translate(0, 0) rotate(0deg); }
            33% { transform: translate(30px, -30px) rotate(120deg); }
            66% { transform: translate(-20px, 20px) rotate(240deg); }
        }

        .grid-pattern {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: linear-gradient(rgba(220,38,38,0.03) 1px, transparent 1px),
                              linear-gradient(90deg, rgba(220,38,38,0.03) 1px, transparent 1px);
            background-size: 50px 50px;
            z-index: 0;
        }

        .container {
            position: relative;
            z-index: 1;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        .glass-card {
            max-width: 650px;
            width: 100%;
            background: rgba(10, 0, 0, 0.75);
            backdrop-filter: blur(25px);
            border-radius: 32px;
            border: 1px solid rgba(220,38,38,0.3);
            padding: 45px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.8);
            animation: slideUp 0.8s cubic-bezier(0.16, 1, 0.3, 1);
            transition: all 0.4s;
        }

        .glass-card:hover {
            transform: translateY(-5px);
        }

        @keyframes slideUp {
            from { opacity: 0; transform: translateY(40px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .header {
            text-align: center;
            margin-bottom: 40px;
        }

        .badge {
            display: inline-block;
            background: linear-gradient(135deg, rgba(220,38,38,0.2), rgba(127,29,29,0.1));
            padding: 8px 18px;
            border-radius: 100px;
            font-size: 11px;
            font-weight: 600;
            color: #ef4444;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 20px;
            border: 1px solid rgba(220,38,38,0.4);
        }

        .header h1 {
            font-size: 48px;
            font-weight: 700;
            background: linear-gradient(135deg, #ffffff 0%, #ef4444 40%, #dc2626 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 12px;
        }

        .header p {
            color: #9ca3af;
            font-size: 14px;
        }

        .logout-btn {
            position: absolute;
            top: 20px;
            right: 20px;
            background: rgba(220,38,38,0.2);
            border: 1px solid rgba(220,38,38,0.3);
            color: #ef4444;
            padding: 8px 16px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 12px;
            font-weight: 600;
            transition: all 0.3s;
            z-index: 100;
        }

        .logout-btn:hover {
            background: rgba(220,38,38,0.4);
        }

        .form-group { margin-bottom: 24px; }
        .label-wrap { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
        .label { display: flex; align-items: center; gap: 8px; font-size: 12px; font-weight: 600; color: #d1d5db; text-transform: uppercase; }
        .btn-link { background: none; border: none; color: #ef4444; font-size: 11px; font-weight: 600; cursor: pointer; padding: 4px 8px; border-radius: 8px; }
        .btn-link:hover { background: rgba(239,68,68,0.1); }
        
        textarea { 
            width: 100%; 
            background: rgba(0, 0, 0, 0.5); 
            border: 1px solid rgba(220,38,38,0.3); 
            border-radius: 16px; 
            color: #ffffff; 
            padding: 14px 18px; 
            font-size: 14px; 
            outline: none; 
            transition: all 0.3s; 
            height: 180px; 
            resize: vertical; 
            font-family: monospace; 
            font-size: 12px; 
        }
        
        textarea:focus { 
            border-color: #ef4444; 
            box-shadow: 0 0 0 3px rgba(239,68,68,0.1); 
            background: rgba(0, 0, 0, 0.7); 
        }

        .selector-group {
            margin-bottom: 20px;
        }

        .selector-label {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 12px;
            font-weight: 600;
            color: #d1d5db;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 12px;
        }

        .region-selector {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
        }

        .region-option {
            position: relative;
            cursor: pointer;
        }

        .region-option input {
            position: absolute;
            opacity: 0;
            cursor: pointer;
        }

        .region-card {
            background: rgba(0, 0, 0, 0.4);
            border: 1px solid rgba(220,38,38,0.2);
            border-radius: 14px;
            padding: 12px;
            text-align: center;
            transition: all 0.3s;
            cursor: pointer;
        }

        .region-option input:checked + .region-card {
            background: linear-gradient(135deg, rgba(220,38,38,0.2), rgba(127,29,29,0.1));
            border-color: #ef4444;
            box-shadow: 0 0 15px rgba(239,68,68,0.3);
            transform: translateY(-2px);
        }

        .region-option:hover .region-card {
            border-color: #ef4444;
            background: rgba(220,38,38,0.1);
            transform: translateY(-2px);
        }

        .region-flag {
            font-size: 24px;
            margin-bottom: 5px;
        }

        .region-name {
            font-size: 11px;
            font-weight: 600;
            color: #ffffff;
        }

        .region-currency {
            font-size: 9px;
            color: #9ca3af;
            margin-top: 3px;
        }

        .link-selector {
            display: flex;
            gap: 15px;
            background: rgba(0, 0, 0, 0.4);
            border-radius: 16px;
            padding: 6px;
            border: 1px solid rgba(220,38,38,0.2);
        }

        .link-option {
            flex: 1;
            text-align: center;
            padding: 12px;
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.3s;
            position: relative;
            overflow: hidden;
        }

        .link-option.active {
            background: linear-gradient(135deg, #dc2626, #991b1b);
            box-shadow: 0 5px 15px rgba(220,38,38,0.3);
        }

        .link-option.active .link-icon,
        .link-option.active .link-text {
            color: white;
        }

        .link-option:not(.active):hover {
            background: rgba(220,38,38,0.1);
        }

        .link-icon {
            font-size: 20px;
            display: block;
            margin-bottom: 5px;
            color: #9ca3af;
            transition: all 0.3s;
        }

        .link-text {
            font-size: 11px;
            font-weight: 600;
            color: #9ca3af;
            transition: all 0.3s;
        }

        .grid-2 {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }

        .btn-generate { 
            width: 100%; 
            background: linear-gradient(135deg, #dc2626, #991b1b); 
            color: white; 
            border: none; 
            border-radius: 16px; 
            padding: 16px; 
            font-size: 15px; 
            font-weight: 700; 
            cursor: pointer; 
            transition: all 0.3s; 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            gap: 10px; 
            margin-top: 8px; 
            text-transform: uppercase; 
        }
        
        .btn-generate:hover { 
            transform: translateY(-2px); 
            box-shadow: 0 20px 30px -12px rgba(220,38,38,0.5); 
        }
        
        .btn-generate:disabled { 
            opacity: 0.6; 
            cursor: not-allowed; 
        }
        
        .loader { 
            width: 18px; 
            height: 18px; 
            border: 2px solid rgba(255,255,255,0.3); 
            border-radius: 50%; 
            border-top-color: #fff; 
            animation: spin 0.8s linear infinite; 
            display: none; 
        }
        
        @keyframes spin { 
            to { transform: rotate(360deg); } 
        }
        
        #result-container { 
            margin-top: 32px; 
            display: none; 
            animation: fadeInUp 0.5s ease; 
        }
        
        @keyframes fadeInUp { 
            from { opacity: 0; transform: translateY(20px); } 
            to { opacity: 1; transform: translateY(0); } 
        }
        
        .result-card { 
            background: linear-gradient(135deg, rgba(34,197,94,0.08), rgba(34,197,94,0.02)); 
            border: 1px solid rgba(34,197,94,0.3); 
            border-radius: 24px; 
            padding: 24px; 
            position: relative; 
            overflow: hidden; 
        }
        
        .result-card::before { 
            content: ''; 
            position: absolute; 
            top: 0; 
            left: 0; 
            right: 0; 
            height: 2px; 
            background: linear-gradient(90deg, transparent, #22c55e, transparent); 
            animation: shimmer 2s infinite; 
        }
        
        @keyframes shimmer { 
            0% { transform: translateX(-100%); } 
            100% { transform: translateX(100%); } 
        }
        
        .result-header { 
            display: flex; 
            align-items: center; 
            gap: 10px; 
            margin-bottom: 16px; 
        }
        
        .result-header span { 
            font-size: 14px; 
            font-weight: 600; 
            color: #22c55e; 
            text-transform: uppercase; 
        }
        
        .result-meta { 
            margin-left: auto; 
            font-size: 11px; 
            color: #6b7280; 
        }
        
        .link-row { 
            background: rgba(0,0,0,0.4); 
            border: 1px solid rgba(34,197,94,0.2); 
            border-radius: 14px; 
            padding: 12px 16px; 
            display: flex; 
            align-items: center; 
            gap: 12px; 
            margin: 16px 0; 
        }
        
        .link-row input { 
            background: transparent; 
            border: none; 
            padding: 0; 
            font-family: monospace; 
            font-size: 12px; 
            color: #22c55e; 
            width: 100%; 
            outline: none; 
        }
        
        .btn-icon { 
            background: rgba(34,197,94,0.1); 
            border: 1px solid rgba(34,197,94,0.3); 
            border-radius: 10px; 
            padding: 8px; 
            color: #22c55e; 
            cursor: pointer; 
            transition: all 0.2s; 
        }
        
        .btn-icon:hover { 
            background: rgba(34,197,94,0.2); 
            transform: scale(1.05); 
        }
        
        .btn-action { 
            width: 100%; 
            padding: 14px; 
            border-radius: 14px; 
            font-size: 14px; 
            font-weight: 600; 
            cursor: pointer; 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            gap: 8px; 
            border: none; 
            transition: all 0.2s; 
            background: linear-gradient(135deg, #22c55e, #16a34a); 
            color: white; 
        }
        
        .btn-action:hover { 
            transform: translateY(-2px); 
            box-shadow: 0 10px 20px -10px rgba(34,197,94,0.5); 
        }
        
        #error-msg { 
            color: #ef4444; 
            font-size: 13px; 
            text-align: center; 
            margin-top: 16px; 
            display: none; 
            padding: 12px; 
            background: rgba(239,68,68,0.1); 
            border-radius: 12px; 
        }
        
        .particles { 
            position: fixed; 
            top: 0; 
            left: 0; 
            width: 100%; 
            height: 100%; 
            pointer-events: none; 
            z-index: 0; 
        }
        
        .particle { 
            position: absolute; 
            background: rgba(239,68,68,0.3); 
            border-radius: 50%; 
            animation: floatParticle 15s infinite linear; 
        }
        
        @keyframes floatParticle { 
            from { transform: translateY(100vh) rotate(0deg); opacity: 0; } 
            10% { opacity: 1; } 
            90% { opacity: 0.5; } 
            to { transform: translateY(-100vh) rotate(360deg); opacity: 0; } 
        }
        
        @media (max-width: 640px) { 
            .glass-card { padding: 30px 24px; } 
            .header h1 { font-size: 36px; } 
            .grid-2 { grid-template-columns: 1fr; gap: 0; }
            .region-selector { grid-template-columns: repeat(2, 1fr); }
        }
        
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: #1a0000; }
        ::-webkit-scrollbar-thumb { background: #dc2626; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="custom-cursor" id="customCursor"></div>
    <div class="cursor-glow" id="cursorGlow"></div>
    <button class="logout-btn" onclick="logout()">🚪 Logout</button>
    
    <div class="bg-animation">
        <div class="gradient-sphere sphere-1"></div>
        <div class="gradient-sphere sphere-2"></div>
        <div class="gradient-sphere sphere-3"></div>
        <div class="grid-pattern"></div>
    </div>
    <div class="particles" id="particles"></div>

    <div class="container">
        <div class="glass-card">
            <div class="header">
                <div class="badge">⚡ PREMIUM GENERATOR</div>
                <h1>Alone_aaroosh GPT Gen PLUS</h1>
                <p>Enterprise-grade session linker with instant checkout</p>
            </div>

            <div class="form-group">
                <div class="label-wrap">
                    <div class="label"><i data-lucide="key" style="width: 14px;"></i> Auth Session</div>
                    <button class="btn-link" onclick="window.open('https://chatgpt.com/api/auth/session', '_blank')">Get Token</button>
                </div>
                <textarea id="sessionInput" placeholder='Paste your ChatGPT authentication JSON here...'></textarea>
            </div>

            <div class="grid-2">
                <div class="selector-group">
                    <div class="selector-label">
                        <i data-lucide="globe" style="width: 14px;"></i> Select Region
                    </div>
                    <div class="region-selector" id="regionSelector">
                        <label class="region-option">
                            <input type="radio" name="region" value="India" checked>
                            <div class="region-card">
                                <div class="region-flag">🇮🇳</div>
                                <div class="region-name">India</div>
                                <div class="region-currency">INR</div>
                            </div>
                        </label>
                        <label class="region-option">
                            <input type="radio" name="region" value="Indonesia">
                            <div class="region-card">
                                <div class="region-flag">🇮🇩</div>
                                <div class="region-name">Indonesia</div>
                                <div class="region-currency">IDR</div>
                            </div>
                        </label>
                        <label class="region-option">
                            <input type="radio" name="region" value="Malaysia">
                            <div class="region-card">
                                <div class="region-flag">🇲🇾</div>
                                <div class="region-name">Malaysia</div>
                                <div class="region-currency">MYR</div>
                            </div>
                        </label>
                        <label class="region-option">
                            <input type="radio" name="region" value="Thailand">
                            <div class="region-card">
                                <div class="region-flag">🇹🇭</div>
                                <div class="region-name">Thailand</div>
                                <div class="region-currency">THB</div>
                            </div>
                        </label>
                        <label class="region-option">
                            <input type="radio" name="region" value="Vietnam">
                            <div class="region-card">
                                <div class="region-flag">🇻🇳</div>
                                <div class="region-name">Vietnam</div>
                                <div class="region-currency">VND</div>
                            </div>
                        </label>
                    </div>
                </div>

                <div class="selector-group">
                    <div class="selector-label">
                        <i data-lucide="link" style="width: 14px;"></i> Link Type
                    </div>
                    <div class="link-selector" id="linkSelector">
                        <div class="link-option active" data-value="shortlink">
                            <div class="link-icon">🔗</div>
                            <div class="link-text">ChatGPT Redirect</div>
                        </div>
                        <div class="link-option" data-value="longlink">
                            <div class="link-icon">💳</div>
                            <div class="link-text">Direct Stripe</div>
                        </div>
                    </div>
                </div>
            </div>

            <button id="generateBtn" class="btn-generate" onclick="generate()">
                <div id="loader" class="loader"></div>
                <i data-lucide="zap" id="rocket-icon" style="width: 18px;"></i>
                <span id="btn-text">Generate Secure Link</span>
            </button>

            <div id="error-msg"></div>
            <div id="result-container">
                <div class="result-card">
                    <div class="result-header">
                        <i data-lucide="check-circle" style="width: 18px;"></i>
                        <span>Checkout Ready</span>
                        <span class="result-meta" id="result-meta"></span>
                    </div>
                    <div class="link-row">
                        <input type="text" id="resultUrl" readonly>
                        <button class="btn-icon" onclick="copyResult()"><i data-lucide="copy" style="width: 16px;"></i></button>
                    </div>
                    <button class="btn-action" onclick="openResult()"><i data-lucide="external-link"></i> Launch Checkout</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        lucide.createIcons();

        const customCursor = document.getElementById('customCursor');
        const cursorGlow = document.getElementById('cursorGlow');
        document.addEventListener('mousemove', (e) => {
            customCursor.style.transform = `translate(${e.clientX - 4}px, ${e.clientY - 4}px)`;
            cursorGlow.style.transform = `translate(${e.clientX - 20}px, ${e.clientY - 20}px)`;
        });

        document.querySelectorAll('button, select, textarea, .btn-link, .region-option, .link-option').forEach(el => {
            el.addEventListener('mouseenter', () => { customCursor.style.transform = 'scale(1.5)'; customCursor.style.background = '#ff3333'; });
            el.addEventListener('mouseleave', () => { customCursor.style.transform = 'scale(1)'; customCursor.style.background = '#ff0000'; });
        });

        const linkOptions = document.querySelectorAll('.link-option');
        let selectedLinkType = 'shortlink';

        linkOptions.forEach(option => {
            option.addEventListener('click', function() {
                linkOptions.forEach(opt => opt.classList.remove('active'));
                this.classList.add('active');
                selectedLinkType = this.getAttribute('data-value');
            });
        });

        function getSelectedRegion() {
            const selected = document.querySelector('input[name="region"]:checked');
            return selected ? selected.value : 'India';
        }

        function createParticles() {
            const container = document.getElementById('particles');
            for(let i = 0; i < 60; i++) {
                const p = document.createElement('div');
                p.classList.add('particle');
                p.style.width = (Math.random() * 3 + 1) + 'px';
                p.style.height = p.style.width;
                p.style.left = Math.random() * 100 + '%';
                p.style.animationDelay = Math.random() * 15 + 's';
                p.style.animationDuration = Math.random() * 10 + 10 + 's';
                p.style.opacity = Math.random() * 0.4;
                p.style.background = `rgba(239,68,68,${Math.random() * 0.5})`;
                container.appendChild(p);
            }
        }
        createParticles();
        setInterval(() => lucide.createIcons(), 100);

        async function generate() {
            const session = document.getElementById('sessionInput').value.trim();
            const region = getSelectedRegion();
            const method = selectedLinkType;
            const btn = document.getElementById('generateBtn');
            const loader = document.getElementById('loader');
            const icon = document.getElementById('rocket-icon');
            const btnText = document.getElementById('btn-text');
            const errorMsg = document.getElementById('error-msg');
            const resultArea = document.getElementById('result-container');

            if (!session) {
                errorMsg.innerText = '⚠️ Please paste your session token first';
                errorMsg.style.display = 'block';
                setTimeout(() => errorMsg.style.display = 'none', 3000);
                return;
            }

            btn.disabled = true;
            loader.style.display = 'block';
            icon.style.display = 'none';
            btnText.innerText = 'Processing...';
            errorMsg.style.display = 'none';
            resultArea.style.display = 'none';

            try {
                const response = await fetch('/gpt/payment', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ plan: 'plus', payment: method, currency: region, session: session })
                });
                const data = await response.json();
                
                if (data.success) {
                    document.getElementById('resultUrl').value = data.url;
                    document.getElementById('result-meta').innerHTML = `🌍 ${data.details.region} • ⚡ Ready`;
                    resultArea.style.display = 'block';
                    resultArea.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                } else {
                    errorMsg.innerText = '❌ ' + data.error;
                    errorMsg.style.display = 'block';
                }
            } catch (e) {
                errorMsg.innerText = '❌ Connection error';
                errorMsg.style.display = 'block';
            } finally {
                btn.disabled = false;
                loader.style.display = 'none';
                icon.style.display = 'block';
                btnText.innerText = 'Generate Secure Link';
            }
        }

        function copyResult() {
            const input = document.getElementById('resultUrl');
            input.select();
            document.execCommand('copy');
            alert('Copied!');
        }

        function openResult() {
            const url = document.getElementById('resultUrl').value;
            if(url) window.open(url, '_blank');
        }

        function logout() {
            sessionStorage.removeItem('sparky_key');
            window.location.href = '/';
        }

        if (!sessionStorage.getItem('sparky_key')) {
            window.location.href = '/';
        }
    </script>
</body>
</html>
"""

# ==================== BACKEND LOGIC ====================
REGIONS = [
    {"key": "India", "label": "India (INR)", "currency": "INR", "country": "IN"},
    {"key": "Indonesia", "label": "Indonesia (IDR)", "currency": "IDR", "country": "ID"},
    {"key": "Malaysia", "label": "Malaysia (MYR)", "currency": "MYR", "country": "MY"},
    {"key": "Thailand", "label": "Thailand (THB)", "currency": "THB", "country": "TH"},
    {"key": "Vietnam", "label": "Vietnam (VND)", "currency": "VND", "country": "VN"},
]
REGION_MAP = {r["key"]: r for r in REGIONS}

class PaymentRequest(BaseModel):
    plan: str
    payment: str
    currency: str
    session: str

class VerifyRequest(BaseModel):
    key: str

class CreateKeyRequest(BaseModel):
    duration: str

class DeleteKeyRequest(BaseModel):
    key: str

def extract_token(user_input):
    try:
        data = json.loads(user_input)
        if "accessToken" in data:
            return data["accessToken"]
        match = re.search(r'"accessToken":"([^"]+)"', user_input)
        if match:
            return match.group(1)
    except:
        pass
    return user_input.strip()

def get_proxy_url(country="TH"):
    rnd = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"http://9ti17wiju-country-{country}-session-{rnd}-time-5:pWOoqnP41K8@global.nullproxies.com:8080"

# Routes
@app.get("/")
async def login_page():
    return HTMLResponse(content=LOGIN_HTML)

@app.get("/generator")
async def generator_page():
    return HTMLResponse(content=GENERATOR_HTML)

@app.post("/verify")
async def verify_key(request: VerifyRequest):
    if is_key_valid(request.key):
        return {"success": True}
    return {"success": False, "error": "Invalid or expired license key"}

@app.get("/admin/keys")
async def admin_list_keys():
    keys = list_keys()
    return {"keys": keys}

@app.post("/admin/create")
async def admin_create_key(request: CreateKeyRequest):
    key, expiry = create_key(request.duration)
    return {"success": True, "key": key, "expiry": expiry}

@app.post("/admin/delete")
async def admin_delete_key(request: DeleteKeyRequest):
    if delete_key(request.key):
        return {"success": True}
    return {"success": False}

@app.post("/gpt/payment")
def generate_payment(req: PaymentRequest):
    try:
        token = extract_token(req.session)
        region_info = REGION_MAP.get(req.currency, REGION_MAP["India"])
        session = tls_client.Session(client_identifier="chrome_120", random_tls_extension_order=True)
        proxy_url = get_proxy_url(country="TH")
        session.proxies = {"http": proxy_url, "https": proxy_url}
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        
        promo_id = "plus-1-month-free"
        try:
            r_check = session.get('https://chatgpt.com/backend-api/accounts/check/v4-2023-04-27', headers=headers, timeout_seconds=10)
            if r_check.status_code == 200:
                accs = r_check.json().get("accounts", {})
                for a_id, a_info in accs.items():
                    ps = a_info.get("eligible_promo_campaigns", {})
                    if "plus" in ps:
                        promo_id = ps["plus"].get("id")
                        break
        except:
            pass

        payload = {
            "plan_name": "chatgptplusplan",
            "entry_point": "all_plans_pricing_modal",
            "checkout_ui_mode": "custom",
            "billing_details": {"country": region_info["country"], "currency": region_info["currency"]},
            "promo_campaign": {"promo_campaign_id": promo_id, "is_coupon_from_query_param": False}
        }
        r = session.post('https://chatgpt.com/backend-api/payments/checkout', headers=headers, json=payload, timeout_seconds=15)
        
        if r.status_code == 200:
            cs_id = r.json().get("checkout_session_id")
            if cs_id:
                chat_url = f"https://chatgpt.com/checkout/openai_llc/{cs_id}"
                strip_url = f"https://pay.openai.com/c/pay/{cs_id}"
                return {
                    "success": True,
                    "url": strip_url if req.payment == "longlink" else chat_url,
                    "details": {"region": region_info["label"]}
                }
        return {"success": False, "error": f"OpenAI Error {r.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"\033[92m✅ Server running on port {port}\033[0m")
    print(f"\033[94m🌐 Your app is live at: https://{os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'localhost')}\033[0m")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
    print("\033[91m" + "="*60 + "\033[0m")
    print("\033[91m🔥 ALONE_AAROOSH GPT GEN PLUS - Premium Session Linker 🔥\033[0m")
    print("\033[91m" + "="*60 + "\033[0m")
    print("\033[95m🚀 Server Status: Active\033[0m")
    print("\033[94m🌐 Local URL: http://localhost:8000\033[0m")
    print("\033[94m🌍 Network URL: http://0.0.0.0:8000\033[0m")
    print("\033[93m🔑 Key System Active - Users need valid key to access\033[0m")
    print("\033[93m👑 Admin Panel: Enter 'Alone_aaroosh67' in key field\033[0m")
    print("\033[91m" + "="*60 + "\033[0m")
    print("\033[33m💡 Press Ctrl+C to stop the server\033[0m")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="error")

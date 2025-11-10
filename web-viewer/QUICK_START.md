# ARVOS Web Viewer - Quick Start

## 🚀 The Easy Way (Recommended)

**Just run the start script:**

```bash
./start-viewer.sh
```

This will:
1. ✅ Auto-detect your computer's IP address
2. ✅ Open browser with correct IP (not localhost)
3. ✅ Generate working QR code automatically
4. ✅ Start the web server

## 🔧 Manual Setup (If Needed)

### Step 1: Find Your Computer's IP Address

**macOS/Linux:**
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
```

**Windows:**
```bash
ipconfig
```

Look for something like: `192.168.1.X` or `10.0.0.X`

### Step 2: Start the Server

```bash
python3 -m http.server 8000
```

### Step 3: Open Browser with IP Address

**IMPORTANT:** Use your IP address, NOT localhost!

```
✅ CORRECT:   http://192.168.1.123:8000
❌ WRONG:     http://localhost:8000
```

## ⚠️ Troubleshooting QR Code Issues

### Problem: QR code shows "YOUR_COMPUTER_IP"

**Cause:** You opened the page with `localhost` or `file://`

**Solution:**
1. Find your IP: `ifconfig | grep "inet "`
2. Open browser: `http://YOUR_ACTUAL_IP:8000`
3. QR code will now have the real IP!

### Problem: WebRTC detection fails

**Solution:**
1. The page will show a manual input field after 5 seconds
2. Type your IP address (e.g., `192.168.1.123`)
3. QR code updates automatically

## 📱 Testing the Connection

1. Open `http://YOUR_IP:8000` in browser
2. Open browser console (F12)
3. Look for: `✅ Detected IP: 192.168.1.X`
4. Scan QR code with iPhone
5. iPhone should connect to your computer!

## 🎯 Why Use IP Instead of Localhost?

When you access via IP address (`http://192.168.1.X:8000`):
- ✅ Browser knows your network IP
- ✅ QR code auto-generates correctly
- ✅ No manual entry needed

When you access via localhost (`http://localhost:8000`):
- ❌ Browser doesn't know your network IP
- ❌ WebRTC detection may fail
- ⚠️ You'll need to enter IP manually

## 🚀 Best Practice

**Always use the start script:**
```bash
./start-viewer.sh
```

It handles everything automatically! 🎉

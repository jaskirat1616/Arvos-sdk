# ARVOS Web Viewer

**Zero-install live sensor streaming for iPhone.** View 3D point clouds, camera feeds, and sensor data in your browser - no Python required.

## ✨ Features

- **🌐 Works Everywhere** - Any device with a browser (Mac, Windows, Linux, Chromebook, tablets)
- **📱 QR Code Pairing** - Automatic connection setup with local IP detection
- **🎯 Live 3D Visualization** - Real-time point cloud rendering with Three.js (100K+ points)
- **📹 Camera Feed** - Stream iPhone camera with overlay support
- **📊 Sensor Dashboard** - IMU, pose, GPS data in real-time
- **💾 Export** - Download PLY point clouds and PNG frames
- **⚡ Performance** - FPS counter, latency monitoring, auto-reconnect
- **🎨 Clean Design** - Minimalist, professional UI with dark mode viewer

---

## 🚀 Quick Start (30 seconds)

### On Your Computer:

**Option 1: Python HTTP Server (Recommended)**
```bash
cd arvos-sdk/web-viewer
python3 -m http.server 8000
```

**Option 2: PHP Server**
```bash
cd arvos-sdk/web-viewer
php -S localhost:8000
```

**Option 3: Node.js (if installed)**
```bash
cd arvos-sdk/web-viewer
npx http-server -p 8000
```

### On Your iPhone:

1. **Open ARVOS app**
2. **Start streaming** (select any mode)
3. **Open browser** on your computer: `http://localhost:8000`
4. **Scan QR code** with iPhone
5. **Done!** Live data appears in ~30 seconds

---

## 📋 Detailed Testing Instructions

### Prerequisites

- **iPhone:** ARVOS app installed and configured
- **Computer:** Mac, Windows, or Linux with any modern browser
- **Network:** Both devices on same WiFi network

### Step-by-Step Test

#### 1. Start Web Server

Open terminal in `arvos-sdk/web-viewer/` directory:

```bash
# Check you're in the right place
ls
# Should show: css/  index.html  js/  viewer.html

# Start server (choose one):
python3 -m http.server 8000   # Python 3
python -m SimpleHTTPServer 8000  # Python 2
php -S 0.0.0.0:8000           # PHP
npx http-server -p 8000        # Node.js
```

You should see:
```
Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
```

#### 2. Open Landing Page

In your browser, navigate to:
```
http://localhost:8000
```

You should see:
- **ARVOS** heading with gradient
- 3-step guide
- QR code in the center
- Connection URL below QR code (e.g., `arvos://192.168.1.100:8765`)

#### 3. Start ARVOS iPhone App

On your iPhone:
1. Open **ARVOS** app
2. Go to **Stream** tab
3. Select a mode (e.g., "RGBD Camera" or "Full Sensor")
4. Tap **CONNECT TO SERVER** button
5. Scan the QR code from the web page

#### 4. Verify Connection

**On iPhone:**
- Status should change to "CONNECTED" (orange dot)
- FPS counter should start updating

**On Web Page:**
- Click **"Open Viewer"** button
- Or navigate to: `http://localhost:8000/viewer.html?port=8765`

#### 5. Test Live Streaming

**On iPhone:**
- Tap **START** button
- Move phone around slowly

**In Browser Viewer:**
- Status badge should show **"Connected"** (green dot)
- FPS should be 1-30 (depending on mode)
- Point cloud should appear and update
- Sensor stats should show live data

**Expected Performance:**
- **Camera:** 5-10 FPS (JPEG compressed)
- **Depth:** 1-5 FPS (point clouds)
- **IMU:** Updates per frame
- **Latency:** 50-200ms on local WiFi

---

## 🎮 Viewer Controls

### Visualization
- **Toggle Points** - Show/hide point cloud
- **Toggle Camera** - Show/hide camera feed overlay
- **Reset View** - Return camera to default position

### Export
- **Save Point Cloud** - Download as `.ply` file (standard format)
- **Capture Frame** - Save current view as `.png` image

### 3D Navigation
- **Rotate:** Click and drag
- **Zoom:** Scroll wheel or pinch
- **Pan:** Right-click drag (or two-finger drag)

---

## 🔧 Troubleshooting

### QR Code Shows Wrong IP

**Problem:** QR code displays `YOUR_COMPUTER_IP` or wrong address

**Solution:**
1. The web page tries to auto-detect your IP
2. If it fails, manually enter your IP:
   - **Mac/Linux:** Run `ifconfig | grep "inet "` in terminal
   - **Windows:** Run `ipconfig` in command prompt
   - Look for `192.168.x.x` or `10.0.x.x`
3. Update port in web page if ARVOS uses different port

### No Connection / Disconnected

**Check:**
- ✅ Both devices on same WiFi network
- ✅ Web server is running (`localhost:8000` loads)
- ✅ Firewall not blocking port 8765
- ✅ ARVOS app shows "CONNECTED" before clicking START
- ✅ iPhone and computer can ping each other

**Mac Firewall:**
```bash
# Allow Python through firewall
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /usr/bin/python3
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblock /usr/bin/python3
```

**Windows Firewall:**
- Windows Defender → Allow an app → Python → Allow

### Point Cloud Not Updating

**Check:**
- iPhone is in streaming mode (not just connected)
- Selected mode includes depth (e.g., "RGBD Camera", "LiDAR Scanner", "Full Sensor")
- Moving phone slowly (depth updates at 1-5 FPS)
- Check browser console for errors (F12 → Console tab)

### Low FPS / Lag

**Optimize:**
- Use 5GHz WiFi instead of 2.4GHz
- Reduce streaming quality in ARVOS settings
- Close other apps using network
- Move closer to WiFi router
- Use USB-C tethering (requires USB WebSocket support)

---

## 📁 File Structure

```
web-viewer/
├── index.html              # Landing page with QR code
├── viewer.html             # Live 3D viewer
├── css/
│   └── minimal.css         # Ultra-clean styling
└── js/
    ├── qr-generator.js     # QR code + IP detection
    ├── websocket-client.js # Connection handling
    ├── threejs-viewer.js   # 3D point cloud renderer
    └── camera-view.js      # Camera feed overlay
```

---

## 🌟 Advanced Usage

### Custom Port

If ARVOS uses a different port:

1. On landing page, change port number
2. Click "Update QR"
3. Scan new QR code

### Deploy to GitHub Pages

```bash
# In arvos-sdk repo
git add web-viewer/
git commit -m "Add web viewer"
git push

# Enable GitHub Pages in repo settings
# Point to /web-viewer directory
# Access at: https://yourusername.github.io/arvos-sdk/web-viewer/
```

### Custom Domain

1. Deploy to any static host (Netlify, Vercel, GitHub Pages)
2. Update ARVOS connection to use your domain
3. Share link: `https://arvos.yourdomain.com`

---

## 💡 Use Cases

### For Researchers
- **SLAM Testing** - Visualize reconstruction in real-time
- **Dataset Collection** - Monitor data quality during capture
- **Demo/Presentations** - Show live sensor data without setup

### For Developers
- **Quick Debugging** - See point clouds instantly
- **API Testing** - Verify WebSocket messages
- **Integration** - Embed in your own web app

### For Students
- **Learning** - Understand 3D sensors visually
- **Projects** - Use as base for AR experiments
- **Robotics** - Visualize robot perception

---

## 🔒 Security Notes

- **Local Network Only** - No internet connection required
- **No Data Storage** - Everything runs in browser memory
- **No Analytics** - Zero tracking or telemetry
- **Open Source** - Inspect all code

---

## 📝 Browser Compatibility

| Browser | Status | Notes |
|---------|--------|-------|
| Chrome | ✅ Full support | Recommended |
| Safari | ✅ Full support | Mac/iOS native |
| Firefox | ✅ Full support | - |
| Edge | ✅ Full support | Chromium-based |
| Opera | ✅ Full support | - |
| IE 11 | ❌ Not supported | Use modern browser |

**Minimum Requirements:**
- WebGL support (for 3D rendering)
- WebSocket support (for streaming)
- ES6 JavaScript (arrow functions, async/await)

---

## 🐛 Reporting Issues

If you encounter bugs:

1. **Check browser console** (F12 → Console)
2. **Note error messages**
3. **Test connection:** Can you ping iPhone IP from computer?
4. **Try different browser**
5. **Open issue** on GitHub with details

---

## 🤝 Contributing

Want to improve the viewer?

**Easy Wins:**
- Add more visualizations (IMU graph, pose trail)
- Implement session recording
- Add VR/AR mode
- Create mobile-friendly controls

**See:** `arvos-sdk/CONTRIBUTING.md`

---

## 📜 License

MIT License - Use freely in your projects

---

## 🎉 Success Checklist

After testing, you should have:

- [x] Loaded landing page at `localhost:8000`
- [x] Saw QR code with your computer's IP
- [x] Connected iPhone ARVOS app via QR scan
- [x] Opened viewer and saw "Connected" status
- [x] Started streaming and saw live point cloud
- [x] Exported PLY file successfully
- [x] FPS shows 1-30, latency < 500ms

**If all checked:** You're ready to use ARVOS web viewer! 🚀

---

**Need Help?** Open an issue or check the main ARVOS SDK documentation.

# ARVOS Web Viewer - Complete Testing Guide

## 🎯 Goal
Test the new zero-install web viewer to ensure it works perfectly with your iPhone ARVOS app.

---

## 📋 Prerequisites

### You Need:
- ✅ iPhone with ARVOS app installed
- ✅ Mac/PC on same WiFi network as iPhone
- ✅ Modern web browser (Chrome, Safari, Firefox, Edge)
- ✅ Python 3 installed (check with `python3 --version`)

### Network Requirements:
- Both devices must be on the **same WiFi network**
- Firewall should allow connections on port 8765 (ARVOS default)
- If using Mac, System Preferences → Security → Firewall → Allow Python

---

## 🚀 Quick Test (5 Minutes)

### Step 1: Start the Web Viewer

Open Terminal and run:

```bash
cd /Users/jaskiratsingh/Desktop/arvos-sdk/web-viewer
./start-viewer.sh
```

**Expected Output:**
```
🚀 Starting ARVOS Web Viewer...

📡 Network Configuration:
   Local IP: 192.168.1.100
   Port: 8000

📱 iPhone Setup:
   1. Open ARVOS app
   2. Go to Stream tab
   3. Tap 'Connect to Server'
   4. Scan QR code from browser

🌐 Opening browser at: http://localhost:8000

✅ Starting Python 3 HTTP server...
Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
```

Your browser should auto-open to `http://localhost:8000`

---

### Step 2: Verify Landing Page

**You Should See:**
- Large "ARVOS" heading at the top
- 3 numbered steps in the middle
- QR code in the center
- Connection URL below QR (like `arvos://192.168.1.100:8765`)
- "CONNECT TO SERVER" and other buttons at bottom

**Check:**
- ✅ Page loads completely
- ✅ QR code is visible (black and white squares)
- ✅ Connection URL shows a real IP address (not "YOUR_COMPUTER_IP")
- ✅ No JavaScript errors in console (press F12 → Console tab)

**Screenshot Checklist:**
![Expected Landing Page](expected-landing.png) ← Take a screenshot!

---

### Step 3: Connect iPhone ARVOS App

**On iPhone:**
1. Open **ARVOS** app
2. Tap **Stream** tab (bottom navigation)
3. Ensure you're NOT streaming yet (stop if needed)
4. Tap **"CONNECT TO SERVER"** button (bottom of screen)
5. **Scan the QR code** from your computer screen

**Expected Result:**
- iPhone should show "CONNECTED" with orange dot
- Status at top should change from "DISCONNECTED" to "CONNECTED"

**If It Fails:**
- Check both devices are on same WiFi
- Try entering IP manually: Settings → Server → Enter IP from web page
- Make sure firewall isn't blocking port 8765

---

### Step 4: Open the Live Viewer

**On Computer:**
1. Click the orange **"Open Viewer"** button
2. New tab should open at `http://localhost:8000/viewer.html?port=8765`

**You Should See:**
- Black background (3D canvas)
- Top bar: "ARVOS Live Viewer" with status badge
- Right panel: Controls and stats
- Status should show "Disconnected" (waiting for streaming)

---

### Step 5: Start Streaming

**On iPhone:**
1. Make sure connection status shows "CONNECTED" (orange dot)
2. Select a mode with depth: **"RGBD Camera"** or **"Full Sensor"**
3. Tap the big **"START"** button

**Expected in Browser Viewer:**
- Status badge changes to **"Connected"** (green dot with glow)
- FPS counter starts updating (1-30)
- Point cloud appears (colored dots in 3D space)
- Stats panel shows live numbers

**Move Your iPhone Around Slowly:**
- Point cloud should update in real-time
- New points appear as you scan the environment
- Colors represent depth (blue=close, red=far)

---

### Step 6: Test 3D Controls

**In Browser Viewer:**
- **Rotate:** Click and drag
- **Zoom:** Scroll wheel up/down
- **Pan:** Right-click and drag (or Ctrl+drag)

**You Should Be Able To:**
- ✅ Spin the point cloud 360°
- ✅ Zoom in/out smoothly
- ✅ Pan to different areas
- ✅ Click "Reset View" button to return to default

---

### Step 7: Test Export Features

**Click "Save Point Cloud" Button:**
- Browser should download a file: `arvos_pointcloud.ply`
- File size should be > 0 bytes (check Downloads folder)
- Should be 100KB - 10MB depending on points captured

**Click "Capture Frame" Button:**
- Browser should download: `arvos_frame.png`
- Open the PNG - should show the 3D view you see

---

### Step 8: Verify Stats

**Check Controls Panel (Right Side):**

**Connection:**
- Status: Connected
- Host: Your computer IP
- Port: 8765

**Stream Stats:**
- FPS: 1-30 (varies by mode)
- Points: 1000-50000 (varies by scene)
- Latency: 50-500ms (WiFi dependent)

**Sensor Data:**
- IMU: Should show acceleration/rotation values
- Pose: Should show (x, y, z) position
- GPS: May show "GPS not available" (normal indoors)

---

## ✅ Success Checklist

After testing, you should have:

- [x] Loaded landing page at `localhost:8000`
- [x] Saw QR code with your computer's IP
- [x] Connected iPhone ARVOS app via QR scan
- [x] Opened viewer and saw "Connected" status
- [x] Started streaming and saw live point cloud
- [x] Rotated/zoomed the 3D view
- [x] Exported PLY file successfully
- [x] Exported PNG frame successfully
- [x] FPS shows 1-30, latency < 500ms
- [x] All stats update in real-time

**If ALL checked:** Perfect! Everything works! 🎉

---

## 🐛 Troubleshooting

### Problem: QR Code Shows "YOUR_COMPUTER_IP"

**Fix:**
1. The script tries to auto-detect IP, but it failed
2. Manually find your IP:
   ```bash
   ifconfig | grep "inet " | grep -v 127.0.0.1
   # Look for 192.168.x.x or 10.0.x.x
   ```
3. Manually enter in browser or update `qr-generator.js`

---

### Problem: "Failed to Connect" on iPhone

**Check:**
1. Both devices on **same WiFi network**
   - iPhone: Settings → WiFi → Note network name
   - Mac: Click WiFi icon → Note network name
   - They must match!

2. **Firewall** isn't blocking
   ```bash
   # Mac: Allow Python through firewall
   sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /usr/bin/python3
   sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblock /usr/bin/python3
   ```

3. **ARVOS app** is actually running streaming server
   - Go to Settings tab in ARVOS
   - Check "Server Port" (should be 8765)

---

### Problem: "No point cloud appears"

**Check:**
1. Selected mode includes depth?
   - ✅ RGBD Camera
   - ✅ LiDAR Scanner
   - ✅ Full Sensor
   - ❌ IMU Only (no depth!)

2. Moving iPhone slowly?
   - Depth updates at 1-5 FPS (slow!)
   - Need to move slowly for points to accumulate

3. Environment has texture?
   - Plain white walls = hard for LiDAR
   - Textured surfaces = better point clouds

---

### Problem: "Low FPS (< 5)"

**Optimize:**
1. **Use 5GHz WiFi** instead of 2.4GHz
2. **Reduce quality** in ARVOS settings
3. **Close other apps** using network bandwidth
4. **Move closer** to WiFi router
5. **Check latency** - should be < 300ms

---

### Problem: Browser console shows errors

**Common Errors & Fixes:**

**"WebSocket connection failed"**
- iPhone not streaming (tap START)
- Wrong IP address
- Firewall blocking port 8765

**"Three.js not loaded"**
- No internet connection (CDN can't load)
- Use local Three.js instead (download and update viewer.html)

**"QRCode is not defined"**
- No internet connection (CDN can't load)
- Download qrcode.min.js locally

---

## 📸 Screenshots to Take

For documentation/debugging, capture:

1. **Landing Page** - Full screen with QR code
2. **iPhone Connected** - ARVOS app showing "CONNECTED"
3. **Viewer Running** - Browser with live point cloud
4. **Stats Panel** - Close-up of FPS/latency numbers
5. **Exported PLY** - Open in CloudCompare/MeshLab

Save to: `/Users/jaskiratsingh/Desktop/arvos-testing/screenshots/`

---

## 🎬 Video Test (Optional)

Record a short video showing:
1. Starting web server (terminal output)
2. Landing page loading
3. Scanning QR code with iPhone
4. Opening viewer
5. Starting stream and seeing point cloud
6. Rotating the 3D view
7. Exporting PLY file

Duration: ~90 seconds
Perfect for demo reels or bug reports!

---

## 📊 Performance Benchmarks

**Expected Performance on Good WiFi:**

| Metric | Good | Acceptable | Poor |
|--------|------|------------|------|
| Latency | < 100ms | 100-300ms | > 300ms |
| Camera FPS | 20-30 | 10-20 | < 10 |
| Depth FPS | 3-5 | 1-3 | < 1 |
| Point Count | 10K-50K | 1K-10K | < 1K |

**If "Poor":** Check network, reduce quality, move closer to router

---

## 🔄 Reset/Clean Test

If things go wrong, reset everything:

```bash
# Stop server (Ctrl+C in terminal)

# Restart iPhone ARVOS app
# (Swipe up, close app, reopen)

# Clear browser cache
# Chrome: Cmd+Shift+Delete → Clear cache
# Safari: Develop → Empty Caches

# Restart web server
cd /Users/jaskiratsingh/Desktop/arvos-sdk/web-viewer
./start-viewer.sh
```

---

## 📝 Test Report Template

After testing, fill this out:

```
Date: _______________
Tester: _____________
iPhone Model: ________
Computer OS: _________

✅ Landing page loads correctly
✅ QR code shows valid IP
✅ iPhone connects successfully
✅ Viewer shows live point cloud
✅ Export features work
✅ Performance is acceptable

Notes:
_____________________
_____________________

Issues found:
_____________________
_____________________

Screenshots attached: Yes/No
```

---

## 🚀 Next Steps After Successful Test

1. **Share with team** - Send them the ARVOS SDK link
2. **Deploy online** - Consider GitHub Pages for public access
3. **Create tutorial video** - Screen record your test
4. **Write blog post** - Show off the zero-install feature
5. **Submit to communities** - r/computervision, r/robotics

---

## 🤝 Getting Help

**If test fails:**
1. Check browser console (F12 → Console)
2. Check ARVOS app logs (if available)
3. Note error messages
4. Take screenshots
5. Open GitHub issue with:
   - OS version
   - Browser version
   - iPhone model
   - Error messages
   - Screenshots

**Contact:**
- GitHub Issues: https://github.com/jaskirat1616/arvos-sdk/issues
- Documentation: See README.md files

---

**Happy Testing! 🎉**

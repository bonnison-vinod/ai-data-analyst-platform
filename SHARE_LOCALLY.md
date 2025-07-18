# 🌐 Share AI Data Analyst Platform Locally

## Quick Setup for Local Network Sharing

### Step 1: Update Backend Configuration
1. Open `E:\Bonison\Project\ai-data-analyst-platform\Backend\main.py`
2. Change the CORS settings to allow your local network:

```python
# Update CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify your local network range
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
```

### Step 2: Start Backend Server
```bash
cd E:\Bonison\Project\ai-data-analyst-platform\Backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 3: Start Frontend Server
```bash
cd E:\Bonison\Project\ai-data-analyst-platform\frontend
npm start
```

### Step 4: Get Your IP Address
1. Open Command Prompt
2. Run: `ipconfig`
3. Find your IPv4 Address (e.g., 192.168.1.100)

### Step 5: Share Access
Give users these URLs:
- **Frontend**: `http://YOUR_IP:3000` (e.g., http://192.168.1.100:3000)
- **Backend API**: `http://YOUR_IP:8000` (e.g., http://192.168.1.100:8000)

### Requirements for Other Users:
- Must be on the same network (WiFi/LAN)
- Modern web browser
- No additional software needed

### Security Note:
- This is for testing only
- Don't use in production without proper security measures

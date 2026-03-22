# Google Maps Location API for Open WebUI & Ollama

A backend solution and frontend integration that enables **Local LLM** (via Ollama & Open WebUI) to display **embedded Google Maps** when users ask about locations (restaurants, attractions, etc.).

---

## 🇮🇩 Versi Bahasa Indonesia

Untuk dokumentasi dalam Bahasa Indonesia, lihat [README.md](README.md).

---

## 📋 Table of Contents

- [Architecture](#architecture)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Google Cloud Console Setup](#google-cloud-console-setup)
- [API Key Security](#api-key-security)
- [Usage](#usage)
- [Folder Structure](#folder-structure)
- [API Documentation](#api-documentation)
- [Troubleshooting](#troubleshooting)
- [Technical Assumptions](#technical-assumptions)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            USER (Chat Interface)                        │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         OPEN WEBUI (Frontend)                           │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Google Maps Location Function (Function Calling)               │   │
│  │  - Detect location intent                                       │   │
│  │  - Call backend API                                             │   │
│  │  - Render embedded map iframe                                   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    FASTAPI BACKEND (Python)                             │
│  ┌──────────────────┐    ┌──────────────────────────────────────────┐  │
│  │  Location API    │───▶│  Google Maps Service                     │  │
│  │  /search-location│    │  - Places API (Text Search)              │  │
│  │  /place/{id}     │    │  - Embed API (iframe URL)                │  │
│  └──────────────────┘    └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      GOOGLE CLOUD PLATFORM                              │
│  ┌──────────────────┐    ┌──────────────────────────────────────────┐  │
│  │  Places API      │    │  Maps Embed API                          │  │
│  │  - Search places │    │  - Generate embed URLs                   │  │
│  │  - Place details │    │  - Directions links                      │  │
│  └──────────────────┘    └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## ✨ Features

- **🎯 Intent Detection**: Automatically detects location-related questions (restaurants, attractions, hotels, etc.)
- **🗺️ Embedded Maps**: Displays Google Maps iframe directly in chat
- **🧭 Directions Link**: Button for navigation to location
- **🔒 Security**: API key management via environment variables
- **⚡ Async Processing**: Uses async/await for optimal performance
- **📦 Docker Ready**: Easy deployment with Docker Compose
- **🇮🇩 Bilingual**: Detects intent in both Indonesian and English
- **⚠️ Error Handling**: Handles quota, billing, and network errors

---

## 📦 Prerequisites

### Required Software

| Software | Minimum Version | Link |
|----------|-----------------|------|
| Python | 3.9+ | [python.org](https://www.python.org/downloads/) |
| Docker & Docker Compose | Latest | [docker.com](https://www.docker.com/) |
| Node.js (optional) | 18+ | [nodejs.org](https://nodejs.org/) |

### Accounts & APIs

| Service | Requirement |
|---------|-------------|
| Google Cloud Platform | Active account with billing enabled |
| Google Places API | API enabled |
| Google Maps Embed API | API enabled |

---

## 🚀 Installation

### Option 1: Using Docker Compose (Recommended)

```bash
# 1. Clone or download this project
cd TaskCodeTestHeyPico

# 2. Copy environment file
cp .env.example .env

# 3. Edit .env and add API Keys from Google Cloud
#    See "Google Cloud Console Setup" section below

# 4. Start all services
docker-compose up -d

# 5. Check status
docker-compose ps

# 6. Access applications
#    - Open WebUI: http://localhost:3000
#    - Backend API: http://localhost:8000
#    - API Docs: http://localhost:8000/docs
```

### Option 2: Manual (Without Docker)

```bash
# 1. Install backend dependencies
cd backend
pip install -r requirements.txt

# 2. Copy environment file
cp ../.env.example .env

# 3. Edit .env and add API Keys

# 4. Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 5. Setup Open WebUI separately
#    - Install Open WebUI: https://docs.openwebui.com/
#    - Upload function from openwebui_functions/ folder
```

---

## ☁️ Google Cloud Console Setup

### Step 1: Create New Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **"Select a project"** → **"New Project"**
3. Name your project (e.g., `maps-location-api`)
4. Click **"Create"**

### Step 2: Enable Required APIs

1. Go to **APIs & Services** → **Library**
2. Search and enable these APIs:
   - **Places API**
   - **Maps Embed API**

### Step 3: Create API Keys

1. Go to **APIs & Services** → **Credentials**
2. Click **"+ CREATE CREDENTIALS"** → **"API key"**
3. **Copy** the generated API Key

### Step 4: Create Two Separate API Keys (Recommended)

For better security, create 2 API keys with different restrictions:

#### API Key 1: Places API
```
Name: places-api-key
API Restrictions: Places API only
```

#### API Key 2: Maps Embed API
```
Name: maps-embed-api-key
API Restrictions: Maps Embed API only
```

### Step 5: Setup Billing

1. Go to **Billing** in Google Cloud Console
2. Link a billing account to your project
3. **Important**: Set budget alerts to avoid unexpected costs

---

## 🔒 API Key Security

### Restrictions in Google Cloud Console

#### 1. HTTP Referrer Restrictions (For Embed API)

```
Application restrictions: HTTP referrers (websites)

Accepted referrers:
- http://localhost:3000/*
- http://localhost:8000/*
- https://your-domain.com/*
```

#### 2. IP Address Restrictions (For Places API)

```
Application restrictions: IP addresses

Accepted IP addresses:
- 127.0.0.1 (development)
- YOUR_SERVER_IP (production)
```

#### 3. API Restrictions

```
API restrictions: Restrict key

Select APIs:
- Places API (for Places API key)
- Maps Embed API (for Embed API key)
```

### Best Practices

| Practice | Description |
|----------|-------------|
| ✅ Don't hardcode API keys | Always use environment variables |
| ✅ Use separate API keys | One key per service/API |
| ✅ Set restrictions | HTTP referrer + IP + API restrictions |
| ✅ Monitor usage | Check Cloud Console for anomalies |
| ✅ Set budget alerts | Get notified when costs exceed threshold |
| ✅ Rotate keys | Change API keys periodically |

---

## 📖 Usage

### 1. Setup Open WebUI Functions

1. Open Open WebUI at `http://localhost:3000`
2. Login and go to **Settings** → **Functions**
3. Click **"+"** to add new function
4. Copy paste code from `openwebui_functions/google_maps_location.py`
5. Configure valves:
   ```
   BACKEND_API_URL: http://localhost:8000
   API_SECRET: your_secret_key
   ```
6. **Enable** function and **Save**

### 2. Test Chat with Location Queries

Try asking in Open WebUI chat:

```
User: Recommend good restaurants in South Jakarta?
User: Where are the best tourist attractions in Bandung?
User: Find a cafe nearby suitable for working
User: Best hotels in Yogyakarta for families
User: Nearest Padang restaurant
User: Where can I eat near here?
User: Places to visit in Bali
```

### 3. Expected Output

When users ask about locations, chat will display:

```
┌─────────────────────────────────────────────────────┐
│ 📍 Locations Found                                  │
├─────────────────────────────────────────────────────┤
│ 1. Restaurant Name                                  │
│    📍 123 Example St., Jakarta                      │
│    ⭐ 4.5                                           │
│                                                     │
│    [Google Maps Embed - Interactive]                │
│                                                     │
│    [🗺️ Directions] [📌 View on Google Maps]       │
└─────────────────────────────────────────────────────┘
```

---

## 📁 Folder Structure

```
TaskCodeTestHeyPico/
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI application
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   └── google_maps_service.py # Google Maps integration
│   │   └── __init__.py
│   ├── requirements.txt               # Python dependencies
│   ├── Dockerfile                     # Backend container
│   └── .env                           # Environment variables (gitignored)
│
├── openwebui_functions/
│   └── google_maps_location.py        # Open WebUI Function
│
├── docker-compose.yml                 # Full stack deployment
├── .env.example                       # Environment template
├── .gitignore                         # Git ignore rules
└── README.md                          # This file (English)
└── README.id.md                       # Indonesian version
```

---

## 📡 API Documentation

### Health Check

```bash
GET http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "Google Maps Location API",
  "version": "1.0.0"
}
```

### Search Location

```bash
POST http://localhost:8000/api/v1/search-location
Content-Type: application/json
X-API-Key: your_secret_key (optional)

{
  "query": "good restaurants",
  "location": "Jakarta",
  "max_results": 3
}
```

**Response:**
```json
{
  "success": true,
  "query": "good restaurants",
  "message": "Found 3 places",
  "places": [
    {
      "name": "Restaurant Name",
      "address": "Full Address Here",
      "place_id": "ChIJ...",
      "rating": 4.5,
      "types": ["restaurant", "food", "point_of_interest"],
      "embed_url": "https://www.google.com/maps/embed/v1/place?key=...&q=place_id:...",
      "directions_url": "https://www.google.com/maps/dir/?api=1&destination=..."
    }
  ]
}
```

### Get Place Embed

```bash
GET http://localhost:8000/api/v1/place/{place_id}/embed
```

**Response:**
```json
{
  "success": true,
  "place_id": "ChIJ...",
  "embed_url": "https://www.google.com/maps/embed/v1/place?key=...&q=place_id:...",
  "directions_url": "https://www.google.com/maps/dir/?api=1&destination=..."
}
```

---

## 🔧 Troubleshooting

### Error: "API quota exceeded"

**Cause:** Daily quota for Google Maps API has reached its limit

**Solution:**
1. Check quota in Google Cloud Console → APIs & Services → Dashboard
2. Upgrade billing tier if needed
3. Wait for quota reset (usually daily)

### Error: "Invalid API Key"

**Cause:** API Key is incorrect or lacks proper permissions

**Solution:**
1. Verify API key in Google Cloud Console
2. Ensure required APIs are enabled
3. Check restrictions (IP, referrer) aren't too strict

### Error: "Billing account required"

**Cause:** API requires billing account even with free tier

**Solution:**
1. Go to Billing in Google Cloud Console
2. Link or create a billing account
3. Set budget alerts for cost control

### Open WebUI Function Not Responding

**Cause:** Function not configured correctly

**Solution:**
1. Check function is enabled in Settings → Functions
2. Verify BACKEND_API_URL is correct
3. Check logs in Open WebUI admin panel

### CORS Error in Browser

**Cause:** Backend doesn't allow origin from Open WebUI

**Solution:**
1. Edit `.env` and add Open WebUI origin to `ALLOWED_ORIGINS`
2. Restart backend server

---

## 📝 Technical Assumptions

| Assumption | Detail |
|------------|--------|
| **Docker** | User has Docker Desktop or Docker Engine + Compose installed |
| **Google Cloud** | User has Google Cloud Platform account with active billing |
| **Open WebUI** | User is familiar with basic Open WebUI installation |
| **Python** | User has basic Python knowledge for troubleshooting |
| **Network** | Ports 3000, 8000, 11434 are available and not used by other apps |
| **OS** | Development on Windows, macOS, or Linux (all supported) |
| **Internet** | Stable internet connection for Google APIs access |

### Out of Scope

| Item | Reason |
|------|--------|
| Ollama model download | Handled automatically by Ollama container |
| Open WebUI user management | Outside maps integration scope |
| Custom UI styling | Uses default Open WebUI styling |
| Database persistence | No database required for this use case |

---

## 📄 License

This project was created for Fullstack Developer position technical test.

---

## 👨‍💻 Author

Fullstack Developer Candidate

---

## 🙏 Acknowledgments

- [Open WebUI](https://github.com/open-webui/open-webui)
- [Ollama](https://ollama.ai/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Google Maps Platform](https://developers.google.com/maps)

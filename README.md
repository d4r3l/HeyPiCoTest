# Google Maps Location API for Open WebUI & Ollama

Solusi backend dan integrasi frontend yang memungkinkan **Local LLM** (via Ollama & Open WebUI) untuk menampilkan **Google Maps embedded** ketika user bertanya tentang lokasi tempat (makan, jalan-jalan, dll).

---

## 🇬🇧 English Version

For English documentation, see [README.en.md](README.en.md).

---

## 📋 Daftar Isi

- [Arsitektur](#arsitektur)
- [Fitur](#fitur)
- [Prasyarat](#prasyarat)
- [Instalasi](#instalasi)
- [Setup Google Cloud Console](#setup-google-cloud-console)
- [Keamanan API Key](#keamanan-api-key)
- [Penggunaan](#penggunaan)
- [Struktur Folder](#struktur-folder)
- [API Documentation](#api-documentation)
- [Troubleshooting](#troubleshooting)
- [Asumsi Teknis](#asumsi-teknis)

---

## 🚀 Quick Start

```bash
# 1. Clone repository
git clone https://github.com/d4r3l/HeyPiCoTest.git
cd HeyPiCoTest

# 2. Setup environment
cp .env.example .env
# Edit .env dan isi API Keys dari Google Cloud Console

# 3. Run dengan Docker
docker-compose up -d

# 4. Akses aplikasi
# - Open WebUI: http://localhost:3000
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

---

## 🏗️ Arsitektur

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

## ✨ Fitur

- **🎯 Intent Detection**: Otomatis mendeteksi pertanyaan tentang lokasi (restoran, wisata, hotel, dll)
- **🗺️ Embedded Maps**: Menampilkan Google Maps iframe langsung di chat
- **🧭 Directions Link**: Tombol untuk navigasi ke lokasi
- **🔒 Security**: API key management via environment variables
- **⚡ Async Processing**: Menggunakan async/await untuk performa optimal
- **📦 Docker Ready**: Deployment mudah dengan Docker Compose
- **🇮🇩 Bilingual**: Mendeteksi intent dalam Bahasa Indonesia dan English
- **⚠️ Error Handling**: Penanganan error quota, billing, dan network issues

---

## 📦 Prasyarat

### Software yang Harus Diinstall

| Software | Versi Minimum | Link |
|----------|---------------|------|
| Python | 3.9+ | [python.org](https://www.python.org/downloads/) |
| Docker & Docker Compose | Latest | [docker.com](https://www.docker.com/) |
| Node.js (opsional) | 18+ | [nodejs.org](https://nodejs.org/) |

### Akun & API

| Service | Requirement |
|---------|-------------|
| Google Cloud Platform | Akun aktif dengan billing enabled |
| Google Places API | API enabled |
| Google Maps Embed API | API enabled |

---

## 🚀 Instalasi

### Opsi 1: Menggunakan Docker Compose (Recommended)

```bash
# 1. Clone atau download project ini
cd TaskCodeTestHeyPico

# 2. Copy environment file
cp .env.example .env

# 3. Edit .env dan isi API Keys dari Google Cloud
#    Lihat section "Setup Google Cloud Console" di bawah

# 4. Jalankan semua services
docker-compose up -d

# 5. Cek status
docker-compose ps

# 6. Akses aplikasi
#    - Open WebUI: http://localhost:3000
#    - Backend API: http://localhost:8000
#    - API Docs: http://localhost:8000/docs
```

### Opsi 2: Manual (Tanpa Docker)

```bash
# 1. Install dependencies backend
cd backend
pip install -r requirements.txt

# 2. Copy environment file
cp ../.env.example .env

# 3. Edit .env dan isi API Keys

# 4. Jalankan backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 5. Setup Open WebUI secara terpisah
#    - Install Open WebUI: https://docs.openwebui.com/
#    - Upload function dari folder openwebui_functions/
```

---

## ☁️ Setup Google Cloud Console

### Langkah 1: Buat Project Baru

1. Buka [Google Cloud Console](https://console.cloud.google.com/)
2. Klik **"Select a project"** → **"New Project"**
3. Beri nama project (contoh: `maps-location-api`)
4. Klik **"Create"**

### Langkah 2: Enable Required APIs

1. Buka **APIs & Services** → **Library**
2. Search dan enable API berikut:
   - **Places API**
   - **Maps Embed API**

### Langkah 3: Buat API Keys

1. Buka **APIs & Services** → **Credentials**
2. Klik **"+ CREATE CREDENTIALS"** → **"API key"**
3. **Copy API Key** yang muncul

### Langkah 4: Buat Dua API Keys Terpisah (Recommended)

Untuk keamanan lebih baik, buat 2 API keys dengan restriction berbeda:

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

### Langkah 5: Setup Billing

1. Buka **Billing** di Google Cloud Console
2. Link billing account ke project
3. **Penting**: Set budget alert untuk menghindari biaya tak terduga

---

## 🔒 Keamanan API Key

### Restriksi di Google Cloud Console

#### 1. HTTP Referrer Restrictions (Untuk Embed API)

```
Application restrictions: HTTP referrers (websites)

Accepted referrers:
- http://localhost:3000/*
- http://localhost:8000/*
- https://your-domain.com/*
```

#### 2. IP Address Restrictions (Untuk Places API)

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
- Places API (untuk Places API key)
- Maps Embed API (untuk Embed API key)
```

### Best Practices

| Practice | Description |
|----------|-------------|
| ✅ Jangan hardcode API key | Selalu gunakan environment variables |
| ✅ Gunakan API key terpisah | Satu key per service/API |
| ✅ Set restriksi | HTTP referrer + IP + API restrictions |
| ✅ Monitor usage | Check Cloud Console untuk anomali |
| ✅ Set budget alert | Notifikasi jika biaya melebihi threshold |
| ✅ Rotate keys | Ganti API key secara berkala |

---

## 📖 Penggunaan

### 1. Setup Open WebUI Functions

1. Buka Open WebUI di `http://localhost:3000`
2. Login dan buka **Settings** → **Functions**
3. Klik **"+"** untuk add new function
4. Copy paste kode dari `openwebui_functions/google_maps_location.py`
5. Configure valves:
   ```
   BACKEND_API_URL: http://localhost:8000
   API_SECRET: your_secret_key
   ```
6. **Enable** function dan **Save**

### 2. Test Chat dengan Location Query

Coba tanya di chat Open WebUI:

```
User: Rekomendasi restoran enak di Jakarta Selatan?
User: Dimana tempat wisata yang bagus di Bandung?
User: Cari cafe dekat sini yang cocok untuk kerja
User: Hotel terbaik di Yogyakarta untuk keluarga
User: Rumah makan padang terdekat
```

### 3. Output yang Diharapkan

Ketika user bertanya tentang lokasi, chat akan menampilkan:

```
┌─────────────────────────────────────────────────────┐
│ 📍 Lokasi Ditemukan                                 │
├─────────────────────────────────────────────────────┤
│ 1. Nama Restoran                                    │
│    📍 Jl. Contoh No. 123, Jakarta                   │
│    ⭐ 4.5                                           │
│                                                     │
│    [Google Maps Embed - Interactive]                │
│                                                     │
│    [🗺️ Petunjuk Arah] [📌 Lihat di Google Maps]   │
└─────────────────────────────────────────────────────┘
```

---

## 📁 Struktur Folder

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
└── README.md                          # This file
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
  "query": "restoran enak",
  "location": "Jakarta",
  "max_results": 3
}
```

**Response:**
```json
{
  "success": true,
  "query": "restoran enak",
  "message": "Ditemukan 3 tempat",
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

### Error: "API quota telah habis"

**Penyebab:** Quota harian Google Maps API telah mencapai limit

**Solusi:**
1. Check quota di Google Cloud Console → APIs & Services → Dashboard
2. Upgrade billing tier jika perlu
3. Tunggu reset quota (biasanya harian)

### Error: "API Key tidak valid"

**Penyebab:** API Key salah atau tidak memiliki permission

**Solusi:**
1. Verify API key di Google Cloud Console
2. Pastikan API yang diperlukan sudah di-enable
3. Check restriksi (IP, referrer) tidak terlalu ketat

### Error: "Billing account required"

**Penyebab:** API memerlukan billing account meskipun ada free tier

**Solusi:**
1. Buka Billing di Google Cloud Console
2. Link atau create billing account
3. Set budget alert untuk kontrol biaya

### Open WebUI Function tidak merespon

**Penyebab:** Function tidak ter-configure dengan benar

**Solusi:**
1. Check function enabled di Settings → Functions
2. Verify BACKEND_API_URL correct
3. Check logs di Open WebUI admin panel

### CORS Error di Browser

**Penyebab:** Backend tidak mengizinkan origin dari Open WebUI

**Solusi:**
1. Edit `.env` dan tambahkan origin Open WebUI ke `ALLOWED_ORIGINS`
2. Restart backend server

---

## 📝 Asumsi Teknis

| Asumsi | Detail |
|--------|--------|
| **Docker** | User sudah install Docker Desktop atau Docker Engine + Compose |
| **Google Cloud** | User memiliki akun Google Cloud Platform dengan billing aktif |
| **Open WebUI** | User familiar dengan dasar-dasar Open WebUI installation |
| **Python** | User memiliki basic Python knowledge untuk troubleshooting |
| **Network** | Port 3000, 8000, 11434 tersedia dan tidak digunakan aplikasi lain |
| **OS** | Development dilakukan di Windows, macOS, atau Linux (semua supported) |
| **Internet** | Koneksi internet stabil untuk akses Google APIs |

### Tidak Termasuk dalam Scope

| Item | Alasan |
|------|--------|
| Ollama model download | Di-handle otomatis oleh Ollama container |
| Open WebUI user management | Diluar scope integrasi maps |
| Custom UI styling | Menggunakan default Open WebUI styling |
| Database persistence | Tidak memerlukan database untuk use case ini |

---

## 📄 License

Project ini dibuat untuk tujuan tes teknis Fullstack Developer position.

---

## 👨‍💻 Author

**Muhammad Reza**

---

## 🙏 Acknowledgments

- [Open WebUI](https://github.com/open-webui/open-webui)
- [Ollama](https://ollama.ai/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Google Maps Platform](https://developers.google.com/maps)

---

## 🔗 Links

- **GitHub Repository:** https://github.com/d4r3l/HeyPiCoTest
- **Open WebUI:** https://openwebui.com
- **Ollama:** https://ollama.ai
- **Google Maps Platform:** https://developers.google.com/maps

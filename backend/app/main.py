"""
FastAPI Backend for Google Maps Integration with Open WebUI
Handles location queries and returns embeddable Google Maps URLs
"""

import sys
import os
from pathlib import Path

# Add app directory to Python path for proper imports
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List
from dotenv import load_dotenv

# Import services
from services.google_maps_service import GoogleMapsService, MapsError

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Google Maps Location API",
    description="API untuk integrasi Google Maps dengan Open WebUI & Ollama",
    version="1.0.0"
)

# CORS configuration - allow Open WebUI to access this API
# In production, restrict this to your Open WebUI domain
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8080").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Key for securing the endpoint (optional, for production)
API_SECRET = os.getenv("API_SECRET", None)


def verify_api_key(x_api_key: Optional[str] = Header(None)) -> None:
    """
    Verifies the API key if API_SECRET is configured.
    Skip verification if API_SECRET is not set (development mode).
    """
    if API_SECRET:
        if not x_api_key or x_api_key != API_SECRET:
            raise HTTPException(
                status_code=401,
                detail="Invalid or missing API key"
            )


# Initialize Google Maps Service
maps_service = GoogleMapsService()


# Request/Response Models
class LocationQuery(BaseModel):
    """Model untuk query lokasi dari user"""
    query: str = Field(..., description="Pertanyaan user tentang lokasi")
    location: Optional[str] = Field(None, description="Lokasi spesifik (kota, daerah)")
    max_results: int = Field(default=3, ge=1, le=10, description="Jumlah maksimal hasil")


class PlaceResult(BaseModel):
    """Model untuk hasil tempat"""
    name: str
    address: str
    place_id: str
    rating: Optional[float] = None
    types: List[str]
    embed_url: str
    directions_url: str


class LocationResponse(BaseModel):
    """Model untuk response API"""
    success: bool
    query: str
    places: List[PlaceResult]
    message: Optional[str] = None


class HealthResponse(BaseModel):
    """Model untuk health check"""
    status: str
    service: str
    version: str


# API Endpoints
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint untuk memastikan service berjalan
    """
    return HealthResponse(
        status="healthy",
        service="Google Maps Location API",
        version="1.0.0"
    )


@app.post("/api/v1/search-location", response_model=LocationResponse, tags=["Location"])
async def search_location(
    request: LocationQuery,
    api_key: Optional[str] = Depends(verify_api_key)
):
    """
    Mencari lokasi berdasarkan query user.
    
    Endpoint ini dipanggil oleh Open WebUI Functions ketika user bertanya
    tentang tempat (makan, jalan-jalan, dll).
    
    **Parameters:**
    - `query`: Pertanyaan user (contoh: "restoran enak", "tempat wisata")
    - `location`: Lokasi spesifik opsional (contoh: "Jakarta", "Bandung")
    - `max_results`: Jumlah maksimal hasil (default: 3)
    
    **Returns:**
    List tempat dengan URL embed Google Maps yang bisa ditampilkan di chat.
    """
    try:
        # Combine query and location for better search
        search_query = request.query
        if request.location:
            search_query = f"{request.query} di {request.location}"
        
        # Search places using Google Places API
        places = await maps_service.search_places(
            query=search_query,
            max_results=request.max_results
        )
        
        if not places:
            return LocationResponse(
                success=True,
                query=request.query,
                places=[],
                message="Tidak ditemukan tempat yang sesuai dengan pencarian Anda."
            )
        
        # Convert to response format
        place_results = [
            PlaceResult(
                name=place["name"],
                address=place["address"],
                place_id=place["place_id"],
                rating=place.get("rating"),
                types=place.get("types", []),
                embed_url=place["embed_url"],
                directions_url=place["directions_url"]
            )
            for place in places
        ]
        
        return LocationResponse(
            success=True,
            query=request.query,
            places=place_results,
            message=f"Ditemukan {len(place_results)} tempat"
        )
        
    except MapsError as e:
        # Handle specific Maps API errors
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=500,
            detail=f"Terjadi kesalahan internal: {str(e)}"
        )


@app.get("/api/v1/place/{place_id}/embed", tags=["Location"])
async def get_place_embed(
    place_id: str,
    api_key: Optional[str] = Depends(verify_api_key)
):
    """
    Mendapatkan URL embed untuk tempat spesifik berdasarkan place_id.
    
    Berguna untuk mendapatkan embed URL tanpa melakukan search ulang.
    """
    try:
        embed_url = maps_service.get_embed_url(place_id)
        directions_url = maps_service.get_directions_url(place_id)
        
        return {
            "success": True,
            "place_id": place_id,
            "embed_url": embed_url,
            "directions_url": directions_url
        }
    except MapsError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )


# Error Handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom error handler untuk HTTPException"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )


if __name__ == "__main__":
    import uvicorn
    # Run with uvicorn for development
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

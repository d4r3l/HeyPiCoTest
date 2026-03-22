"""
Google Maps Service
Menangani integrasi dengan Google Places API dan Google Maps Embed API
"""

import os
import aiohttp
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class MapsError(Exception):
    """Custom exception untuk Google Maps API errors"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class GoogleMapsService:
    """
    Service untuk berinteraksi dengan Google Maps APIs.
    
    Menggunakan:
    - Google Places API: Untuk mencari tempat berdasarkan query
    - Google Maps Embed API: Untuk mendapatkan URL embed iframe
    """
    
    def __init__(self):
        # API Keys dari environment variables
        self.places_api_key = os.getenv("GOOGLE_PLACES_API_KEY")
        self.maps_embed_api_key = os.getenv("GOOGLE_MAPS_EMBED_API_KEY")
        
        # API Endpoints
        self.places_endpoint = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        self.embed_endpoint = "https://www.google.com/maps/embed/v1/place"
        
        # Validasi API keys
        if not self.places_api_key:
            raise MapsError(
                "GOOGLE_PLACES_API_KEY tidak ditemukan di environment variables",
                status_code=500
            )
        if not self.maps_embed_api_key:
            raise MapsError(
                "GOOGLE_MAPS_EMBED_API_KEY tidak ditemukan di environment variables",
                status_code=500
            )
    
    async def search_places(
        self,
        query: str,
        max_results: int = 3,
        location: Optional[str] = None
    ) -> List[Dict]:
        """
        Mencari tempat menggunakan Google Places Text Search API.
        
        Args:
            query: Kata kunci pencarian (contoh: "restoran enak", "tempat wisata")
            max_results: Jumlah maksimal hasil yang dikembalikan
            location: Lokasi spesifik opsional untuk mempersempit pencarian
        
        Returns:
            List tempat dengan informasi lengkap termasuk embed URL
        
        Raises:
            MapsError: Jika API request gagal atau quota habis
        """
        async with aiohttp.ClientSession() as session:
            # Build request parameters
            params = {
                "query": query,
                "key": self.places_api_key,
                "max_results": max_results  # Note: API akan return max 20 results
            }
            
            # Add location bias jika disediakan
            if location:
                params["query"] = f"{query} di {location}"
            
            try:
                async with session.get(self.places_endpoint, params=params) as response:
                    if response.status != 200:
                        error_data = await response.json()
                        raise self._handle_api_error(error_data, response.status)
                    
                    data = await response.json()
                    
                    # Handle API-level errors
                    if data.get("status") == "ZERO_RESULTS":
                        return []
                    elif data.get("status") == "OVER_QUERY_LIMIT":
                        raise MapsError(
                            "API quota telah habis. Silakan coba lagi nanti.",
                            status_code=429
                        )
                    elif data.get("status") == "REQUEST_DENIED":
                        raise MapsError(
                            f"Akses ditolak: {data.get('error_message', 'Unknown error')}",
                            status_code=403
                        )
                    elif data.get("status") == "INVALID_REQUEST":
                        raise MapsError(
                            "Request tidak valid. Periksa parameter pencarian.",
                            status_code=400
                        )
                    
                    # Process results
                    results = data.get("results", [])[:max_results]
                    return [self._process_place_result(place) for place in results]
                    
            except aiohttp.ClientError as e:
                raise MapsError(
                    f"Gagal terhubung ke Google Maps API: {str(e)}",
                    status_code=503
                )
    
    def _process_place_result(self, place: Dict) -> Dict:
        """
        Memproses hasil dari Places API menjadi format yang diinginkan.
        
        Args:
            place: Raw place data dari Google Places API
        
        Returns:
            Dict dengan informasi tempat yang sudah diproses
        """
        place_id = place.get("place_id", "")
        
        return {
            "name": place.get("name", "Unknown"),
            "address": place.get("formatted_address", "Address not available"),
            "place_id": place_id,
            "rating": place.get("rating"),
            "types": place.get("types", []),
            "location": place.get("geometry", {}).get("location", {}),
            "embed_url": self.get_embed_url(place_id),
            "directions_url": self.get_directions_url(place_id)
        }
    
    def get_embed_url(self, place_id: str) -> str:
        """
        Membuat URL embed untuk iframe Google Maps.
        
        Args:
            place_id: Place ID dari Google Places API
        
        Returns:
            URL yang bisa digunakan sebagai src iframe
        """
        # URL encode the parameters
        from urllib.parse import urlencode
        
        params = {
            "key": self.maps_embed_api_key,
            "q": f"place_id:{place_id}"
        }
        
        return f"{self.embed_endpoint}?{urlencode(params)}"
    
    def get_directions_url(self, place_id: str, origin: str = "") -> str:
        """
        Membuat URL untuk directions ke tempat.
        
        Args:
            place_id: Place ID dari Google Places API
            origin: Lokasi asal (opsional, akan menggunakan current location jika kosong)
        
        Returns:
            URL Google Maps untuk directions
        """
        from urllib.parse import urlencode
        
        params = {
            "api": "1",
            "destination": f"place_id:{place_id}"
        }
        
        if origin:
            params["origin"] = origin
        
        return f"https://www.google.com/maps/dir/?{urlencode(params)}"
    
    def _handle_api_error(self, error_data: Dict, status_code: int) -> MapsError:
        """
        Menangani error dari API response.
        
        Args:
            error_data: Data error dari API response
            status_code: HTTP status code
        
        Returns:
            MapsError dengan message yang sesuai
        """
        error_message = error_data.get("error_message", "Unknown error occurred")
        
        # Check for specific error types
        if "quota" in error_message.lower():
            return MapsError(
                "API quota telah habis. Silakan upgrade billing account atau coba lagi nanti.",
                status_code=429
            )
        elif "billing" in error_message.lower():
            return MapsError(
                "API tidak aktif. Pastikan billing account sudah dikonfigurasi di Google Cloud Console.",
                status_code=403
            )
        elif "api key" in error_message.lower():
            return MapsError(
                "API Key tidak valid atau tidak memiliki permission yang cukup.",
                status_code=401
            )
        
        return MapsError(
            f"Google Maps API Error: {error_message}",
            status_code=status_code
        )
    
    async def search_places_nearby(
        self,
        latitude: float,
        longitude: float,
        radius: int = 1000,
        keyword: Optional[str] = None,
        max_results: int = 3
    ) -> List[Dict]:
        """
        Mencari tempat di sekitar koordinat tertentu (Nearby Search).
        
        Args:
            latitude: Latitude koordinat
            longitude: Longitude koordinat
            radius: Radius pencarian dalam meter (max 50000)
            keyword: Kata kunci opsional
            max_results: Jumlah maksimal hasil
        
        Returns:
            List tempat di sekitar koordinat
        """
        async with aiohttp.ClientSession() as session:
            params = {
                "location": f"{latitude},{longitude}",
                "radius": min(radius, 50000),  # Max 50km
                "key": self.places_api_key
            }
            
            if keyword:
                params["keyword"] = keyword
            
            endpoint = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            
            try:
                async with session.get(endpoint, params=params) as response:
                    if response.status != 200:
                        error_data = await response.json()
                        raise self._handle_api_error(error_data, response.status)
                    
                    data = await response.json()
                    
                    if data.get("status") == "ZERO_RESULTS":
                        return []
                    elif data.get("status") == "OVER_QUERY_LIMIT":
                        raise MapsError(
                            "API quota telah habis.",
                            status_code=429
                        )
                    
                    results = data.get("results", [])[:max_results]
                    return [self._process_place_result(place) for place in results]
                    
            except aiohttp.ClientError as e:
                raise MapsError(
                    f"Gagal terhubung ke Google Maps API: {str(e)}",
                    status_code=503
                )

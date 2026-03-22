"""
Open WebUI Functions - Google Maps Location Tool

Script ini diupload ke Open WebUI Functions untuk enable function calling
ketika user bertanya tentang lokasi (tempat makan, jalan-jalan, dll).

Cara Install di Open WebUI:
1. Buka Open WebUI → Settings → Functions
2. Klik "+" untuk add new function
3. Copy paste seluruh kode ini
4. Set Environment Variables di Open WebUI:
   - BACKEND_API_URL: URL backend FastAPI (contoh: http://localhost:8000)
   - API_SECRET: API key untuk autentikasi (opsional)
5. Enable function dan simpan
"""

import os
import re
import json
import aiohttp
from typing import Optional, Dict, Any

# Metadata untuk Open WebUI Functions
__version__ = "1.0.0"
__author__ = "Muhammad Reza"
__description__ = "Google Maps Location Finder - Menampilkan peta ketika user bertanya tentang tempat"


class Pipes:
    """
    Main class untuk Open WebUI Functions.
    Open WebUI akan memanggil method pipe() untuk memproses request.
    """
    
    def __init__(self):
        self.type = "filter"  # Filter type untuk intercept user messages
        self.name = "Google Maps Location Finder"
        self.id = "google_maps_location_finder"
        
        # Configuration dari environment variables
        self.backend_url = os.getenv("BACKEND_API_URL", "http://localhost:8000")
        self.api_secret = os.getenv("API_SECRET", "")
        
        # Location intent keywords (Bahasa Indonesia & English)
        self.location_keywords = [
            # Indonesian
            "restoran", "rumah makan", "kuliner", "makan", "minum", "cafe", "kedai",
            "tempat wisata", "wisata", "jalan-jalan", "liburan", "rekreasi", "tamasya",
            "hotel", "penginapan", "villa", "resort",
            "mall", "pusat perbelanjaan", "belanja", "toko", "pasar",
            "rumah sakit", "klinik", "puskesmas", "apotek", "farmasi",
            "sekolah", "universitas", "kampus", "kursus", "les",
            "gym", "fitness", "olahraga", "lapangan", "kolam renang",
            "bioskop", "teater", "museum", "galeri", "taman", "pantai", "gunung",
            "stasiun", "bandara", "terminal", "halte", "parkir",
            "bengkel", "spbu", "pom bensin",
            "bank", "atm", "kantor pos",
            "masjid", "gereja", "pura", "vihara", "klenteng",
            "tempat", "lokasi", "dimana", "di mana", "dekat", "sekitar",
            # English
            "restaurant", "food", "eat", "drink", "cafe", "coffee",
            "tourist", "attraction", "travel", "vacation", "sightseeing",
            "hotel", "accommodation", "lodging", "resort",
            "mall", "shopping", "store", "market",
            "hospital", "clinic", "pharmacy", "drugstore",
            "school", "university", "college",
            "gym", "fitness", "sport", "pool",
            "cinema", "theater", "museum", "gallery", "park", "beach", "mountain",
            "station", "airport", "terminal", "parking",
            "gas station", "workshop",
            "bank", "atm", "post office",
            "mosque", "church", "temple",
            "place", "location", "where", "near", "around"
        ]
    
    async def pipe(
        self,
        user_message: str,
        model_id: str,
        messages: list,
        body: dict,
        user: Optional[dict] = None,
        metadata: Optional[dict] = None
    ) -> str:
        """
        Main method yang dipanggil oleh Open WebUI.
        
        Args:
            user_message: Pesan dari user
            model_id: ID model LLM yang digunakan
            messages: Riwayat percakapan
            body: Request body dari Open WebUI
            user: Informasi user (opsional)
            metadata: Metadata tambahan (opsional)
        
        Returns:
            Response message yang akan ditampilkan di chat
        """
        # Check if user message contains location intent
        if self._has_location_intent(user_message):
            try:
                # Extract location info from message
                location_info = self._extract_location_info(user_message)
                
                # Call backend API to search places
                places = await self._search_locations(
                    query=location_info["query"],
                    location=location_info.get("location"),
                    max_results=3
                )
                
                if places and places.get("success") and places.get("places"):
                    # Generate rich response with map embed
                    return self._generate_map_response(places)
                else:
                    # No places found, let LLM handle normally
                    return user_message
                    
            except Exception as e:
                # On error, let LLM handle normally
                print(f"[Google Maps Function] Error: {str(e)}")
                return user_message
        
        # No location intent, pass through to LLM
        return user_message
    
    def _has_location_intent(self, message: str) -> bool:
        """
        Mendeteksi apakah pesan user mengandung intent terkait lokasi.
        
        Args:
            message: Pesan dari user
        
        Returns:
            True jika pesan mengandung intent lokasi
        """
        message_lower = message.lower()
        
        # Check for question patterns about locations
        location_patterns = [
            r"(dimana|di mana|where).*(bisa|bisa|boleh|boleh).*(makan|makan|wisata|wisata)",
            r"(recommend|rekomendasi|suggest|sarani).*\s*(restoran|restaurant|tempat|place|hotel|wisata)",
            r"(makan|eat|food|kuliner).*\s*(dekat|near|sekitar|around)",
            r"(wisata|tourist|jalan).*\s*(dekat|near|sekitar|around)",
            r"(cari|looking|search).*\s*(restoran|hotel|tempat|place|wisata)",
            r"(tempat|place).*\s*(makan|eat|wisata|tourist|jalan|hotel)",
        ]
        
        # Check patterns first
        for pattern in location_patterns:
            if re.search(pattern, message_lower):
                return True
        
        # Check keywords
        keyword_count = sum(1 for keyword in self.location_keywords if keyword in message_lower)
        
        # Require at least 2 location-related keywords to trigger
        return keyword_count >= 2
    
    def _extract_location_info(self, message: str) -> Dict[str, str]:
        """
        Mengekstrak informasi lokasi dari pesan user.
        
        Args:
            message: Pesan dari user
        
        Returns:
            Dict dengan query dan location
        """
        # Default values
        result = {
            "query": message,
            "location": None
        }
        
        # Try to extract city/area names (common Indonesian cities)
        cities = [
            "jakarta", "bandung", "surabaya", "yogyakarta", "semarang",
            "medan", "palembang", "makassar", "balikpapan", "manado",
            "denpasar", "bali", "lombok", "batam", "pekanbaru",
            "bogor", "depok", "tangerang", "bekasi", "serpong"
        ]
        
        message_lower = message.lower()
        
        # Check for city mentions
        for city in cities:
            if city in message_lower:
                result["location"] = city.capitalize()
                break
        
        # Check for "di [location]" pattern
        di_pattern = r"\bdi\s+(\w+)"
        match = re.search(di_pattern, message_lower)
        if match:
            potential_location = match.group(1)
            if potential_location not in ["sini", "situ", "mana", "where", "the", "a"]:
                result["location"] = potential_location.capitalize()
        
        # Extract the main query (remove question words)
        query = message
        question_words = [
            "dimana", "di mana", "where", "cari", "looking for",
            "recommend", "rekomendasi", "suggest", "sarani",
            "ada", "is there", "are there", "tolong", "please"
        ]
        
        for word in question_words:
            query = re.sub(rf"\b{word}\b", "", query, flags=re.IGNORECASE)
        
        result["query"] = query.strip()
        
        return result
    
    async def _search_locations(
        self,
        query: str,
        location: Optional[str] = None,
        max_results: int = 3
    ) -> Optional[Dict]:
        """
        Memanggil backend API untuk mencari lokasi.
        
        Args:
            query: Query pencarian
            location: Lokasi spesifik (kota, daerah)
            max_results: Jumlah maksimal hasil
        
        Returns:
            Response dari backend API
        """
        api_url = f"{self.backend_url.rstrip('/')}/api/v1/search-location"
        
        payload = {
            "query": query,
            "location": location,
            "max_results": max_results
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Add API secret if configured
        if self.api_secret:
            headers["X-API-Key"] = self.api_secret
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_data = await response.json()
                        print(f"[Google Maps Function] API Error: {error_data}")
                        return None
                        
        except aiohttp.ClientError as e:
            print(f"[Google Maps Function] Connection Error: {str(e)}")
            return None
        except Exception as e:
            print(f"[Google Maps Function] Unexpected Error: {str(e)}")
            return None
    
    def _generate_map_response(self, places_data: Dict) -> str:
        """
        Membuat response HTML dengan embedded Google Maps.
        
        Args:
            places_data: Data tempat dari backend API
        
        Returns:
            Formatted string dengan HTML untuk embed maps
        """
        places = places_data.get("places", [])
        
        if not places:
            return ""
        
        # Build HTML response
        html_parts = []
        
        # Header
        html_parts.append(f"<div style='font-family: Arial, sans-serif; margin: 20px 0;'>")
        html_parts.append(f"<h3 style='color: #1a73e8; margin-bottom: 15px;'>📍 {places_data.get('message', 'Lokasi Ditemukan')}</h3>")
        
        # Add each place
        for i, place in enumerate(places):
            html_parts.append(f"""
            <div style='border: 1px solid #e0e0e0; border-radius: 8px; margin: 15px 0; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                <div style='padding: 15px; background: #f8f9fa; border-bottom: 1px solid #e0e0e0;'>
                    <h4 style='margin: 0 0 8px 0; color: #202124;'>{i + 1}. {place.get('name', 'Unknown')}</h4>
                    <p style='margin: 0; color: #5f6368; font-size: 14px;'>📍 {place.get('address', 'Address not available')}</p>
                    {f"<p style='margin: 8px 0 0 0; color: #fbbc04; font-weight: bold;'>⭐ {place.get('rating', 'N/A')}</p>" if place.get('rating') else ""}
                </div>
                <div style='height: 300px; width: 100%;'>
                    <iframe 
                        width="100%" 
                        height="100%" 
                        style="border:0;" 
                        loading="lazy" 
                        allowfullscreen 
                        referrerpolicy="no-referrer-when-downgrade"
                        src="{place.get('embed_url', '')}">
                    </iframe>
                </div>
                <div style='padding: 12px; background: #fff;'>
                    <a href="{place.get('directions_url', '')}" 
                       target="_blank" 
                       style='display: inline-block; padding: 10px 20px; background: #1a73e8; color: white; text-decoration: none; border-radius: 4px; font-weight: 500;'>
                        🗺️ Petunjuk Arah
                    </a>
                    <a href="https://www.google.com/maps/place/?q=place_id:{place.get('place_id', '')}" 
                       target="_blank" 
                       style='display: inline-block; padding: 10px 20px; background: #34a853; color: white; text-decoration: none; border-radius: 4px; font-weight: 500; margin-left: 8px;'>
                        📌 Lihat di Google Maps
                    </a>
                </div>
            </div>
            """)
        
        # Footer
        html_parts.append("</div>")
        
        return "".join(html_parts)


# Filter configuration untuk Open WebUI
valves = {
    "BACKEND_API_URL": {
        "type": "string",
        "description": "URL backend FastAPI (contoh: http://localhost:8000)",
        "required": True,
        "default": "http://localhost:8000"
    },
    "API_SECRET": {
        "type": "string",
        "description": "API Secret untuk autentikasi (opsional)",
        "required": False,
        "default": ""
    }
}

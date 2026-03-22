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
   - GOOGLE_MAPS_API_KEY: Google Maps API Key (opsional, untuk direct API call)
5. Enable function dan simpan
"""

import os
import re
import json
import aiohttp
from typing import Optional, Dict, Any, List


# ============================================================================
# CONFIGURATION - VALVES
# ============================================================================
class Valves:
    """
    Configuration valves untuk Open WebUI Functions.
    Nilai-nilai ini bisa di-set dari UI Open WebUI.
    """
    BACKEND_API_URL: str = "http://localhost:8000"
    API_SECRET: str = "your_secret_api_key_here_change_in_production"
    GOOGLE_MAPS_API_KEY: str = ""
    ENABLE_DIRECT_GOOGLE_API: bool = False
    MAX_RESULTS: int = 3


# ============================================================================
# MAIN PIPE CLASS
# ============================================================================
class Pipe:
    """
    Main Pipe class untuk Open WebUI Functions.
    Class ini akan dipanggil oleh Open WebUI untuk memproses user messages.
    """
    
    def __init__(self):
        """
        Initialize Pipe class dengan configuration dari valves.
        """
        # Initialize valves
        self.valves = Valves()
        
        # Metadata
        self.name = "Google Maps Location Finder"
        self.description = "Menampilkan Google Maps ketika user bertanya tentang lokasi"
        
        # Location intent keywords (Bahasa Indonesia & English)
        self.location_keywords = {
            # Indonesian - Food & Dining
            "restoran", "rumah makan", "kuliner", "makan", "minum", "cafe", "kedai", 
            "warung", "kantin", "food court", "street food",
            
            # Indonesian - Tourism & Recreation
            "tempat wisata", "wisata", "jalan-jalan", "liburan", "rekreasi", "tamasya",
            "objek wisata", "destinasi", "atraksi", "pemandangan",
            
            # Indonesian - Accommodation
            "hotel", "penginapan", "villa", "resort", "homestay", "guest house",
            "losmen", "hostel", "motel",
            
            # Indonesian - Shopping
            "mall", "pusat perbelanjaan", "belanja", "toko", "pasar", "supermarket",
            "minimarket", "distro", "butik",
            
            # Indonesian - Healthcare
            "rumah sakit", "klinik", "puskesmas", "apotek", "farmasi", "dokter",
            "ugd", "igd", "laboratorium",
            
            # Indonesian - Education
            "sekolah", "universitas", "kampus", "kursus", "les", "perpustakaan",
            "tk", "sd", "smp", "sma",
            
            # Indonesian - Sports & Fitness
            "gym", "fitness", "olahraga", "lapangan", "kolam renang", "stadion",
            "gelanggang", "gor", "tennis", "badminton",
            
            # Indonesian - Entertainment
            "bioskop", "teater", "museum", "galeri", "taman", "pantai", "gunung",
            "danau", "air terjun", "curug", "bukit",
            
            # Indonesian - Transportation
            "stasiun", "bandara", "terminal", "halte", "parkir", "pelabuhan",
            "dermaga",
            
            # Indonesian - Services
            "bengkel", "spbu", "pom bensin", "bank", "atm", "kantor pos",
            "polisi", "damkar",
            
            # Indonesian - Religious
            "masjid", "gereja", "pura", "vihara", "klenteng", "musholla",
            
            # Indonesian - Question Words
            "tempat", "lokasi", "dimana", "di mana", "dekat", "sekitar", "terdekat",
            "rekomendasi", "rekomendasi", "sarani", "suggest",
            
            # English - General
            "restaurant", "food", "eat", "drink", "cafe", "coffee", "dining",
            "tourist", "attraction", "travel", "vacation", "sightseeing", "destination",
            "hotel", "accommodation", "lodging", "resort", "stay",
            "mall", "shopping", "store", "market", "shop",
            "hospital", "clinic", "pharmacy", "drugstore", "medical",
            "school", "university", "college", "education",
            "gym", "fitness", "sport", "pool", "stadium",
            "cinema", "theater", "museum", "gallery", "park", "beach", "mountain",
            "station", "airport", "terminal", "parking", "harbor",
            "gas station", "workshop", "bank", "atm", "post office",
            "mosque", "church", "temple",
            "place", "location", "where", "near", "nearby", "around",
            "recommend", "recommendation", "best", "top"
        }
        
        # Indonesian cities for location extraction
        self.indonesian_cities = [
            "jakarta", "bandung", "surabaya", "yogyakarta", "semarang",
            "medan", "palembang", "makassar", "balikpapan", "manado",
            "denpasar", "bali", "lombok", "batam", "pekanbaru",
            "bogor", "depok", "tangerang", "bekasi", "serpong",
            "malang", "solo", "surakarta", "pontianak", "banjarmasin",
            "padang", "manado", "ambon", "jayapura", "sorong",
            "mataram", "kupang", "kendari", "palu", "gorontalo",
            "ternate", "tidore", "sorong", "madiin", "kediri",
            "blitar", "pasuruan", "probolinggo", "batu", "cirebon",
            "tasikmalaya", "sukabumi", "cianjur", "garut", "purwokerto",
            "magelang", "salatiga", "pekalongan", "tegal", "kudus",
            "jepara", "rembang", "pati", "blora", "wonogiri",
            "klaten", "sleman", "bantul", "kulon progo", "gunung kidul"
        ]
    
    async def pipe(
        self,
        body: dict,
        __user__: dict = None
    ) -> Optional[str]:
        """
        Main method yang dipanggil oleh Open WebUI untuk memproses request.
        
        Args:
            body: Request body dari Open WebUI, berisi 'messages' dengan user message
            __user__: Informasi user (opsional)
        
        Returns:
            Formatted location results dengan Google Maps embed, atau None jika tidak ada location intent
        """
        try:
            # Extract user message from body
            messages = body.get("messages", [])
            if not messages:
                return None
            
            # Get last user message
            user_message = messages[-1].get("content", "")
            if not user_message:
                return None
            
            # Check if message contains location intent
            if not self._has_location_intent(user_message):
                return None
            
            # Extract location information
            location_info = self._extract_location_info(user_message)
            
            # Search for places
            if self.valves.ENABLE_DIRECT_GOOGLE_API and self.valves.GOOGLE_MAPS_API_KEY:
                # Direct Google Maps API call
                places = await self._search_google_maps_direct(
                    query=location_info["query"],
                    location=location_info.get("location"),
                    max_results=self.valves.MAX_RESULTS
                )
            else:
                # Call backend API
                places = await self._search_backend_api(
                    query=location_info["query"],
                    location=location_info.get("location"),
                    max_results=self.valves.MAX_RESULTS
                )
            
            # Generate and return formatted response
            if places and len(places) > 0:
                return self._generate_location_response(places, location_info["query"])
            
            # No places found, let LLM handle
            return None
            
        except Exception as e:
            print(f"[Google Maps Function] Error: {str(e)}")
            return None
    
    def _has_location_intent(self, message: str) -> bool:
        """
        Mendeteksi apakah pesan user mengandung intent terkait lokasi.
        
        Args:
            message: Pesan dari user
        
        Returns:
            True jika pesan mengandung intent lokasi
        """
        message_lower = message.lower()
        
        # Check for location question patterns (Indonesian & English)
        location_patterns = [
            # Indonesian patterns
            r"(dimana|di mana|where).*(bisa|boleh|dapat).*(makan|wisata|belanja)",
            r"(rekomendasi|recommend|suggest|sarani).*(restoran|restaurant|hotel|wisata|cafe)",
            r"(makan|eat|food|kuliner).*(dekat|near|sekitar|around|terdekat)",
            r"(wisata|tourist|jalan).*(dekat|near|sekitar|around|terdekat)",
            r"(cari|looking|search|mencari).*(restoran|hotel|tempat|place|wisata)",
            r"(tempat|place).*(makan|eat|wisata|tourist|jalan|hotel|belanja)",
            r"(ada|is there|are there).*(restoran|hotel|wisata|cafe|tempat)",
            r"(dekat|near|sekitar|around).*(sini|here|sana|there)",
            r"(lokasi|location).*(terdekat|nearest|dekat)",
        ]
        
        # Check patterns first (higher priority)
        for pattern in location_patterns:
            if re.search(pattern, message_lower):
                return True
        
        # Count location keywords
        keyword_count = sum(1 for keyword in self.location_keywords if keyword in message_lower)
        
        # Require at least 2 location-related keywords to trigger
        return keyword_count >= 2
    
    def _extract_location_info(self, message: str) -> Dict[str, Any]:
        """
        Mengekstrak informasi lokasi dari pesan user.
        
        Args:
            message: Pesan dari user
        
        Returns:
            Dict dengan query dan location
        """
        result = {
            "query": message.strip(),
            "location": None
        }
        
        message_lower = message.lower()
        
        # Check for Indonesian city mentions
        for city in self.indonesian_cities:
            if city in message_lower:
                result["location"] = city.capitalize()
                break
        
        # Check for "di [location]" pattern (Indonesian)
        di_pattern = r"\bdi\s+(\w+)"
        match = re.search(di_pattern, message_lower)
        if match:
            potential_location = match.group(1)
            if potential_location not in ["sini", "situ", "mana", "where", "the", "a", "ini", "itu"]:
                result["location"] = potential_location.capitalize()
        
        # Check for "in [location]" pattern (English)
        in_pattern = r"\bin\s+(\w+)"
        match = re.search(in_pattern, message_lower)
        if match and not result["location"]:
            potential_location = match.group(1)
            if potential_location not in ["the", "a", "this", "that", "here", "there"]:
                result["location"] = potential_location.capitalize()
        
        # Extract the main query (remove question words)
        query = message
        question_words = [
            "dimana", "di mana", "where", "cari", "looking for", "mencari",
            "recommend", "rekomendasi", "suggest", "sarani", "saran",
            "ada", "is there", "are there", "tolong", "please", "bisa",
            "boleh", "dapat", "show", "tampilkan", "carikan"
        ]
        
        for word in question_words:
            query = re.sub(rf"\b{word}\b", "", query, flags=re.IGNORECASE)
        
        result["query"] = query.strip()
        
        return result
    
    async def _search_backend_api(
        self,
        query: str,
        location: Optional[str] = None,
        max_results: int = 3
    ) -> Optional[List[Dict]]:
        """
        Memanggil backend API untuk mencari lokasi.
        
        Args:
            query: Query pencarian
            location: Lokasi spesifik (kota, daerah)
            max_results: Jumlah maksimal hasil
        
        Returns:
            List tempat dari backend API
        """
        api_url = f"{self.valves.BACKEND_API_URL.rstrip('/')}/api/v1/search-location"
        
        payload = {
            "query": query,
            "location": location,
            "max_results": max_results
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Add API secret if configured
        if self.valves.API_SECRET and self.valves.API_SECRET != "":
            headers["X-API-Key"] = self.valves.API_SECRET
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, json=payload, headers=headers, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("success") and data.get("places"):
                            return data.get("places")
                    else:
                        error_data = await response.json()
                        print(f"[Google Maps Function] Backend API Error: {error_data}")
                    return None
                        
        except aiohttp.ClientError as e:
            print(f"[Google Maps Function] Connection Error: {str(e)}")
            return None
        except Exception as e:
            print(f"[Google Maps Function] Unexpected Error: {str(e)}")
            return None
    
    async def _search_google_maps_direct(
        self,
        query: str,
        location: Optional[str] = None,
        max_results: int = 3
    ) -> Optional[List[Dict]]:
        """
        Direct call to Google Places API (fallback jika backend tidak tersedia).
        
        Args:
            query: Query pencarian
            location: Lokasi spesifik
            max_results: Jumlah maksimal hasil
        
        Returns:
            List tempat dari Google Places API
        """
        if not self.valves.GOOGLE_MAPS_API_KEY:
            return None
        
        search_query = query
        if location:
            search_query = f"{query} in {location}"
        
        url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {
            "query": search_query,
            "key": self.valves.GOOGLE_MAPS_API_KEY,
            "max_results": max_results
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = data.get("results", [])[:max_results]
                        
                        places = []
                        for place in results:
                            place_id = place.get("place_id", "")
                            embed_url = f"https://www.google.com/maps/embed/v1/place?key={self.valves.GOOGLE_MAPS_API_KEY}&q=place_id:{place_id}"
                            directions_url = f"https://www.google.com/maps/dir/?api=1&destination=place_id:{place_id}"
                            
                            places.append({
                                "name": place.get("name", "Unknown"),
                                "address": place.get("formatted_address", "Address not available"),
                                "place_id": place_id,
                                "rating": place.get("rating"),
                                "types": place.get("types", []),
                                "embed_url": embed_url,
                                "directions_url": directions_url
                            })
                        
                        return places
                    else:
                        print(f"[Google Maps Function] Google API Error: {response.status}")
                        return None
                        
        except Exception as e:
            print(f"[Google Maps Function] Google API Error: {str(e)}")
            return None
    
    def _generate_location_response(
        self,
        places: List[Dict],
        query: str
    ) -> str:
        """
        Membuat response HTML dengan embedded Google Maps.
        
        Args:
            places: List tempat dari API
            query: Query pencarian original
        
        Returns:
            Formatted HTML string dengan Google Maps embed
        """
        if not places:
            return ""
        
        # Build HTML response
        html_parts = []
        
        # Header
        html_parts.append("<div style='font-family: Arial, sans-serif; margin: 20px 0;'>")
        html_parts.append(f"<h3 style='color: #1a73e8; margin-bottom: 15px; font-size: 20px;'>📍 Hasil untuk: \"{query}\"</h3>")
        html_parts.append(f"<p style='color: #5f6368; margin-bottom: 20px;'>Ditemukan {len(places)} tempat</p>")
        
        # Add each place
        for i, place in enumerate(places):
            rating_html = ""
            if place.get("rating"):
                stars = "⭐" * int(place.get("rating", 0) / 2)
                rating_html = f"<p style='margin: 8px 0 0 0; color: #fbbc04; font-weight: bold;'>{stars} {place.get('rating', 'N/A')}</p>"
            
            types_html = ""
            if place.get("types"):
                place_types = place.get("types", [])[:3]
                types_html = f"<p style='margin: 8px 0 0 0; color: #5f6368; font-size: 12px;'>🏷️ {', '.join(place_types)}</p>"
            
            html_parts.append(f"""
            <div style='border: 1px solid #e0e0e0; border-radius: 8px; margin: 15px 0; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
                <div style='padding: 15px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;'>
                    <h4 style='margin: 0 0 8px 0; font-size: 18px;'>{i + 1}. {place.get('name', 'Unknown')}</h4>
                    <p style='margin: 0; opacity: 0.9; font-size: 14px;'>📍 {place.get('address', 'Address not available')}</p>
                    {rating_html}
                    {types_html}
                </div>
                <div style='height: 300px; width: 100%; background: #f0f0f0;'>
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
                <div style='padding: 15px; background: #fff; display: flex; gap: 10px; flex-wrap: wrap;'>
                    <a href="{place.get('directions_url', '')}" 
                       target="_blank" 
                       rel="noopener noreferrer"
                       style='display: inline-block; padding: 10px 20px; background: #1a73e8; color: white; text-decoration: none; border-radius: 6px; font-weight: 500; font-size: 14px;'>
                        🗺️ Petunjuk Arah
                    </a>
                    <a href="https://www.google.com/maps/place/?q=place_id:{place.get('place_id', '')}" 
                       target="_blank" 
                       rel="noopener noreferrer"
                       style='display: inline-block; padding: 10px 20px; background: #34a853; color: white; text-decoration: none; border-radius: 6px; font-weight: 500; font-size: 14px;'>
                        📌 Lihat di Google Maps
                    </a>
                    {f"<a href='tel:+62' style='display: inline-block; padding: 10px 20px; background: #fbbc04; color: #202124; text-decoration: none; border-radius: 6px; font-weight: 500; font-size: 14px;'>📞 Hubungi</a>" if place.get('phone') else ""}
                </div>
            </div>
            """)
        
        # Footer
        html_parts.append("</div>")
        
        return "".join(html_parts)


# ============================================================================
# HELPER FUNCTIONS (Optional)
# ============================================================================

def test_location_detection():
    """Test function untuk location intent detection."""
    pipe = Pipe()
    
    test_messages = [
        "Rekomendasi restoran enak di Jakarta?",
        "Dimana tempat wisata di Bandung?",
        "Cari cafe terdekat untuk kerja",
        "Hotel terbaik di Yogyakarta untuk keluarga",
        "What are the best restaurants near me?",
        "Where can I eat around here?",
        "Tempat belanja di Surabaya",
        "Rumah makan padang terdekat"
    ]
    
    for msg in test_messages:
        has_intent = pipe._has_location_intent(msg)
        location_info = pipe._extract_location_info(msg)
        print(f"✓ {msg}")
        print(f"  Intent: {has_intent}, Location: {location_info.get('location')}")
        print()


if __name__ == "__main__":
    # Run test if executed directly
    test_location_detection()

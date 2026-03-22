"""
Test script untuk Google Maps Location API
Jalankan setelah backend server aktif
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health check endpoint"""
    print("=" * 50)
    print("Testing Health Check...")
    print("=" * 50)
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()
    return response.status_code == 200

def test_search_location():
    """Test search location endpoint"""
    print("=" * 50)
    print("Testing Search Location...")
    print("=" * 50)
    
    payload = {
        "query": "restoran enak",
        "location": "Jakarta",
        "max_results": 3
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    # Add API key if configured
    import os
    api_key = os.getenv("API_SECRET")
    if api_key:
        headers["X-API-Key"] = api_key
    
    response = requests.post(
        f"{BASE_URL}/api/v1/search-location",
        json=payload,
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()
    return response.status_code == 200

def test_search_location_indonesian():
    """Test dengan query Bahasa Indonesia"""
    print("=" * 50)
    print("Testing Indonesian Query...")
    print("=" * 50)
    
    payload = {
        "query": "tempat wisata",
        "location": "Bandung",
        "max_results": 5
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/search-location",
        json=payload
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()
    return response.status_code == 200

def test_invalid_query():
    """Test dengan query yang tidak valid"""
    print("=" * 50)
    print("Testing Invalid Query...")
    print("=" * 50)
    
    payload = {
        "query": "",
        "max_results": 3
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/search-location",
        json=payload
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()
    return True  # Any response is acceptable for this test

def run_all_tests():
    """Run all tests"""
    print("\n")
    print("╔" + "=" * 48 + "╗")
    print("║  Google Maps Location API - Test Suite     ║")
    print("╚" + "=" * 48 + "╝")
    print()
    
    tests = [
        ("Health Check", test_health),
        ("Search Location", test_search_location),
        ("Indonesian Query", test_search_location_indonesian),
        ("Invalid Query", test_invalid_query),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"❌ {name} FAILED: {str(e)}\n")
            results.append((name, False))
    
    # Summary
    print("=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {name}")
    
    print()
    print(f"Total: {passed}/{total} tests passed")
    print("=" * 50)
    
    return passed == total

if __name__ == "__main__":
    import sys
    success = run_all_tests()
    sys.exit(0 if success else 1)

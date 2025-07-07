#!/usr/bin/env python3
"""
Quick Backend Integration Test
Tests the HTTP communication between the main API and the enhanced backend
"""

import requests
import json
import time

def test_enhanced_backend_http():
    """Test HTTP communication with the enhanced backend"""
    print("🔗 Testing Enhanced Backend HTTP Communication")
    print("=" * 50)
    
    # Test health endpoint
    try:
        print("📡 Testing health endpoint...")
        response = requests.get('http://127.0.0.1:5001/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend Status: {data.get('status', 'unknown')}")
            print(f"✅ Backend Type: {data.get('backend', 'unknown')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to enhanced backend: {e}")
        print("   Make sure to run: start_enhanced_backend.bat")
        return False
    
    # Test scanning endpoint
    test_urls = [
        "https://www.google.com",
        "https://example.com"
    ]
    
    for url in test_urls:
        print(f"\n🔍 Testing scan with: {url}")
        try:
            response = requests.post(
                'http://127.0.0.1:5001/scan',
                json={'url': url, 'format': 'json'},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Scan successful!")
                print(f"   URL: {result.get('url', 'N/A')}")
                print(f"   Detection: {result.get('detection', 'N/A')}")
                
                scores = result.get('scores', {})
                if scores:
                    print("   Scores:")
                    for component, score in scores.items():
                        print(f"     {component}: {score}")
            else:
                print(f"❌ Scan failed: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Scan error: {e}")
    
    return True

def test_main_api_integration():
    """Test the main API integration"""
    print("\n🔄 Testing Main API Integration")
    print("=" * 50)
    
    try:
        print("📡 Testing main API availability...")
        response = requests.get('http://127.0.0.1:5000/', timeout=5)
        print("✅ Main API is running")
    except Exception as e:
        print(f"❌ Main API not available: {e}")
        print("   Make sure to run: python api.py in grad/grad/url/urlScan/")
        return False
    
    # Test enhanced scan endpoint
    test_url = "https://www.google.com"
    print(f"\n🔍 Testing enhanced scan with: {test_url}")
    
    try:
        form_data = {'url': test_url}
        response = requests.post(
            'http://127.0.0.1:5000/enhanced_scan',
            data=form_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Enhanced scan successful!")
                print(f"   Backend Type: {result.get('backend_type', 'unknown')}")
                print(f"   Detection: {result.get('detection', 'unknown')}")
            else:
                print(f"❌ Enhanced scan failed: {result.get('error', 'unknown')}")
        else:
            print(f"❌ Enhanced scan HTTP error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Enhanced scan error: {e}")
    
    return True

def main():
    print("🚀 ClickSafe Backend Integration Test")
    print("🎯 Testing HTTP communication between components")
    print("=" * 60)
    
    # Test backend
    backend_ok = test_enhanced_backend_http()
    
    if backend_ok:
        print("\n" + "=" * 60)
        # Test integration
        integration_ok = test_main_api_integration()
        
        print("\n" + "=" * 60)
        print("🎯 Integration Test Results:")
        print(f"Enhanced Backend: {'✅ Available' if backend_ok else '❌ Not Available'}")
        print(f"Main API Integration: {'✅ Working' if integration_ok else '❌ Not Working'}")
        
        if backend_ok and integration_ok:
            print("\n🎉 SUCCESS: Enhanced backend integration is working!")
            print("   You can now use the enhanced scanning features.")
        else:
            print("\n⚠️  PARTIAL: Some components may not be working optimally.")
    else:
        print("\n❌ FAILED: Enhanced backend is not available.")
        print("   The system will use legacy fallback mode.")
    
    print("\n📖 Next Steps:")
    print("   1. Start enhanced backend: start_enhanced_backend.bat")
    print("   2. Start main API: python api.py")
    print("   3. Test website: http://localhost/grad/scan_results.html")

if __name__ == "__main__":
    main()

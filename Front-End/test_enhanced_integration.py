#!/usr/bin/env python3
"""
Enhanced Backend Integration Test Script
Tests the integration between the new backend and the existing frontend
"""

import requests
import json
import time
import sys

def test_backend_connection():
    """Test if the enhanced backend is running"""
    try:
        response = requests.get('http://127.0.0.1:5001/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Enhanced backend is running")
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   Backend: {data.get('backend', 'unknown')}")
            return True
        else:
            print(f"❌ Enhanced backend returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Enhanced backend connection failed: {e}")
        return False

def test_main_api_connection():
    """Test if the main API is running"""
    try:
        response = requests.get('http://127.0.0.1:5000/', timeout=5)
        print("✅ Main API is running")
        return True
    except Exception as e:
        print(f"❌ Main API connection failed: {e}")
        return False

def test_enhanced_scan(url="https://www.google.com"):
    """Test the enhanced scanning functionality"""
    print(f"\n🔍 Testing enhanced scan with URL: {url}")
    
    try:
        # Test the enhanced backend directly
        response = requests.post(
            'http://127.0.0.1:5001/scan',
            json={'url': url, 'format': 'json'},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Enhanced backend scan successful")
            print(f"   URL: {result.get('url', 'unknown')}")
            print(f"   Detection: {result.get('detection', 'unknown')}")
            
            scores = result.get('scores', {})
            if scores:
                print("   Scores:")
                for feature, score in scores.items():
                    print(f"     {feature}: {score}")
            
            return True
        else:
            print(f"❌ Enhanced backend scan failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Enhanced backend scan error: {e}")
        return False

def test_main_api_enhanced_scan(url="https://www.google.com"):
    """Test the main API enhanced scanning"""
    print(f"\n🔄 Testing main API enhanced scan with URL: {url}")
    
    try:
        # Test through the main API
        form_data = {'url': url}
        response = requests.post(
            'http://127.0.0.1:5000/enhanced_scan',
            data=form_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Main API enhanced scan successful")
                print(f"   URL: {result.get('url', 'unknown')}")
                print(f"   Detection: {result.get('detection', 'unknown')}")
                print(f"   Backend Type: {result.get('backend_type', 'unknown')}")
                return True
            else:
                print(f"❌ Main API enhanced scan failed: {result.get('error', 'unknown error')}")
                return False
        else:
            print(f"❌ Main API enhanced scan failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Main API enhanced scan error: {e}")
        return False

def test_legacy_fallback(url="https://www.google.com"):
    """Test the legacy fallback functionality"""
    print(f"\n🔄 Testing legacy fallback with URL: {url}")
    
    try:
        # Test the regular scanurl endpoint
        form_data = {'url': url}
        response = requests.post(
            'http://127.0.0.1:5000/scanurl',
            data=form_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Legacy fallback working")
            print(f"   Result available: {bool(result.get('result'))}")
            return True
        else:
            print(f"❌ Legacy fallback failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Legacy fallback error: {e}")
        return False

def main():
    print("🚀 Enhanced Backend Integration Test")
    print("=" * 50)
    
    # Test backend connections
    print("\n📡 Testing Backend Connections:")
    enhanced_backend_ok = test_backend_connection()
    main_api_ok = test_main_api_connection()
    
    if not main_api_ok:
        print("\n❌ Main API is not running. Please start it first.")
        sys.exit(1)
    
    # Test scanning functionality
    test_urls = [
        "https://www.google.com",
        "https://www.facebook.com",
        "https://example.com"
    ]
    
    for url in test_urls:
        if enhanced_backend_ok:
            test_enhanced_scan(url)
            test_main_api_enhanced_scan(url)
        else:
            print(f"\n⚠️ Enhanced backend not available, testing fallback for {url}")
        
        test_legacy_fallback(url)
        
        print("\n" + "-" * 30)
    
    print("\n🎯 Integration Test Summary:")
    print(f"Enhanced Backend: {'✅ Available' if enhanced_backend_ok else '❌ Not Available'}")
    print(f"Main API: {'✅ Available' if main_api_ok else '❌ Not Available'}")
    print(f"Integration Status: {'✅ Ready' if main_api_ok else '❌ Not Ready'}")
    
    if enhanced_backend_ok and main_api_ok:
        print("\n🎉 All systems operational! The enhanced backend integration is working correctly.")
    elif main_api_ok:
        print("\n⚠️ Legacy fallback mode operational. Enhanced backend not available.")
    else:
        print("\n❌ System not operational. Please check your setup.")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Quick Integration Test for ClickSafe Enhanced Backend
Tests the complete flow from main API to enhanced backend
"""

import sys
import os
import requests
import time
import json
import subprocess
from pathlib import Path

def test_backend_connectivity():
    """Test if the enhanced backend is running and responding"""
    print("🔍 Testing Enhanced Backend Connectivity...")
    
    try:
        # Test health endpoint
        response = requests.get('http://127.0.0.1:5001/health', timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Backend Health Check: {health_data}")
            return True
        else:
            print(f"❌ Backend health check failed with status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend not accessible: {e}")
        return False

def test_direct_backend_scan():
    """Test direct scanning via the enhanced backend"""
    print("\n🔍 Testing Direct Backend Scanning...")
    
    test_url = "https://www.google.com"
    
    try:
        response = requests.post(
            'http://127.0.0.1:5001/scan',
            json={'url': test_url, 'format': 'json'},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Direct scan successful!")
            print(f"   URL: {result.get('url', 'N/A')}")
            print(f"   Detection: {result.get('detection', 'N/A')}")
            print(f"   Scores: {result.get('scores', {})}")
            return True
        else:
            print(f"❌ Direct scan failed with status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Direct scan request failed: {e}")
        return False

def test_main_api_integration():
    """Test the main API integration with enhanced backend"""
    print("\n🔍 Testing Main API Integration...")
    
    test_url = "https://www.google.com"
    
    try:
        # Test the main API scanurl endpoint
        form_data = {'url': test_url}
        response = requests.post(
            'http://127.0.0.1:5000/scanurl',
            data=form_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Main API integration successful!")
            print(f"   Result available: {'result' in result}")
            print(f"   Enhanced data available: {'enhanced_data' in result}")
            
            if 'enhanced_data' in result:
                enhanced = result['enhanced_data']
                print(f"   Backend type: {enhanced.get('backend_type', 'N/A')}")
                print(f"   Detection: {enhanced.get('detection', 'N/A')}")
            
            return True
        else:
            print(f"❌ Main API integration failed with status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Main API integration test failed: {e}")
        return False

def test_enhanced_scan_endpoint():
    """Test the enhanced scan endpoint"""
    print("\n🔍 Testing Enhanced Scan Endpoint...")
    
    test_url = "https://www.facebook.com"
    
    try:
        form_data = {'url': test_url}
        response = requests.post(
            'http://127.0.0.1:5000/enhanced_scan',
            data=form_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Enhanced scan endpoint successful!")
            print(f"   Success: {result.get('success', False)}")
            print(f"   Backend type: {result.get('backend_type', 'N/A')}")
            print(f"   Detection: {result.get('detection', 'N/A')}")
            print(f"   Guest ID: {result.get('guest_id', 'N/A')}")
            return True
        else:
            print(f"❌ Enhanced scan failed with status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Enhanced scan test failed: {e}")
        return False

def check_backend_process():
    """Check if backend process is running"""
    print("\n🔍 Checking Backend Process Status...")
    
    try:
        # Try to connect to see if anything is listening on port 5001
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('127.0.0.1', 5001))
        sock.close()
        
        if result == 0:
            print("✅ Port 5001 is open (backend likely running)")
            return True
        else:
            print("❌ Port 5001 is not accessible (backend not running)")
            return False
    except Exception as e:
        print(f"❌ Error checking backend process: {e}")
        return False

def check_main_api_process():
    """Check if main API process is running"""
    print("\n🔍 Checking Main API Process Status...")
    
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('127.0.0.1', 5000))
        sock.close()
        
        if result == 0:
            print("✅ Port 5000 is open (main API likely running)")
            return True
        else:
            print("❌ Port 5000 is not accessible (main API not running)")
            return False
    except Exception as e:
        print(f"❌ Error checking main API process: {e}")
        return False

def main():
    """Run all integration tests"""
    print("=" * 60)
    print("🛡️  ClickSafe Enhanced Backend Integration Test")
    print("=" * 60)
    
    # Check if processes are running
    backend_running = check_backend_process()
    main_api_running = check_main_api_process()
    
    if not backend_running:
        print("\n⚠️  Enhanced backend (port 5001) is not running!")
        print("   Please start it using: start_enhanced_backend.bat")
        
    if not main_api_running:
        print("\n⚠️  Main API (port 5000) is not running!")
        print("   Please start it from: grad/grad/url/urlScan/api.py")
    
    if not (backend_running and main_api_running):
        print("\n❌ Cannot run integration tests without both services running")
        return False
    
    # Run tests
    tests = [
        ("Backend Connectivity", test_backend_connectivity),
        ("Direct Backend Scan", test_direct_backend_scan),
        ("Main API Integration", test_main_api_integration),
        ("Enhanced Scan Endpoint", test_enhanced_scan_endpoint),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, passed_test in results:
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{status} - {test_name}")
        if passed_test:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All integration tests passed! The enhanced backend is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the logs above for details.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

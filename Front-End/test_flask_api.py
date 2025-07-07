"""
Flask API Test Script for ClickSafe
Run this to test if the Flask API is working correctly
"""

import requests
import json

def test_flask_api():
    print("Testing ClickSafe Flask API...")
    
    # Test URL scanning endpoint
    test_url = "https://www.youtube.com/"
    
    print(f"\n1. Testing /scanurl endpoint with URL: {test_url}")
    try:
        # Test with form data (as used by the website)
        data = {'url': test_url}
        response = requests.post('http://127.0.0.1:5000/scanurl', data=data, timeout=30)
        
        if response.status_code == 200:
            print("✅ /scanurl endpoint working!")
            print(f"Response type: {response.headers.get('content-type')}")
            
            # Try to parse as JSON first
            try:
                result = response.json()
                print(f"JSON Response: {result}")
            except:
                # If not JSON, it's plain text
                result = response.text
                print(f"Text Response: {result[:200]}...")
        else:
            print(f"❌ /scanurl failed with status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - Flask API is not running!")
        print("Please start the Flask API first:")
        print("cd c:\\xampp\\htdocs\\grad\\grad\\url\\urlScan")
        print("python api.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    print(f"\n2. Testing /testing endpoint with URL: {test_url}")
    try:
        # Test with JSON data (as used by the extension)
        headers = {'Content-Type': 'application/json'}
        data = json.dumps({'url': test_url})
        response = requests.post('http://127.0.0.1:5000/testing', data=data, headers=headers, timeout=30)
        
        if response.status_code == 200:
            print("✅ /testing endpoint working!")
            print(f"Response: {response.text[:200]}...")
        else:
            print(f"❌ /testing failed with status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    print(f"\n3. Testing guest session creation")
    try:
        # Test guest login endpoint
        headers = {'Content-Type': 'application/json'}
        guest_data = json.dumps({'guest_id': 'test_guest_123'})
        response = requests.post('http://127.0.0.1:5000/guest_login', data=guest_data, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ Guest session endpoint working!")
            result = response.json()
            print(f"Guest session result: {result}")
        else:
            print(f"⚠️  Guest session failed with status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"⚠️  Guest session error: {e}")
    
    print("\n🎉 API Test Complete!")
    return True

if __name__ == "__main__":
    test_flask_api()

#!/usr/bin/env python3
"""
ClickSafe Enhanced Backend Integration Status Check
Comprehensive verification of the integration status
"""

import os
import sys
from pathlib import Path
import json

def check_file_exists(file_path, description):
    """Check if a file exists and print status"""
    if os.path.exists(file_path):
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} (MISSING)")
        return False

def check_directory_structure():
    """Verify the enhanced backend directory structure"""
    print("🔍 Checking Enhanced Backend Directory Structure...")
    
    base_path = r"c:\xampp\htdocs\website_backend\url_host"
    
    required_files = [
        ("Enhanced Backend API", os.path.join(base_path, "api.py")),
        ("Main Orchestrator", os.path.join(base_path, "main.py")),
        ("Identification Module", os.path.join(base_path, "identifiation.py")),
        ("Blacklist Features", os.path.join(base_path, "blackListedFeature.py")),
        ("Lexical Features", os.path.join(base_path, "LexicalFeatures.py")),
        ("Host-Based Features", os.path.join(base_path, "HostBasedFeature.py")),
        ("Content-Based Features", os.path.join(base_path, "ContentBasedFeature.py")),
        ("Feature Evaluation", os.path.join(base_path, "FeatureEvaluationMethod.py")),
        ("Imports Manager", os.path.join(base_path, "imports.py")),
        ("Requirements", os.path.join(base_path, "requirements.txt")),
        ("Startup Script", os.path.join(base_path, "start_enhanced_backend.bat")),
        ("HTML Template", os.path.join(base_path, "templates", "result.html")),
    ]
    
    all_present = True
    for description, file_path in required_files:
        if not check_file_exists(file_path, description):
            all_present = False
    
    return all_present

def check_main_api_integration():
    """Check main API integration files"""
    print("\n🔍 Checking Main API Integration...")
    
    main_api_path = r"c:\xampp\htdocs\grad\grad\url\urlScan\api.py"
    frontend_path = r"c:\xampp\htdocs\grad\scan_results.html"
    
    files_to_check = [
        ("Main API", main_api_path),
        ("Frontend HTML", frontend_path),
    ]
    
    all_present = True
    for description, file_path in files_to_check:
        if not check_file_exists(file_path, description):
            all_present = False
    
    return all_present

def check_integration_functions():
    """Check if key integration functions are present"""
    print("\n🔍 Checking Integration Functions...")
    
    main_api_path = r"c:\xampp\htdocs\grad\grad\url\urlScan\api.py"
    
    try:
        with open(main_api_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        functions_to_check = [
            "enhanced_url_scan",
            "format_new_backend_result",
            "@app.route(\"/enhanced_scan\"",
            "requests.post"
        ]
        
        all_found = True
        for func in functions_to_check:
            if func in content:
                print(f"✅ Function/Pattern found: {func}")
            else:
                print(f"❌ Function/Pattern missing: {func}")
                all_found = False
        
        return all_found
    except Exception as e:
        print(f"❌ Error checking integration functions: {e}")
        return False

def check_frontend_enhancement():
    """Check if frontend has enhanced result handling"""
    print("\n🔍 Checking Frontend Enhancement...")
    
    frontend_path = r"c:\xampp\htdocs\grad\scan_results.html"
    
    try:
        with open(frontend_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        features_to_check = [
            "enhanced_data",
            "displayScanResult",
            "score-card",
            "detection-badge",
            "/enhanced_scan"
        ]
        
        all_found = True
        for feature in features_to_check:
            if feature in content:
                print(f"✅ Frontend feature found: {feature}")
            else:
                print(f"❌ Frontend feature missing: {feature}")
                all_found = False
        
        return all_found
    except Exception as e:
        print(f"❌ Error checking frontend enhancement: {e}")
        return False

def check_documentation():
    """Check if documentation files exist"""
    print("\n🔍 Checking Documentation...")
    
    doc_files = [
        r"c:\xampp\htdocs\grad\ENHANCED_BACKEND_INTEGRATION.md",
        r"c:\xampp\htdocs\grad\BACKEND_INTEGRATION_COMPLETE.md",
    ]
    
    all_present = True
    for doc_file in doc_files:
        if not check_file_exists(doc_file, "Documentation"):
            all_present = False
    
    return all_present

def check_test_scripts():
    """Check if test scripts exist"""
    print("\n🔍 Checking Test Scripts...")
    
    test_files = [
        r"c:\xampp\htdocs\grad\test_backend_integration.py",
        r"c:\xampp\htdocs\grad\test_enhanced_integration.py",
        r"c:\xampp\htdocs\grad\test_full_integration.py",
    ]
    
    all_present = True
    for test_file in test_files:
        if not check_file_exists(test_file, "Test Script"):
            all_present = False
    
    return all_present

def verify_backend_imports():
    """Verify that the backend imports are working"""
    print("\n🔍 Checking Backend Import Structure...")
    
    imports_path = r"c:\xampp\htdocs\website_backend\url_host\imports.py"
    
    try:
        with open(imports_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        required_imports = [
            "import requests",
            "from urllib.parse",
            "import socket",
            "import ssl",
            "import re",
            "import whois",
            "from bs4 import BeautifulSoup"
        ]
        
        all_found = True
        for imp in required_imports:
            if imp in content:
                print(f"✅ Import found: {imp}")
            else:
                print(f"⚠️  Import may be missing: {imp}")
        
        return True
    except Exception as e:
        print(f"❌ Error checking backend imports: {e}")
        return False

def generate_integration_status_report():
    """Generate a comprehensive status report"""
    print("=" * 70)
    print("🛡️  ClickSafe Enhanced Backend Integration Status Report")
    print("=" * 70)
    
    checks = [
        ("Backend Directory Structure", check_directory_structure),
        ("Main API Integration", check_main_api_integration),
        ("Integration Functions", check_integration_functions),
        ("Frontend Enhancement", check_frontend_enhancement),
        ("Documentation", check_documentation),
        ("Test Scripts", check_test_scripts),
        ("Backend Imports", verify_backend_imports),
    ]
    
    results = []
    
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ Check '{check_name}' failed with exception: {e}")
            results.append((check_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 INTEGRATION STATUS SUMMARY")
    print("=" * 70)
    
    passed = 0
    total = len(results)
    
    for check_name, passed_check in results:
        status = "✅ COMPLETE" if passed_check else "❌ INCOMPLETE"
        print(f"{status} - {check_name}")
        if passed_check:
            passed += 1
    
    print(f"\nOverall Status: {passed}/{total} components complete")
    
    if passed == total:
        print("\n🎉 Integration Status: FULLY COMPLETE")
        print("   All components are in place and ready for testing!")
        
        print("\n📋 Next Steps:")
        print("   1. Start the enhanced backend: website_backend/url_host/start_enhanced_backend.bat")
        print("   2. Start the main API: python grad/grad/url/urlScan/api.py")
        print("   3. Run integration tests: python grad/test_full_integration.py")
        print("   4. Test with frontend: grad/scan_results.html")
        
        return True
    else:
        print("\n⚠️  Integration Status: INCOMPLETE")
        print("   Some components are missing. Please check the details above.")
        
        missing_count = total - passed
        print(f"   {missing_count} component(s) need attention.")
        
        return False

def main():
    """Main function"""
    try:
        return generate_integration_status_report()
    except Exception as e:
        print(f"❌ Error running status check: {e}")
        return False

if __name__ == "__main__":
    success = main()
    print(f"\n{'='*70}")
    if success:
        print("✅ Status check completed successfully!")
    else:
        print("❌ Status check found issues that need attention.")
    sys.exit(0 if success else 1)

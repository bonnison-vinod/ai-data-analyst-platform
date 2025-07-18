#!/usr/bin/env python3
"""
Simple test script to verify API connectivity
"""

import requests
import json

API_BASE = "http://127.0.0.1:8000/api"

def test_api_connectivity():
    """Test if API is accessible"""
    try:
        response = requests.get(f"{API_BASE}/sessions/")
        print(f"API Status: {response.status_code}")
        print(f"API Response: {response.json()}")
        return True
    except Exception as e:
        print(f"API Error: {e}")
        return False

def test_file_upload():
    """Test file upload with a simple CSV"""
    try:
        # Create a simple test CSV
        csv_content = "name,age,city\nJohn,25,New York\nJane,30,San Francisco\nBob,35,Chicago"
        
        files = {
            'file': ('test.csv', csv_content, 'text/csv')
        }
        
        data = {
            'question': 'What is the average age?'
        }
        
        response = requests.post(f"{API_BASE}/generate-enhanced-report/", files=files, data=data)
        print(f"Upload Status: {response.status_code}")
        print(f"Upload Response: {response.json()}")
        
        if response.status_code == 200:
            return response.json().get('session_id')
        else:
            return None
            
    except Exception as e:
        print(f"Upload Error: {e}")
        return None

def test_progress_check(session_id):
    """Test progress checking"""
    try:
        response = requests.get(f"{API_BASE}/report-progress/{session_id}")
        print(f"Progress Status: {response.status_code}")
        print(f"Progress Response: {response.json()}")
        return True
    except Exception as e:
        print(f"Progress Error: {e}")
        return False

if __name__ == "__main__":
    print("Testing API connectivity...")
    
    # Test 1: API connectivity
    if not test_api_connectivity():
        print("❌ API not accessible. Make sure the backend is running.")
        exit(1)
    
    print("✅ API is accessible")
    
    # Test 2: File upload
    print("\nTesting file upload...")
    session_id = test_file_upload()
    
    if session_id:
        print(f"✅ File upload successful. Session ID: {session_id}")
        
        # Test 3: Progress check
        print("\nTesting progress check...")
        if test_progress_check(session_id):
            print("✅ Progress check successful")
        else:
            print("❌ Progress check failed")
    else:
        print("❌ File upload failed")

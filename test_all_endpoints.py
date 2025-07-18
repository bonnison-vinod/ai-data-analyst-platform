#!/usr/bin/env python3
"""
Comprehensive API Endpoint Testing Script
Tests all backend endpoints and reports their status
"""

import requests
import json
import os
import time
from datetime import datetime

# API Base URL
API_BASE = "http://localhost:8000/api"

class EndpointTester:
    def __init__(self):
        self.results = []
        self.test_file_path = "Backend/app/uploads/sample_data.csv"
        
    def log_result(self, endpoint, method, status, response_data=None, error=None):
        """Log test result"""
        result = {
            'endpoint': endpoint,
            'method': method,
            'status': 'PASS' if status == 'success' else 'FAIL',
            'response_code': response_data.get('status_code') if response_data else None,
            'error': error,
            'timestamp': datetime.now().isoformat()
        }
        self.results.append(result)
        
        # Print result
        status_emoji = "✅" if result['status'] == 'PASS' else "❌"
        print(f"{status_emoji} {method} {endpoint} - {result['status']}")
        if error:
            print(f"   Error: {error}")
        elif response_data and 'response' in response_data:
            print(f"   Response: {str(response_data['response'])[:100]}...")
        print()

    def test_get_endpoint(self, endpoint, description=""):
        """Test GET endpoint"""
        print(f"🔍 Testing GET {endpoint} - {description}")
        try:
            response = requests.get(f"{API_BASE}{endpoint}", timeout=10)
            if response.status_code == 200:
                self.log_result(endpoint, "GET", "success", {
                    'status_code': response.status_code,
                    'response': response.json() if response.content else "Empty response"
                })
                return response.json() if response.content else {}
            else:
                self.log_result(endpoint, "GET", "fail", {
                    'status_code': response.status_code
                }, f"HTTP {response.status_code}: {response.text[:200]}")
                return None
        except Exception as e:
            self.log_result(endpoint, "GET", "fail", None, str(e))
            return None

    def test_post_endpoint(self, endpoint, data=None, files=None, description=""):
        """Test POST endpoint"""
        print(f"🔍 Testing POST {endpoint} - {description}")
        try:
            if files:
                response = requests.post(f"{API_BASE}{endpoint}", files=files, data=data, timeout=30)
            else:
                response = requests.post(f"{API_BASE}{endpoint}", json=data, timeout=30)
            
            if response.status_code in [200, 201, 202]:
                self.log_result(endpoint, "POST", "success", {
                    'status_code': response.status_code,
                    'response': response.json() if response.content else "Empty response"
                })
                return response.json() if response.content else {}
            else:
                self.log_result(endpoint, "POST", "fail", {
                    'status_code': response.status_code
                }, f"HTTP {response.status_code}: {response.text[:200]}")
                return None
        except Exception as e:
            self.log_result(endpoint, "POST", "fail", None, str(e))
            return None

    def test_upload_endpoints(self):
        """Test file upload endpoints"""
        if not os.path.exists(self.test_file_path):
            print(f"❌ Test file not found: {self.test_file_path}")
            return None
            
        # Test simple upload
        with open(self.test_file_path, 'rb') as f:
            files = {'file': f}
            data = {'question': 'Test upload question'}
            result = self.test_post_endpoint('/upload/', data=data, files=files, 
                                           description="Simple file upload")
            
        # Test enhanced analysis
        with open(self.test_file_path, 'rb') as f:
            files = {'file': f}
            data = {
                'question': 'Test analysis question',
                'analysis_type': 'comprehensive',
                'custom_sheets': '[]'
            }
            result = self.test_post_endpoint('/generate-enhanced-report/', 
                                           data=data, files=files,
                                           description="Enhanced report generation")
            return result
            
        # Test magic question
        with open(self.test_file_path, 'rb') as f:
            files = {'file': f}
            data = {'question': 'What are the key insights in this data?'}
            self.test_post_endpoint('/magic-question/', data=data, files=files,
                                  description="Magic question analysis")

    def run_all_tests(self):
        """Run comprehensive endpoint testing"""
        print("🚀 Starting Comprehensive API Endpoint Testing")
        print("=" * 60)
        
        # 1. Health/Basic Endpoints
        print("\n📊 BASIC ENDPOINTS")
        print("-" * 30)
        self.test_get_endpoint('/sessions/', "List active sessions")
        
        # 2. Dashboard Endpoints  
        print("\n📈 DASHBOARD ENDPOINTS")
        print("-" * 30)
        self.test_get_endpoint('/dashboard/kpis', "Dashboard KPIs")
        self.test_post_endpoint('/dashboard/refresh', description="Refresh dashboard")
        
        # 3. Upload Endpoints
        print("\n📤 UPLOAD ENDPOINTS")
        print("-" * 30)
        session_result = self.test_upload_endpoints()
        
        # 4. Analysis Endpoints
        print("\n🔬 ANALYSIS ENDPOINTS")
        print("-" * 30)
        if session_result and 'session_id' in session_result:
            session_id = session_result['session_id']
            
            # Test progress tracking
            self.test_get_endpoint(f'/report-progress/{session_id}', 
                                 "Check analysis progress")
            
            # Wait a bit for processing
            time.sleep(3)
            
            # Test download
            self.test_get_endpoint(f'/download-report/{session_id}', 
                                 "Download analysis report")
        
        # 5. Direct Analysis Endpoints
        print("\n🧪 DIRECT ANALYSIS ENDPOINTS")
        print("-" * 30)
        if os.path.exists(self.test_file_path):
            with open(self.test_file_path, 'rb') as f:
                files = {'file': f}
                data = {'query': 'Test query', 'analysis_type': 'descriptive'}
                self.test_post_endpoint('/analyze', data=data, files=files,
                                      description="Direct analysis")
                
            with open(self.test_file_path, 'rb') as f:
                files = {'file': f}
                self.test_post_endpoint('/analyze-excel', files=files,
                                      description="Excel analysis")
        
        # 6. Database/API Endpoints (optional)
        print("\n🗄️ EXTERNAL DATA ENDPOINTS")
        print("-" * 30)
        # These might fail without proper credentials, but we test the endpoint
        db_data = {
            "connection_string": "sqlite:///test.db",
            "query": "SELECT 1 as test_col",
            "question": "Test database connection"
        }
        self.test_post_endpoint('/analyze-database/', data=db_data,
                              description="Database analysis (may fail without DB)")
        
        api_data = {
            "api_url": "https://jsonplaceholder.typicode.com/posts/1",
            "headers": {},
            "question": "Test API connection"
        }
        self.test_post_endpoint('/analyze-api/', data=api_data,
                              description="API data analysis")
        
        # 7. Session Management
        print("\n🔧 SESSION MANAGEMENT")
        print("-" * 30)
        sessions = self.test_get_endpoint('/sessions/', "List all sessions")
        if sessions and sessions.get('active_sessions'):
            for session_id in sessions['active_sessions'][:2]:  # Test first 2
                self.test_get_endpoint(f'/report-progress/{session_id}', 
                                     f"Progress for {session_id[:20]}...")

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📋 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r['status'] == 'PASS'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED ENDPOINTS:")
            for result in self.results:
                if result['status'] == 'FAIL':
                    print(f"   {result['method']} {result['endpoint']}: {result['error']}")
        
        print(f"\n✅ WORKING ENDPOINTS:")
        for result in self.results:
            if result['status'] == 'PASS':
                print(f"   {result['method']} {result['endpoint']}")

def main():
    print("🔬 AI Data Analyst Platform - Complete Endpoint Testing")
    print("📅 Started at:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print()
    
    # Check if backend is running
    try:
        response = requests.get("http://localhost:8000", timeout=5)
        print("✅ Backend server is running")
    except:
        print("❌ Backend server is not accessible at http://localhost:8000")
        print("Please make sure the backend is running before testing endpoints")
        return
    
    # Run tests
    tester = EndpointTester()
    tester.run_all_tests()
    tester.print_summary()
    
    # Save detailed results
    with open('endpoint_test_results.json', 'w') as f:
        json.dump(tester.results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: endpoint_test_results.json")
    print("🏁 Testing completed!")

if __name__ == "__main__":
    main()

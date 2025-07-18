#!/usr/bin/env python3
"""
Test script to call the enhanced analysis API endpoint
"""

import requests
import json
import time
import os

def test_enhanced_analysis():
    # API endpoint
    base_url = "http://localhost:8000/api"
    
    # File to upload
    file_path = "uploads/sample_data.csv"
    
    if not os.path.exists(file_path):
        print(f"File {file_path} not found!")
        return
    
    # Test data
    files = {'file': open(file_path, 'rb')}
    data = {
        'question': 'Analyze this sales data and provide comprehensive insights about sales performance, profit margins, and regional trends. Create visualizations and pivot tables.',
        'analysis_type': 'comprehensive',
        'custom_sheets': '[]'
    }
    
    print("🚀 Starting enhanced analysis test...")
    print(f"📄 File: {file_path}")
    print(f"❓ Question: {data['question']}")
    print("=" * 80)
    
    try:
        # Start analysis
        response = requests.post(f"{base_url}/generate-enhanced-report/", files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            session_id = result.get('session_id')
            
            print(f"✅ Analysis started successfully!")
            print(f"🆔 Session ID: {session_id}")
            print(f"📊 Status: {result.get('status')}")
            print(f"📈 Progress endpoint: {result.get('progress_endpoint')}")
            print(f"⬇️ Download endpoint: {result.get('download_endpoint')}")
            
            # Monitor progress
            print("\n📊 Monitoring progress...")
            while True:
                progress_response = requests.get(f"{base_url}/report-progress/{session_id}")
                if progress_response.status_code == 200:
                    progress = progress_response.json()
                    
                    status = progress.get('status')
                    percentage = progress.get('percentage', 0)
                    message = progress.get('message', '')
                    current_step = progress.get('current_step', '')
                    step_number = progress.get('current_step_number', 0)
                    total_steps = progress.get('total_steps', 6)
                    
                    print(f"📊 Progress: {percentage:.1f}% | Step {step_number}/{total_steps}: {current_step}")
                    print(f"💬 Message: {message}")
                    
                    if progress.get('completed'):
                        if progress.get('error'):
                            print(f"❌ Error: {progress.get('error')}")
                            break
                        else:
                            print("✅ Analysis completed successfully!")
                            
                            # Try to download the report
                            download_response = requests.get(f"{base_url}/download-report/{session_id}")
                            if download_response.status_code == 200:
                                # Save the report
                                report_filename = f"analysis_report_{session_id}.xlsx"
                                with open(report_filename, 'wb') as f:
                                    f.write(download_response.content)
                                print(f"📄 Report saved as: {report_filename}")
                                
                                # Check file size
                                file_size = os.path.getsize(report_filename)
                                print(f"📊 Report size: {file_size:,} bytes")
                                
                            else:
                                print(f"❌ Download failed: {download_response.status_code}")
                                print(f"Error: {download_response.text}")
                            break
                    
                    time.sleep(2)
                else:
                    print(f"❌ Progress check failed: {progress_response.status_code}")
                    break
                    
        else:
            print(f"❌ Analysis failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
    
    finally:
        files['file'].close()

def test_magic_question():
    """Test the magic question endpoint"""
    base_url = "http://localhost:8000/api"
    file_path = "uploads/sample_data.csv"
    
    if not os.path.exists(file_path):
        print(f"File {file_path} not found!")
        return
    
    files = {'file': open(file_path, 'rb')}
    data = {
        'question': 'What are the key trends in this sales data? Show me profit analysis by region and product category with charts.'
    }
    
    print("\n🎯 Testing Magic Question Analysis...")
    print(f"📄 File: {file_path}")
    print(f"❓ Question: {data['question']}")
    print("=" * 80)
    
    try:
        response = requests.post(f"{base_url}/magic-question/", files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            session_id = result.get('session_id')
            
            print(f"✅ Magic analysis started!")
            print(f"🆔 Session ID: {session_id}")
            print(f"🔮 Detected analysis: {json.dumps(result.get('detected_analysis', {}), indent=2)}")
            print(f"📊 Data info: {result.get('data_info')}")
            
            # Monitor progress (similar to enhanced analysis)
            print("\n📊 Monitoring magic analysis progress...")
            while True:
                progress_response = requests.get(f"{base_url}/report-progress/{session_id}")
                if progress_response.status_code == 200:
                    progress = progress_response.json()
                    
                    percentage = progress.get('percentage', 0)
                    message = progress.get('message', '')
                    current_step = progress.get('current_step', '')
                    
                    print(f"📊 Progress: {percentage:.1f}% | {current_step}: {message}")
                    
                    if progress.get('completed'):
                        if progress.get('error'):
                            print(f"❌ Error: {progress.get('error')}")
                        else:
                            print("✅ Magic analysis completed!")
                            # Try to download
                            download_response = requests.get(f"{base_url}/download-report/{session_id}")
                            if download_response.status_code == 200:
                                report_filename = f"magic_analysis_{session_id}.xlsx"
                                with open(report_filename, 'wb') as f:
                                    f.write(download_response.content)
                                print(f"📄 Magic report saved as: {report_filename}")
                            else:
                                print(f"❌ Download failed: {download_response.status_code}")
                        break
                    
                    time.sleep(2)
                else:
                    print(f"❌ Progress check failed: {progress_response.status_code}")
                    break
                    
        else:
            print(f"❌ Magic analysis failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Magic test failed: {str(e)}")
    
    finally:
        files['file'].close()

if __name__ == "__main__":
    print("🔬 AI Data Analyst Platform - Analysis Test")
    print("=" * 50)
    
    # Test enhanced analysis
    test_enhanced_analysis()
    
    # Test magic question
    test_magic_question()
    
    print("\n🏁 Testing completed!")

#!/usr/bin/env python3
"""
Comprehensive Backend Test Suite for AI-Enhanced XSS Scanner Platform
Tests all API endpoints, AI integration, and core functionality
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime
from typing import Dict, List, Any
import uuid

# Backend URL from environment
BACKEND_URL = "https://essentials-only.preview.emergentagent.com/api"

class XSSScanner_BackendTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.scan_ids = []
        self.vulnerability_ids = []
        
    async def setup(self):
        """Setup test session"""
        self.session = aiohttp.ClientSession()
        print("🔧 Backend Test Session Initialized")
        
    async def cleanup(self):
        """Cleanup test session"""
        if self.session:
            await self.session.close()
        print("🧹 Test Session Cleaned Up")
        
    def log_result(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        if response_data and not success:
            print(f"   Response: {response_data}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        
    async def test_create_scan(self):
        """Test POST /api/scans - Create new XSS scan"""
        test_name = "Create XSS Scan"
        
        try:
            scan_data = {
                "target_url": "https://testsite.com",
                "scan_type": "comprehensive",
                "include_forms": True,
                "include_urls": True,
                "max_depth": 3,
                "custom_payloads": [
                    "<script>alert('Custom XSS Test')</script>",
                    "<img src=x onerror=alert('Custom Test')>"
                ]
            }
            
            async with self.session.post(f"{BACKEND_URL}/scans", json=scan_data) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'id' in data and 'target_url' in data:
                        self.scan_ids.append(data['id'])
                        self.log_result(test_name, True, f"Scan created with ID: {data['id']}")
                        return data['id']
                    else:
                        self.log_result(test_name, False, "Response missing required fields", data)
                else:
                    error_text = await response.text()
                    self.log_result(test_name, False, f"HTTP {response.status}", error_text)
                    
        except Exception as e:
            self.log_result(test_name, False, f"Exception: {str(e)}")
            
        return None
        
    async def test_get_all_scans(self):
        """Test GET /api/scans - Get all scans"""
        test_name = "Get All Scans"
        
        try:
            async with self.session.get(f"{BACKEND_URL}/scans") as response:
                if response.status == 200:
                    data = await response.json()
                    if isinstance(data, list):
                        self.log_result(test_name, True, f"Retrieved {len(data)} scans")
                        return data
                    else:
                        self.log_result(test_name, False, "Response is not a list", data)
                else:
                    error_text = await response.text()
                    self.log_result(test_name, False, f"HTTP {response.status}", error_text)
                    
        except Exception as e:
            self.log_result(test_name, False, f"Exception: {str(e)}")
            
        return []
        
    async def test_get_scan_result(self, scan_id: str):
        """Test GET /api/scans/{scan_id}/result - Get scan results"""
        test_name = f"Get Scan Result ({scan_id[:8]}...)"
        
        try:
            # Wait a bit for background scan to process
            await asyncio.sleep(2)
            
            async with self.session.get(f"{BACKEND_URL}/scans/{scan_id}/result") as response:
                if response.status == 200:
                    data = await response.json()
                    if 'scan_id' in data and 'status' in data:
                        self.log_result(test_name, True, f"Status: {data['status']}, Vulnerabilities: {data.get('total_vulnerabilities', 0)}")
                        return data
                    else:
                        self.log_result(test_name, False, "Response missing required fields", data)
                elif response.status == 404:
                    self.log_result(test_name, False, "Scan result not found - may still be processing")
                else:
                    error_text = await response.text()
                    self.log_result(test_name, False, f"HTTP {response.status}", error_text)
                    
        except Exception as e:
            self.log_result(test_name, False, f"Exception: {str(e)}")
            
        return None
        
    async def test_get_scan_vulnerabilities(self, scan_id: str):
        """Test GET /api/scans/{scan_id}/vulnerabilities - Get vulnerabilities"""
        test_name = f"Get Scan Vulnerabilities ({scan_id[:8]}...)"
        
        try:
            # Wait for scan to complete
            await asyncio.sleep(3)
            
            async with self.session.get(f"{BACKEND_URL}/scans/{scan_id}/vulnerabilities") as response:
                if response.status == 200:
                    data = await response.json()
                    if isinstance(data, list):
                        # Store vulnerability IDs for AI triage testing
                        for vuln in data:
                            if 'id' in vuln:
                                self.vulnerability_ids.append(vuln['id'])
                        
                        self.log_result(test_name, True, f"Retrieved {len(data)} vulnerabilities")
                        return data
                    else:
                        self.log_result(test_name, False, "Response is not a list", data)
                else:
                    error_text = await response.text()
                    self.log_result(test_name, False, f"HTTP {response.status}", error_text)
                    
        except Exception as e:
            self.log_result(test_name, False, f"Exception: {str(e)}")
            
        return []
        
    async def test_ai_triage(self):
        """Test POST /api/ai/triage - AI vulnerability triage"""
        test_name = "AI Vulnerability Triage"
        
        if not self.vulnerability_ids:
            self.log_result(test_name, False, "No vulnerability IDs available for triage testing")
            return
            
        try:
            triage_data = {
                "vulnerability_ids": self.vulnerability_ids[:3],  # Test with first 3 vulnerabilities
                "context": "Production web application with high user traffic. Priority should be given to vulnerabilities that could lead to data theft or account compromise."
            }
            
            async with self.session.post(f"{BACKEND_URL}/ai/triage", json=triage_data) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'triage_analysis' in data and 'vulnerability_count' in data:
                        self.log_result(test_name, True, f"Triaged {data['vulnerability_count']} vulnerabilities")
                        return data
                    else:
                        self.log_result(test_name, False, "Response missing required fields", data)
                else:
                    error_text = await response.text()
                    self.log_result(test_name, False, f"HTTP {response.status}", error_text)
                    
        except Exception as e:
            self.log_result(test_name, False, f"Exception: {str(e)}")
            
        return None
        
    async def test_nlp_query(self):
        """Test POST /api/ai/nlp-query - Natural language queries"""
        test_name = "AI NLP Query Processing"
        
        test_queries = [
            "What vulnerabilities were found in the recent scans?",
            "How many critical XSS vulnerabilities do we have?",
            "What are the most common attack vectors discovered?",
            "Show me the security risk summary for our applications"
        ]
        
        success_count = 0
        
        for query in test_queries:
            try:
                query_data = {
                    "query": query,
                    "session_id": str(uuid.uuid4())
                }
                
                async with self.session.post(f"{BACKEND_URL}/ai/nlp-query", json=query_data) as response:
                    if response.status == 200:
                        data = await response.json()
                        if 'query' in data and 'response' in data:
                            success_count += 1
                            print(f"   ✓ Query: '{query[:50]}...' - Response received")
                        else:
                            print(f"   ✗ Query: '{query[:50]}...' - Invalid response format")
                    else:
                        error_text = await response.text()
                        print(f"   ✗ Query: '{query[:50]}...' - HTTP {response.status}")
                        
            except Exception as e:
                print(f"   ✗ Query: '{query[:50]}...' - Exception: {str(e)}")
                
        if success_count == len(test_queries):
            self.log_result(test_name, True, f"All {success_count} NLP queries processed successfully")
        elif success_count > 0:
            self.log_result(test_name, True, f"{success_count}/{len(test_queries)} NLP queries successful")
        else:
            self.log_result(test_name, False, "No NLP queries processed successfully")
            
    async def test_dashboard_stats(self):
        """Test GET /api/dashboard/stats - Dashboard statistics"""
        test_name = "Dashboard Statistics"
        
        try:
            async with self.session.get(f"{BACKEND_URL}/dashboard/stats") as response:
                if response.status == 200:
                    data = await response.json()
                    required_fields = ['total_scans', 'completed_scans', 'total_vulnerabilities', 'severity_distribution']
                    
                    if all(field in data for field in required_fields):
                        severity_dist = data['severity_distribution']
                        total_by_severity = sum([severity_dist.get(sev, 0) for sev in ['critical', 'high', 'medium', 'low']])
                        
                        self.log_result(test_name, True, 
                            f"Scans: {data['total_scans']}, Vulnerabilities: {data['total_vulnerabilities']}, "
                            f"By Severity: {total_by_severity}")
                        return data
                    else:
                        missing_fields = [field for field in required_fields if field not in data]
                        self.log_result(test_name, False, f"Missing fields: {missing_fields}", data)
                else:
                    error_text = await response.text()
                    self.log_result(test_name, False, f"HTTP {response.status}", error_text)
                    
        except Exception as e:
            self.log_result(test_name, False, f"Exception: {str(e)}")
            
        return None
        
    async def test_error_handling(self):
        """Test error handling for invalid requests"""
        test_name = "Error Handling"
        
        error_tests = [
            {
                "name": "Invalid Scan ID",
                "url": f"{BACKEND_URL}/scans/invalid-scan-id/result",
                "method": "GET",
                "expected_status": 404
            },
            {
                "name": "Missing Scan Data",
                "url": f"{BACKEND_URL}/scans",
                "method": "POST",
                "data": {},
                "expected_status": 422
            },
            {
                "name": "Invalid Vulnerability IDs",
                "url": f"{BACKEND_URL}/ai/triage",
                "method": "POST",
                "data": {"vulnerability_ids": ["invalid-id"]},
                "expected_status": 404
            }
        ]
        
        success_count = 0
        
        for test in error_tests:
            try:
                if test["method"] == "GET":
                    async with self.session.get(test["url"]) as response:
                        if response.status == test["expected_status"]:
                            success_count += 1
                            print(f"   ✓ {test['name']} - Correctly returned {response.status}")
                        else:
                            print(f"   ✗ {test['name']} - Expected {test['expected_status']}, got {response.status}")
                            
                elif test["method"] == "POST":
                    async with self.session.post(test["url"], json=test["data"]) as response:
                        if response.status == test["expected_status"]:
                            success_count += 1
                            print(f"   ✓ {test['name']} - Correctly returned {response.status}")
                        else:
                            print(f"   ✗ {test['name']} - Expected {test['expected_status']}, got {response.status}")
                            
            except Exception as e:
                print(f"   ✗ {test['name']} - Exception: {str(e)}")
                
        if success_count == len(error_tests):
            self.log_result(test_name, True, f"All {success_count} error handling tests passed")
        else:
            self.log_result(test_name, False, f"Only {success_count}/{len(error_tests)} error handling tests passed")
            
    async def run_comprehensive_tests(self):
        """Run all backend tests in sequence"""
        print("🚀 Starting Comprehensive Backend Tests for AI-Enhanced XSS Scanner Platform")
        print(f"🎯 Testing Backend URL: {BACKEND_URL}")
        print("=" * 80)
        
        await self.setup()
        
        try:
            # Test 1: Create XSS Scan
            print("\n📝 Testing XSS Scan Creation...")
            scan_id = await self.test_create_scan()
            
            # Test 2: Get All Scans
            print("\n📋 Testing Scan Retrieval...")
            await self.test_get_all_scans()
            
            # Test 3: Get Scan Results (if scan was created)
            if scan_id:
                print(f"\n📊 Testing Scan Results for {scan_id[:8]}...")
                await self.test_get_scan_result(scan_id)
                
                # Test 4: Get Vulnerabilities
                print(f"\n🔍 Testing Vulnerability Retrieval for {scan_id[:8]}...")
                await self.test_get_scan_vulnerabilities(scan_id)
            
            # Test 5: AI Triage (if vulnerabilities exist)
            print("\n🤖 Testing AI Vulnerability Triage...")
            await self.test_ai_triage()
            
            # Test 6: NLP Query Processing
            print("\n💬 Testing AI NLP Query Processing...")
            await self.test_nlp_query()
            
            # Test 7: Dashboard Statistics
            print("\n📈 Testing Dashboard Statistics...")
            await self.test_dashboard_stats()
            
            # Test 8: Error Handling
            print("\n⚠️ Testing Error Handling...")
            await self.test_error_handling()
            
        finally:
            await self.cleanup()
            
        # Print Summary
        print("\n" + "=" * 80)
        print("📋 TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if total - passed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  • {result['test']}: {result['details']}")
        
        print("\n🎯 CRITICAL BACKEND FUNCTIONALITY STATUS:")
        
        # Check critical functionality
        critical_tests = [
            "Create XSS Scan",
            "Get All Scans", 
            "Dashboard Statistics"
        ]
        
        critical_passed = sum(1 for result in self.test_results 
                            if result['test'] in critical_tests and result['success'])
        
        if critical_passed == len(critical_tests):
            print("✅ All critical backend functionality is working")
        else:
            print("❌ Some critical backend functionality is failing")
            
        return passed == total

async def main():
    """Main test execution"""
    tester = XSSScanner_BackendTester()
    success = await tester.run_comprehensive_tests()
    
    if success:
        print("\n🎉 All backend tests passed successfully!")
        return 0
    else:
        print("\n💥 Some backend tests failed!")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
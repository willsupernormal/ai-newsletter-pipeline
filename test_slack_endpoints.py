#!/usr/bin/env python3
"""
Comprehensive Slack Endpoint Testing Script
Tests all webhook endpoints to identify which ones Slack can reach
"""

import requests
import json
import sys
from datetime import datetime

# Your Railway URL
BASE_URL = "https://ai-newsletter-pipeline-production.up.railway.app"

# Test endpoints
ENDPOINTS = [
    "/health",
    "/slack/test",
    "/slack/simple", 
    "/slack/minimal",
    "/slack/challenge",
    "/slack/interactions",
    "/slack/events"
]

def test_endpoint(endpoint: str, method: str = "POST"):
    """Test a single endpoint"""
    url = f"{BASE_URL}{endpoint}"
    
    # Prepare test payload (Slack url_verification format)
    payload = {
        "type": "url_verification",
        "challenge": f"test_challenge_{datetime.now().timestamp()}"
    }
    
    print(f"\n{'='*80}")
    print(f"Testing: {method} {url}")
    print(f"{'='*80}")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        else:
            # Test with JSON
            response = requests.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
        
        print(f"✅ Status Code: {response.status_code}")
        print(f"📄 Response Headers:")
        for key, value in response.headers.items():
            print(f"   {key}: {value}")
        
        print(f"📦 Response Body:")
        try:
            response_json = response.json()
            print(f"   {json.dumps(response_json, indent=2)}")
            
            # Check if challenge was returned
            if 'challenge' in response_json:
                if response_json['challenge'] == payload['challenge']:
                    print(f"✅ Challenge correctly returned!")
                else:
                    print(f"⚠️  Challenge mismatch!")
        except:
            print(f"   {response.text[:500]}")
        
        print(f"⏱️  Response Time: {response.elapsed.total_seconds():.3f}s")
        
        return {
            "endpoint": endpoint,
            "method": method,
            "status": response.status_code,
            "success": response.status_code == 200,
            "response_time": response.elapsed.total_seconds()
        }
        
    except requests.exceptions.Timeout:
        print(f"❌ TIMEOUT - Server took too long to respond")
        return {"endpoint": endpoint, "method": method, "success": False, "error": "timeout"}
    except requests.exceptions.ConnectionError as e:
        print(f"❌ CONNECTION ERROR - Cannot reach server")
        print(f"   Error: {e}")
        return {"endpoint": endpoint, "method": method, "success": False, "error": "connection"}
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return {"endpoint": endpoint, "method": method, "success": False, "error": str(e)}


def test_form_encoded(endpoint: str):
    """Test endpoint with form-encoded data (how Slack sends button clicks)"""
    url = f"{BASE_URL}{endpoint}"
    
    print(f"\n{'='*80}")
    print(f"Testing FORM-ENCODED: POST {url}")
    print(f"{'='*80}")
    
    # Simulate Slack button click payload
    payload_data = {
        "type": "block_actions",
        "user": {"id": "U123", "username": "testuser"},
        "actions": [{
            "action_id": "add_to_pipeline",
            "value": "test-article-id"
        }]
    }
    
    form_data = {
        "payload": json.dumps(payload_data)
    }
    
    try:
        response = requests.post(
            url,
            data=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )
        
        print(f"✅ Status Code: {response.status_code}")
        print(f"📦 Response: {response.text[:500]}")
        
        return {"endpoint": endpoint, "method": "POST (form)", "success": response.status_code == 200}
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return {"endpoint": endpoint, "method": "POST (form)", "success": False, "error": str(e)}


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("🧪 SLACK ENDPOINT TESTING SUITE")
    print("="*80)
    print(f"Base URL: {BASE_URL}")
    print(f"Testing {len(ENDPOINTS)} endpoints")
    print("="*80)
    
    results = []
    
    # Test all endpoints with JSON
    for endpoint in ENDPOINTS:
        if endpoint == "/health":
            result = test_endpoint(endpoint, "GET")
        else:
            result = test_endpoint(endpoint, "POST")
        results.append(result)
    
    # Test interactions endpoint with form-encoded data
    print("\n" + "="*80)
    print("🔄 Testing Form-Encoded Payloads (Button Clicks)")
    print("="*80)
    result = test_form_encoded("/slack/interactions")
    results.append(result)
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    successful = [r for r in results if r.get('success')]
    failed = [r for r in results if not r.get('success')]
    
    print(f"\n✅ Successful: {len(successful)}/{len(results)}")
    for r in successful:
        print(f"   • {r['method']} {r['endpoint']}")
    
    if failed:
        print(f"\n❌ Failed: {len(failed)}/{len(results)}")
        for r in failed:
            error = r.get('error', 'unknown')
            print(f"   • {r['method']} {r['endpoint']} - {error}")
    
    print("\n" + "="*80)
    print("🎯 RECOMMENDATIONS FOR SLACK CONFIGURATION")
    print("="*80)
    
    # Find best endpoint
    working_endpoints = [r for r in results if r.get('success') and '/slack/' in r['endpoint']]
    
    if working_endpoints:
        print("\n✅ Working endpoints you can try in Slack:")
        for r in working_endpoints:
            print(f"\n   {BASE_URL}{r['endpoint']}")
            print(f"   - Response time: {r.get('response_time', 0):.3f}s")
            print(f"   - Status: {r.get('status', 'unknown')}")
    else:
        print("\n⚠️  No Slack endpoints are responding correctly!")
        print("   This suggests a server configuration issue.")
    
    print("\n" + "="*80)
    print("📝 NEXT STEPS")
    print("="*80)
    print("""
1. Try each working endpoint in Slack's Interactivity settings
2. Check Railway logs while saving the URL in Slack
3. If still no requests appear in logs, the issue is Slack-side
4. Consider using Slack Events API as alternative
    """)


if __name__ == "__main__":
    main()

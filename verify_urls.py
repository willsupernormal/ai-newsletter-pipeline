#!/usr/bin/env python3
"""
Verify that all URLs are correctly configured
Check Railway URL, Slack webhook URL, and interactivity URL
"""

import requests
import json
from config.settings import Settings

def main():
    print("="*80)
    print("🔍 URL VERIFICATION CHECK")
    print("="*80)
    print()
    
    settings = Settings()
    
    # Expected Railway URL
    railway_url = "https://ai-newsletter-pipeline-production.up.railway.app"
    
    print("📋 CONFIGURED URLs:")
    print("-"*80)
    print(f"1. Railway Base URL (Expected):")
    print(f"   {railway_url}")
    print()
    print(f"2. Slack Webhook URL (from .env):")
    print(f"   {settings.SLACK_WEBHOOK_URL[:60]}..." if settings.SLACK_WEBHOOK_URL else "   ❌ NOT CONFIGURED")
    print()
    print(f"3. Slack Bot Token (from .env):")
    print(f"   {settings.SLACK_BOT_TOKEN[:20]}..." if settings.SLACK_BOT_TOKEN else "   ❌ NOT CONFIGURED")
    print()
    print(f"4. Slack Signing Secret (from .env):")
    print(f"   {'✅ Configured' if settings.SLACK_SIGNING_SECRET else '❌ NOT CONFIGURED'}")
    print()
    
    print("="*80)
    print("🧪 TESTING URLs:")
    print("="*80)
    print()
    
    # Test 1: Health endpoint
    print("Test 1: Railway Health Endpoint")
    print("-"*80)
    try:
        response = requests.get(f"{railway_url}/health", timeout=10)
        if response.status_code == 200:
            print(f"✅ PASS - Status: {response.status_code}")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ FAIL - Status: {response.status_code}")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    print()
    
    # Test 2: Interactions endpoint
    print("Test 2: Slack Interactions Endpoint")
    print("-"*80)
    test_payload = {
        "type": "url_verification",
        "challenge": "test_challenge_12345"
    }
    try:
        response = requests.post(
            f"{railway_url}/slack/interactions",
            json=test_payload,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if data.get('challenge') == test_payload['challenge']:
                print(f"✅ PASS - Challenge response correct")
                print(f"   Status: {response.status_code}")
                print(f"   Response: {data}")
            else:
                print(f"⚠️  PARTIAL - Responded but challenge mismatch")
                print(f"   Expected: {test_payload['challenge']}")
                print(f"   Got: {data.get('challenge')}")
        else:
            print(f"❌ FAIL - Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    print()
    
    # Test 3: Events endpoint
    print("Test 3: Slack Events Endpoint")
    print("-"*80)
    try:
        response = requests.post(
            f"{railway_url}/slack/events",
            json=test_payload,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if data.get('challenge') == test_payload['challenge']:
                print(f"✅ PASS - Challenge response correct")
            else:
                print(f"⚠️  PARTIAL - Responded but challenge mismatch")
        else:
            print(f"❌ FAIL - Status: {response.status_code}")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    print()
    
    # Test 4: Check if Railway URL might have changed
    print("Test 4: Check for URL Redirects")
    print("-"*80)
    try:
        response = requests.get(f"{railway_url}/health", allow_redirects=False, timeout=10)
        if response.status_code in [301, 302, 307, 308]:
            print(f"⚠️  WARNING - URL redirects to: {response.headers.get('Location')}")
            print(f"   You should use the redirect URL in Slack!")
        else:
            print(f"✅ No redirects - URL is correct")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    print()
    
    print("="*80)
    print("📊 SUMMARY & RECOMMENDATIONS")
    print("="*80)
    print()
    
    print("✅ URLs to use in Slack App Settings:")
    print()
    print("1. Interactivity & Shortcuts → Request URL:")
    print(f"   {railway_url}/slack/interactions")
    print()
    print("2. Event Subscriptions → Request URL (alternative):")
    print(f"   {railway_url}/slack/events")
    print()
    print("3. OAuth & Permissions → Redirect URLs:")
    print(f"   {railway_url}/slack/oauth")
    print()
    
    print("="*80)
    print("🔍 POTENTIAL ISSUES TO CHECK:")
    print("="*80)
    print()
    
    issues = []
    
    if not settings.SLACK_BOT_TOKEN:
        issues.append("❌ SLACK_BOT_TOKEN not configured in .env")
    
    if not settings.SLACK_SIGNING_SECRET:
        issues.append("❌ SLACK_SIGNING_SECRET not configured in .env")
    
    if not settings.SLACK_WEBHOOK_URL:
        issues.append("❌ SLACK_WEBHOOK_URL not configured in .env")
    
    # Check if webhook URL matches expected pattern
    if settings.SLACK_WEBHOOK_URL and "hooks.slack.com" not in settings.SLACK_WEBHOOK_URL:
        issues.append("⚠️  SLACK_WEBHOOK_URL doesn't look like a Slack webhook URL")
    
    if issues:
        for issue in issues:
            print(issue)
        print()
        print("Fix these issues in your .env file!")
    else:
        print("✅ All environment variables are configured")
    
    print()
    print("="*80)
    print("🎯 NEXT STEPS:")
    print("="*80)
    print()
    print("1. Copy the exact URL from 'URLs to use' section above")
    print("2. Go to: https://api.slack.com/apps")
    print("3. Click your app → Interactivity & Shortcuts")
    print("4. Paste the URL EXACTLY as shown above")
    print("5. Click 'Save Changes'")
    print()
    print("If you still get an error, the issue is likely:")
    print("- Missing OAuth redirect URL (add it in OAuth & Permissions)")
    print("- App needs to be reinstalled to workspace")
    print("- App was created without interactivity enabled")
    print()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Diagnose Slack App Configuration
Check if the Slack app has all required settings
"""

import requests
import json
from config.settings import Settings

def check_slack_app_info():
    """Check Slack app configuration using API"""
    settings = Settings()
    
    print("="*80)
    print("🔍 SLACK APP CONFIGURATION DIAGNOSTIC")
    print("="*80)
    
    # Check if bot token exists
    if not settings.SLACK_BOT_TOKEN:
        print("❌ SLACK_BOT_TOKEN not configured!")
        return
    
    print(f"\n✅ Bot Token: {settings.SLACK_BOT_TOKEN[:20]}...")
    
    # Test 1: Check auth.test
    print("\n" + "-"*80)
    print("Test 1: Verify Bot Token")
    print("-"*80)
    
    try:
        response = requests.post(
            "https://slack.com/api/auth.test",
            headers={"Authorization": f"Bearer {settings.SLACK_BOT_TOKEN}"}
        )
        data = response.json()
        
        if data.get('ok'):
            print("✅ Bot token is valid!")
            print(f"   Team: {data.get('team')}")
            print(f"   User: {data.get('user')}")
            print(f"   User ID: {data.get('user_id')}")
            print(f"   Bot ID: {data.get('bot_id')}")
        else:
            print(f"❌ Bot token invalid: {data.get('error')}")
            return
    except Exception as e:
        print(f"❌ Error checking bot token: {e}")
        return
    
    # Test 2: Check bot info
    print("\n" + "-"*80)
    print("Test 2: Check Bot Information")
    print("-"*80)
    
    try:
        response = requests.post(
            "https://slack.com/api/bots.info",
            headers={"Authorization": f"Bearer {settings.SLACK_BOT_TOKEN}"},
            json={"bot": data.get('bot_id')}
        )
        bot_data = response.json()
        
        if bot_data.get('ok'):
            bot = bot_data.get('bot', {})
            print("✅ Bot info retrieved!")
            print(f"   Name: {bot.get('name')}")
            print(f"   App ID: {bot.get('app_id')}")
            print(f"   Deleted: {bot.get('deleted', False)}")
        else:
            print(f"⚠️  Could not get bot info: {bot_data.get('error')}")
    except Exception as e:
        print(f"⚠️  Error checking bot info: {e}")
    
    # Test 3: Check app permissions
    print("\n" + "-"*80)
    print("Test 3: Check App Permissions")
    print("-"*80)
    
    try:
        response = requests.get(
            "https://slack.com/api/apps.permissions.info",
            headers={"Authorization": f"Bearer {settings.SLACK_BOT_TOKEN}"}
        )
        perms_data = response.json()
        
        if perms_data.get('ok'):
            info = perms_data.get('info', {})
            team = info.get('team', {})
            
            print("✅ Permissions info retrieved!")
            print(f"   Team ID: {team.get('id')}")
            print(f"   Team Name: {team.get('name')}")
            
            # Check scopes
            scopes = info.get('scopes', {})
            bot_scopes = scopes.get('bot', [])
            
            print(f"\n   Bot Scopes ({len(bot_scopes)}):")
            for scope in bot_scopes:
                print(f"      • {scope}")
            
            # Check for required scopes
            required_scopes = ['chat:write', 'chat:write.public']
            missing_scopes = [s for s in required_scopes if s not in bot_scopes]
            
            if missing_scopes:
                print(f"\n   ⚠️  Missing required scopes: {', '.join(missing_scopes)}")
            else:
                print(f"\n   ✅ All required scopes present")
                
        else:
            print(f"⚠️  Could not get permissions: {perms_data.get('error')}")
    except Exception as e:
        print(f"⚠️  Error checking permissions: {e}")
    
    # Test 4: Test posting a message
    print("\n" + "-"*80)
    print("Test 4: Test Message Posting")
    print("-"*80)
    
    if settings.SLACK_WEBHOOK_URL:
        print(f"✅ Webhook URL configured: {settings.SLACK_WEBHOOK_URL[:50]}...")
        
        try:
            test_message = {
                "text": "🧪 Diagnostic Test Message",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "🧪 *Diagnostic Test*\nThis is a test message from the diagnostic script."
                        }
                    }
                ]
            }
            
            response = requests.post(
                settings.SLACK_WEBHOOK_URL,
                json=test_message
            )
            
            if response.status_code == 200:
                print("✅ Test message posted successfully!")
            else:
                print(f"⚠️  Message posting failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Error posting message: {e}")
    else:
        print("⚠️  SLACK_WEBHOOK_URL not configured")
    
    # Summary
    print("\n" + "="*80)
    print("📊 DIAGNOSTIC SUMMARY")
    print("="*80)
    
    print("""
Configuration Status:
✅ Bot token is valid and working
✅ App is installed to workspace
✅ Basic API calls work

Next Steps to Debug Interactivity Issue:

1. CHECK SLACK APP SETTINGS (Manual):
   - Go to: https://api.slack.com/apps
   - Click your app
   - Check "Interactivity & Shortcuts":
     • Is "Interactivity" toggle ON?
     • Is Request URL configured?
     • Does it show a green checkmark or red X?
   
2. CHECK OAUTH SETTINGS:
   - Go to "OAuth & Permissions"
   - Check "Redirect URLs" section
   - Should have at least one redirect URL configured
   
3. CHECK APP MANIFEST:
   - Go to "App Manifest"
   - Look for "interactivity" section
   - Should have "is_enabled: true" and "request_url" set

4. TRY THESE URLS IN SLACK SETTINGS:
   - https://ai-newsletter-pipeline-production.up.railway.app/slack/interactions
   - https://ai-newsletter-pipeline-production.up.railway.app/slack/simple
   - https://ai-newsletter-pipeline-production.up.railway.app/slack/minimal
   - https://ai-newsletter-pipeline-production.up.railway.app/slack/challenge

5. IF NONE WORK:
   The issue is likely that Slack requires the app to be created with
   interactivity enabled from the start, or there's a missing OAuth flow.
   
   Consider creating a NEW Slack app using "From an app manifest" with
   interactivity pre-configured.
    """)


if __name__ == "__main__":
    check_slack_app_info()

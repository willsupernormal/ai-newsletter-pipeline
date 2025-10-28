#!/usr/bin/env python3
"""
Identify which Slack app is which by checking their configuration
This will show you the differences between the old and new app
"""

import requests
import json
from datetime import datetime

def check_app(bot_token, app_name="App"):
    """Check a Slack app's configuration using its bot token"""
    
    print(f"\n{'='*80}")
    print(f"🔍 CHECKING {app_name}")
    print('='*80)
    
    # Test 1: Verify token and get basic info
    print("\n1️⃣ Basic App Information:")
    print("-"*80)
    try:
        response = requests.post(
            "https://slack.com/api/auth.test",
            headers={"Authorization": f"Bearer {bot_token}"}
        )
        data = response.json()
        
        if data.get('ok'):
            print(f"✅ Token is valid")
            print(f"   Team: {data.get('team')}")
            print(f"   Team ID: {data.get('team_id')}")
            print(f"   User: {data.get('user')}")
            print(f"   User ID: {data.get('user_id')}")
            print(f"   Bot ID: {data.get('bot_id')}")
            print(f"   App ID: {data.get('url', '').split('/')[-1] if data.get('url') else 'N/A'}")
            
            # Store for comparison
            app_info = {
                'team': data.get('team'),
                'user': data.get('user'),
                'user_id': data.get('user_id'),
                'bot_id': data.get('bot_id')
            }
        else:
            print(f"❌ Token invalid: {data.get('error')}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None
    
    # Test 2: Check bot info
    print("\n2️⃣ Bot Details:")
    print("-"*80)
    try:
        response = requests.post(
            "https://slack.com/api/bots.info",
            headers={"Authorization": f"Bearer {bot_token}"},
            json={"bot": data.get('bot_id')}
        )
        bot_data = response.json()
        
        if bot_data.get('ok'):
            bot = bot_data.get('bot', {})
            print(f"✅ Bot Name: {bot.get('name')}")
            print(f"   App ID: {bot.get('app_id')}")
            print(f"   Deleted: {bot.get('deleted', False)}")
            print(f"   Updated: {datetime.fromtimestamp(bot.get('updated', 0)).strftime('%Y-%m-%d %H:%M:%S')}")
            
            app_info['app_id'] = bot.get('app_id')
            app_info['bot_name'] = bot.get('name')
            app_info['updated'] = bot.get('updated')
        else:
            print(f"⚠️  Could not get bot info: {bot_data.get('error')}")
    except Exception as e:
        print(f"⚠️  Error: {e}")
    
    # Test 3: Check scopes
    print("\n3️⃣ OAuth Scopes:")
    print("-"*80)
    try:
        response = requests.get(
            "https://slack.com/api/apps.permissions.info",
            headers={"Authorization": f"Bearer {bot_token}"}
        )
        perms_data = response.json()
        
        if perms_data.get('ok'):
            info = perms_data.get('info', {})
            scopes = info.get('scopes', {})
            bot_scopes = scopes.get('bot', [])
            
            print(f"✅ Bot Scopes ({len(bot_scopes)}):")
            for scope in sorted(bot_scopes):
                print(f"   • {scope}")
            
            app_info['scopes'] = bot_scopes
            
            # Check for key scopes
            has_oauth = 'channels:history' in bot_scopes
            print(f"\n   OAuth-related scopes: {'✅ YES' if has_oauth else '❌ NO'}")
        else:
            print(f"⚠️  Could not get permissions: {perms_data.get('error')}")
    except Exception as e:
        print(f"⚠️  Error: {e}")
    
    return app_info


def main():
    print("="*80)
    print("🔍 SLACK APP IDENTIFIER")
    print("="*80)
    print("\nThis script will help you identify which app is which")
    print("by comparing their configurations.\n")
    
    # Get tokens
    print("Please provide the bot tokens for comparison:")
    print("(You can find them in: https://api.slack.com/apps → Your App → OAuth & Permissions)\n")
    
    token1 = input("Enter FIRST bot token (old app): ").strip()
    if not token1:
        print("❌ No token provided for first app")
        return
    
    token2 = input("Enter SECOND bot token (new app): ").strip()
    if not token2:
        print("❌ No token provided for second app")
        return
    
    # Check both apps
    app1_info = check_app(token1, "FIRST APP (Old)")
    app2_info = check_app(token2, "SECOND APP (New)")
    
    # Compare
    print("\n" + "="*80)
    print("📊 COMPARISON")
    print("="*80)
    
    if app1_info and app2_info:
        print("\n🔍 Key Differences:\n")
        
        # User ID (most reliable identifier)
        if app1_info.get('user_id') != app2_info.get('user_id'):
            print(f"✅ Different User IDs:")
            print(f"   First:  {app1_info.get('user_id')}")
            print(f"   Second: {app2_info.get('user_id')}")
        else:
            print(f"⚠️  SAME User ID: {app1_info.get('user_id')}")
        
        # Bot ID
        if app1_info.get('bot_id') != app2_info.get('bot_id'):
            print(f"\n✅ Different Bot IDs:")
            print(f"   First:  {app1_info.get('bot_id')}")
            print(f"   Second: {app2_info.get('bot_id')}")
        else:
            print(f"\n⚠️  SAME Bot ID: {app1_info.get('bot_id')}")
        
        # App ID
        if app1_info.get('app_id') != app2_info.get('app_id'):
            print(f"\n✅ Different App IDs:")
            print(f"   First:  {app1_info.get('app_id')}")
            print(f"   Second: {app2_info.get('app_id')}")
        else:
            print(f"\n⚠️  SAME App ID: {app1_info.get('app_id')}")
        
        # Scopes
        scopes1 = set(app1_info.get('scopes', []))
        scopes2 = set(app2_info.get('scopes', []))
        
        if scopes1 != scopes2:
            print(f"\n✅ Different Scopes:")
            
            only_first = scopes1 - scopes2
            if only_first:
                print(f"\n   Only in FIRST app:")
                for scope in sorted(only_first):
                    print(f"      • {scope}")
            
            only_second = scopes2 - scopes1
            if only_second:
                print(f"\n   Only in SECOND app:")
                for scope in sorted(only_second):
                    print(f"      • {scope}")
        else:
            print(f"\n⚠️  SAME Scopes")
        
        # Updated timestamp
        if app1_info.get('updated') and app2_info.get('updated'):
            time1 = datetime.fromtimestamp(app1_info.get('updated'))
            time2 = datetime.fromtimestamp(app2_info.get('updated'))
            
            print(f"\n📅 Last Updated:")
            print(f"   First:  {time1.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Second: {time2.strftime('%Y-%m-%d %H:%M:%S')}")
            
            if time2 > time1:
                print(f"\n   ✅ Second app is NEWER (created more recently)")
            else:
                print(f"\n   ⚠️  First app is newer")
    
    print("\n" + "="*80)
    print("🎯 RECOMMENDATION")
    print("="*80)
    print("\nTo identify your apps in Slack's dashboard:")
    print("1. Go to: https://api.slack.com/apps")
    print("2. Look for these identifiers:")
    print(f"   • First App - User ID: {app1_info.get('user_id') if app1_info else 'N/A'}")
    print(f"   • Second App - User ID: {app2_info.get('user_id') if app2_info else 'N/A'}")
    print("\n3. The app with the NEWER timestamp is your new app")
    print("4. Use the NEW app's token in your .env file")
    print("\n" + "="*80)


if __name__ == "__main__":
    main()

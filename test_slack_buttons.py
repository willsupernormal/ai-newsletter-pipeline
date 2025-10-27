#!/usr/bin/env python3
"""
Test different Slack button configurations
Send test messages with various button setups to isolate the issue
"""

import asyncio
import json
from config.settings import Settings
from services.slack_notifier import SlackNotifier

async def test_button_configurations():
    """Test multiple button configurations"""
    settings = Settings()
    notifier = SlackNotifier(settings)
    
    print("🧪 Testing Different Slack Button Configurations\n")
    
    # Test 1: Simple button with minimal config
    print("Test 1: Minimal Button Configuration")
    print("-" * 80)
    
    message_1 = {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Test 1: Minimal Button*\nClick this button to test basic interactivity"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "🔘 Test Minimal"
                        },
                        "action_id": "test_minimal",
                        "value": "test_1"
                    }
                ]
            }
        ]
    }
    
    try:
        await notifier.post_message(message_1)
        print("✅ Test 1 sent successfully\n")
    except Exception as e:
        print(f"❌ Test 1 failed: {e}\n")
    
    await asyncio.sleep(2)
    
    # Test 2: Button with URL (no interactivity needed)
    print("Test 2: URL Button (No Webhook)")
    print("-" * 80)
    
    message_2 = {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Test 2: URL Button*\nThis button opens a URL (no webhook needed)"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "🔗 Open URL"
                        },
                        "url": "https://ai-newsletter-pipeline-production.up.railway.app/health"
                    }
                ]
            }
        ]
    }
    
    try:
        await notifier.post_message(message_2)
        print("✅ Test 2 sent successfully\n")
    except Exception as e:
        print(f"❌ Test 2 failed: {e}\n")
    
    await asyncio.sleep(2)
    
    # Test 3: Multiple buttons with different endpoints
    print("Test 3: Multiple Buttons (Different Endpoints)")
    print("-" * 80)
    
    message_3 = {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Test 3: Multiple Endpoint Test*\nTry each button - they point to different endpoints"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "🔘 /interactions"
                        },
                        "action_id": "test_interactions",
                        "value": "endpoint_interactions"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "🔘 /simple"
                        },
                        "action_id": "test_simple",
                        "value": "endpoint_simple"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "🔘 /minimal"
                        },
                        "action_id": "test_minimal_endpoint",
                        "value": "endpoint_minimal"
                    }
                ]
            }
        ]
    }
    
    try:
        await notifier.post_message(message_3)
        print("✅ Test 3 sent successfully\n")
    except Exception as e:
        print(f"❌ Test 3 failed: {e}\n")
    
    await asyncio.sleep(2)
    
    # Test 4: Button with confirm dialog
    print("Test 4: Button with Confirmation")
    print("-" * 80)
    
    message_4 = {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Test 4: Confirmation Dialog*\nThis button shows a confirmation before triggering"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "🔘 Confirm Test"
                        },
                        "action_id": "test_confirm",
                        "value": "test_4",
                        "confirm": {
                            "title": {
                                "type": "plain_text",
                                "text": "Are you sure?"
                            },
                            "text": {
                                "type": "mrkdwn",
                                "text": "This will test the webhook endpoint"
                            },
                            "confirm": {
                                "type": "plain_text",
                                "text": "Yes, test it"
                            },
                            "deny": {
                                "type": "plain_text",
                                "text": "Cancel"
                            }
                        }
                    }
                ]
            }
        ]
    }
    
    try:
        await notifier.post_message(message_4)
        print("✅ Test 4 sent successfully\n")
    except Exception as e:
        print(f"❌ Test 4 failed: {e}\n")
    
    await asyncio.sleep(2)
    
    # Test 5: Original "Add to Pipeline" button
    print("Test 5: Original Add to Pipeline Button")
    print("-" * 80)
    
    message_5 = {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Test 5: Original Configuration*\nThis is the actual button from the digest"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "🔖 Add to Pipeline"
                        },
                        "action_id": "add_to_pipeline",
                        "value": "test-article-id-12345"
                    }
                ]
            }
        ]
    }
    
    try:
        await notifier.post_message(message_5)
        print("✅ Test 5 sent successfully\n")
    except Exception as e:
        print(f"❌ Test 5 failed: {e}\n")
    
    print("="*80)
    print("📊 All test messages sent!")
    print("="*80)
    print("""
Next Steps:
1. Check your Slack channel for the test messages
2. Try clicking each button
3. Note which ones show errors vs which work
4. Check Railway logs to see if ANY requests come through
5. Report back which buttons work and which don't

Expected Behaviors:
- Test 1: Should trigger webhook (if interactivity works)
- Test 2: Should open URL directly (no webhook needed)
- Test 3: Should trigger webhook (if interactivity works)
- Test 4: Should show confirmation, then trigger webhook
- Test 5: Should trigger webhook (original button)

If ALL buttons show the same error, the issue is app-level configuration.
If SOME buttons work, we can isolate the specific configuration issue.
    """)


if __name__ == "__main__":
    asyncio.run(test_button_configurations())

# 🧪 Comprehensive Slack Debugging Test Suite

**Created**: October 27, 2025  
**Purpose**: Systematically isolate why Slack interactivity URL verification is failing

---

## 📋 What We've Built

### **1. Multiple Test Endpoints** (`api/webhook_server.py`)

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/slack/interactions` | POST | Yes | Original endpoint with full auth |
| `/slack/simple` | GET/POST | No | Minimal with challenge handling |
| `/slack/minimal` | GET/POST | No | Absolute minimal (returns OK) |
| `/slack/challenge` | POST | No | Dedicated challenge handler |
| `/slack/test` | ALL | No | Accepts any HTTP method |
| `/slack/events` | POST | No | Events API endpoint |

**Key Differences**:
- Some have signature verification, some don't
- Different response formats
- Different HTTP method support
- This helps isolate if auth or response format is the issue

---

### **2. Test Scripts**

#### **`test_slack_endpoints.py`**
Tests all endpoints from outside the system:
- Sends url_verification challenges
- Tests both JSON and form-encoded payloads
- Measures response times
- Identifies which endpoints work

**Run**: `python3 test_slack_endpoints.py`

#### **`test_slack_buttons.py`**
Sends 5 different button configurations to Slack:
1. Minimal button (basic interactivity)
2. URL button (no webhook - should always work)
3. Multiple buttons (different endpoints)
4. Button with confirmation dialog
5. Original "Add to Pipeline" button

**Run**: `python3 test_slack_buttons.py`

**Purpose**: Determine if specific button configs work

#### **`diagnose_slack_app.py`**
Checks Slack app configuration via API:
- Verifies bot token
- Checks permissions/scopes
- Tests message posting
- Identifies missing configuration

**Run**: `python3 diagnose_slack_app.py`

---

### **3. Documentation**

#### **`docs/SLACK_DEBUGGING_GUIDE.md`**
Comprehensive 5-phase testing process:
- Phase 1: Verify server endpoints
- Phase 2: Test Slack app config
- Phase 3: Test button configurations
- Phase 4: Try each endpoint in Slack
- Phase 5: Check Railway logs

Includes decision tree and results template.

#### **`QUICK_DEBUG_STEPS.md`**
Quick reference card with:
- 6 steps to run in order
- Expected outputs
- Quick diagnosis guide
- Quick fixes to try

#### **`README_DEBUGGING.md`**
Quick start guide for the test suite.

#### **`slack_app_manifest.yaml`**
Template for recreating Slack app with correct configuration.

---

## 🎯 Testing Strategy

### **Isolation Approach**

We're testing multiple variables:

1. **Endpoint Path**: Does Slack prefer certain paths?
2. **Authentication**: Is signature verification blocking?
3. **Response Format**: Is our challenge response correct?
4. **HTTP Methods**: Does Slack need specific methods?
5. **App Configuration**: Is the app properly set up?

### **Progressive Testing**

```
Test 1: Can we reach the server? (test_slack_endpoints.py)
   ↓
Test 2: Is the Slack app configured? (diagnose_slack_app.py)
   ↓
Test 3: Do any buttons work? (test_slack_buttons.py)
   ↓
Test 4: Which URLs does Slack accept? (Manual testing)
   ↓
Test 5: Are requests reaching the server? (Railway logs)
```

---

## 🔍 What Each Test Reveals

### **If `test_slack_endpoints.py` fails**
→ Server/Railway configuration issue  
→ Not a Slack problem

### **If `diagnose_slack_app.py` fails**
→ Slack app token or permissions issue  
→ Need to fix app configuration

### **If Test 2 (URL button) fails**
→ Slack app not properly installed  
→ Need to reinstall app

### **If no requests appear in Railway logs**
→ Slack is not sending requests  
→ App configuration issue (OAuth, manifest, etc.)

### **If requests appear but fail**
→ Server responding incorrectly  
→ Code issue (response format, signature, etc.)

---

## 📊 Possible Outcomes

### **Outcome A: Everything works locally, nothing in Slack**
**Diagnosis**: Slack app missing OAuth configuration  
**Fix**: Add OAuth redirect URL, reinstall app

### **Outcome B: Some endpoints work in Slack**
**Diagnosis**: Specific endpoint configuration issue  
**Fix**: Use the working endpoint, update button configuration

### **Outcome C: Requests reach server but fail verification**
**Diagnosis**: Signature verification or response format issue  
**Fix**: Check logs, adjust response format

### **Outcome D: URL button works, interactive buttons don't**
**Diagnosis**: Interactivity not enabled in app manifest  
**Fix**: Recreate app from manifest with interactivity pre-configured

---

## 🚀 Deployment Instructions

### **1. Commit and Push**
```bash
git add .
git commit -m "Add comprehensive Slack debugging test suite"
git push origin main
```

### **2. Wait for Railway Deployment**
Check Railway dashboard for successful deployment (~2 minutes)

### **3. Run Tests in Order**
```bash
# Test 1: Server endpoints
python3 test_slack_endpoints.py

# Test 2: Slack app config
python3 diagnose_slack_app.py

# Test 3: Send test buttons
python3 test_slack_buttons.py
```

### **4. Manual Testing**
1. Go to Slack channel
2. Click each test button
3. Note which work/fail

### **5. Try URLs in Slack Settings**
For each endpoint:
- Go to Slack app settings
- Try configuring the URL
- Note exact error message
- Check Railway logs

---

## 📝 Results Template

```
=== TEST RESULTS ===

Date: [DATE]

SERVER TESTS:
- test_slack_endpoints.py: [ PASS / FAIL ]
- All endpoints reachable: [ YES / NO ]
- Response times: [ <3s / >3s ]

SLACK APP TESTS:
- diagnose_slack_app.py: [ PASS / FAIL ]
- Bot token valid: [ YES / NO ]
- Required scopes present: [ YES / NO ]

BUTTON TESTS:
- Test 1 (Minimal): [ WORKS / ERROR ]
- Test 2 (URL): [ WORKS / ERROR ]
- Test 3 (Multiple): [ WORKS / ERROR ]
- Test 4 (Confirm): [ WORKS / ERROR ]
- Test 5 (Original): [ WORKS / ERROR ]

SLACK URL TESTS:
Tried in Slack settings:
- /slack/simple: [ ERROR: "..." ]
- /slack/minimal: [ ERROR: "..." ]
- /slack/challenge: [ ERROR: "..." ]
- /slack/interactions: [ ERROR: "..." ]

RAILWAY LOGS:
- Any requests from Slack: [ YES / NO ]
- If YES, endpoint: [ENDPOINT]
- Request details: [PASTE]

CONCLUSION:
[What's the issue?]

RECOMMENDED FIX:
[What to try next?]
```

---

## 🎓 Key Insights

### **Why Multiple Endpoints?**
Different endpoints test different hypotheses:
- `/slack/simple`: No auth - tests if signature verification is blocking
- `/slack/minimal`: Absolute minimal - tests if response format is wrong
- `/slack/challenge`: Dedicated handler - tests if routing is the issue

### **Why Different Button Types?**
Different buttons test different features:
- URL button: No webhook needed - tests if app is installed
- Minimal button: Basic interactivity - tests if feature is enabled
- Multiple buttons: Different endpoints - tests which endpoint works

### **Why Check Logs?**
Logs tell us if Slack is even trying:
- No logs = Slack not sending requests (app config issue)
- Logs with errors = Server responding incorrectly (code issue)

---

## 🔧 Next Steps After Testing

### **If Issue is App Configuration**
1. Add OAuth redirect URL
2. Reinstall app to workspace
3. Try configuring interactivity again

### **If Issue is Code**
1. Check logs for exact error
2. Fix response format
3. Redeploy and test

### **If Nothing Works**
1. Recreate app from manifest
2. Or use Events API instead
3. Or use slash commands instead

---

## 📞 Support

After running all tests, provide:
1. Completed results template
2. Screenshots of Slack errors
3. Railway log excerpts
4. Slack app manifest (if available)

This will give us complete visibility into the issue!

---

**Ready to debug! 🚀**

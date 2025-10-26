# 🗂️ Airtable Complete Setup Guide - Content Pipeline

**Time Required**: 20-25 minutes  
**Difficulty**: Beginner-friendly  
**Goal**: Create your Content Pipeline base in Airtable with exact specifications

---

## 📋 **Table of Contents**

1. [Create Airtable Account](#1-create-airtable-account)
2. [Create New Base](#2-create-new-base)
3. [Configure Table Structure](#3-configure-table-structure)
4. [Create Views](#4-create-views)
5. [Get API Credentials](#5-get-api-credentials)
6. [Add to Environment](#6-add-to-environment)
7. [Test Connection](#7-test-connection)

---

## 1. Create Airtable Account

### **If You Don't Have an Account:**

1. Go to https://airtable.com
2. Click **"Sign up for free"**
3. Enter your email and create password
4. Verify your email address
5. Choose **"Free"** plan (sufficient for this project)

### **If You Have an Account:**

1. Go to https://airtable.com
2. Click **"Sign in"**
3. Log in with your credentials

---

## 2. Create New Base

1. From your Airtable home page, click **"Create a base"** or **"+"** button
2. Select **"Start from scratch"**
3. **Base Name**: Type exactly: `Content Pipeline`
4. Click **"Create base"**

You should now see an empty base with one table called "Table 1"

---

## 3. Configure Table Structure

### **Step 3.1: Rename the Table**

1. Click on **"Table 1"** at the top left
2. Select **"Rename table"**
3. Type: `Content Pipeline`
4. Press Enter

### **Step 3.2: Delete Default Fields**

Airtable creates some default fields. Let's start fresh:

1. You'll see fields like "Name", "Notes", "Attachments", etc.
2. **Keep the first field** (we'll rename it to "Title")
3. **Delete all other fields**:
   - Hover over field name
   - Click the dropdown arrow
   - Select "Delete field"
   - Confirm deletion

### **Step 3.3: Rename First Field to "Title"**

1. Click on the first field name (probably "Name")
2. Select "Customize field type"
3. Change **Field name** to: `Title`
4. **Field type**: Single line text
5. Click **"Save"**

### **Step 3.4: Add All Required Fields**

Now we'll add each field one by one. Click the **"+"** button to the right of the last column to add each field.

---

#### **Field 1: Title** (Already created)
- **Field name**: `Title`
- **Field type**: Single line text
- **Description**: Article title

---

#### **Field 2: Stage**
1. Click **"+"** to add field
2. **Field name**: `Stage`
3. **Field type**: Single select
4. Click **"Add option"** and add these options **exactly**:
   - `📥 Saved`
   - `🔍 Research`
   - `✍️ Writing`
   - `📋 Ready`
   - `📤 Published`
5. **Default value**: Select `📥 Saved`
6. Click **"Create field"**

---

#### **Field 3: Original URL**
1. Click **"+"**
2. **Field name**: `Original URL`
3. **Field type**: URL
4. Click **"Create field"**

---

#### **Field 4: Source**
1. Click **"+"**
2. **Field name**: `Source`
3. **Field type**: Single select
4. Add these options:
   - `VentureBeat`
   - `MIT Technology Review`
   - `AI Business`
   - `TechCrunch`
   - `The Register`
   - `Analytics India Magazine`
   - `Harvard Business Review`
   - `The Batch (Andrew Ng)`
   - `Other`
5. Click **"Create field"**

---

#### **Field 5: Digest Date**
1. Click **"+"**
2. **Field name**: `Digest Date`
3. **Field type**: Date
4. **Date format**: Local (2024/01/15)
5. **Include time**: No (uncheck)
6. Click **"Create field"**

---

#### **Field 6: Theme**
1. Click **"+"**
2. **Field name**: `Theme`
3. **Field type**: Single select
4. Add these options:
   - `AI Governance`
   - `Vendor Lock-in`
   - `Data Strategy`
   - `Enterprise Adoption`
   - `Model Performance`
   - `Regulatory Compliance`
   - `Technical Innovation`
   - `Business Strategy`
   - `Ethics & Safety`
   - `Market Trends`
5. Click **"Create field"**

---

#### **Field 7: Content Type**
1. Click **"+"**
2. **Field name**: `Content Type`
3. **Field type**: Single select
4. Add these options:
   - `News`
   - `Research`
   - `Opinion`
   - `Analysis`
   - `Case Study`
   - `Tutorial`
5. Click **"Create field"**

---

#### **Field 8: Priority**
1. Click **"+"**
2. **Field name**: `Priority`
3. **Field type**: Single select
4. Add these options:
   - `🔴 High`
   - `🟡 Medium`
   - `🟢 Low`
5. **Default value**: `🟡 Medium`
6. Click **"Create field"**

---

#### **Field 9: AI Summary Short**
1. Click **"+"**
2. **Field name**: `AI Summary Short`
3. **Field type**: Long text
4. **Enable rich text formatting**: No (leave unchecked)
5. Click **"Create field"**

---

#### **Field 10: AI Summary Full**
1. Click **"+"**
2. **Field name**: `AI Summary Full`
3. **Field type**: Long text
4. **Enable rich text formatting**: No
5. Click **"Create field"**

---

#### **Field 11: Key Metrics**
1. Click **"+"**
2. **Field name**: `Key Metrics`
3. **Field type**: Long text
4. **Enable rich text formatting**: No
5. Click **"Create field"**

---

#### **Field 12: Key Quotes**
1. Click **"+"**
2. **Field name**: `Key Quotes`
3. **Field type**: Long text
4. **Enable rich text formatting**: No
5. Click **"Create field"**

---

#### **Field 13: Why It Matters**
1. Click **"+"**
2. **Field name**: `Why It Matters`
3. **Field type**: Long text
4. **Enable rich text formatting**: No
5. Click **"Create field"**

---

#### **Field 14: Full Article Text**
1. Click **"+"**
2. **Field name**: `Full Article Text`
3. **Field type**: Long text
4. **Enable rich text formatting**: No
5. Click **"Create field"**

---

#### **Field 15: Word Count**
1. Click **"+"**
2. **Field name**: `Word Count`
3. **Field type**: Number
4. **Number format**: Integer (1,000)
5. **Precision**: 0 decimal places
6. Click **"Create field"**

---

#### **Field 16: Author**
1. Click **"+"**
2. **Field name**: `Author`
3. **Field type**: Single line text
4. Click **"Create field"**

---

#### **Field 17: Additional Research**
1. Click **"+"**
2. **Field name**: `Additional Research`
3. **Field type**: Long text
4. **Enable rich text formatting**: Yes (check this box)
5. Click **"Create field"**

---

#### **Field 18: Your Angle**
1. Click **"+"**
2. **Field name**: `Your Angle`
3. **Field type**: Long text
4. **Enable rich text formatting**: Yes
5. Click **"Create field"**

---

#### **Field 19: Draft Content**
1. Click **"+"**
2. **Field name**: `Draft Content`
3. **Field type**: Long text
4. **Enable rich text formatting**: Yes
5. Click **"Create field"**

---

#### **Field 20: Target Platform**
1. Click **"+"**
2. **Field name**: `Target Platform`
3. **Field type**: Single select
4. Add these options:
   - `LinkedIn`
   - `Blog`
   - `Newsletter`
   - `Twitter Thread`
   - `Medium`
   - `YouTube Script`
   - `Podcast Notes`
5. Click **"Create field"**

---

#### **Field 21: Tags**
1. Click **"+"**
2. **Field name**: `Tags`
3. **Field type**: Multiple select
4. Add these initial options (you can add more later):
   - `vendor-agnostic`
   - `case-study`
   - `technical`
   - `strategic`
   - `actionable`
   - `research-heavy`
   - `opinion-piece`
   - `data-driven`
5. Click **"Create field"**

---

#### **Field 22: My Notes**
1. Click **"+"**
2. **Field name**: `My Notes`
3. **Field type**: Long text
4. **Enable rich text formatting**: Yes
5. Click **"Create field"**

---

#### **Field 23: Status Notes**
1. Click **"+"**
2. **Field name**: `Status Notes`
3. **Field type**: Long text
4. **Enable rich text formatting**: Yes
5. Click **"Create field"**

---

#### **Field 24: Supabase ID**
1. Click **"+"**
2. **Field name**: `Supabase ID`
3. **Field type**: Single line text
4. **Description**: "UUID from Supabase database for linking"
5. Click **"Create field"**

---

### **Step 3.5: Verify All Fields**

You should now have **24 fields** in this exact order:

1. Title
2. Stage
3. Original URL
4. Source
5. Digest Date
6. Theme
7. Content Type
8. Priority
9. AI Summary Short
10. AI Summary Full
11. Key Metrics
12. Key Quotes
13. Why It Matters
14. Full Article Text
15. Word Count
16. Author
17. Additional Research
18. Your Angle
19. Draft Content
20. Target Platform
21. Tags
22. My Notes
23. Status Notes
24. Supabase ID

---

## 4. Create Views

Views help you organize and filter your content. Let's create 6 essential views.

### **View 1: Pipeline (Kanban) - Default View**

1. At the top left, click on **"Grid view"** dropdown
2. Select **"Kanban"**
3. In the dialog:
   - **Stack by**: Select `Stage`
   - **Card fields**: Select these to show on cards:
     - Title
     - Source
     - Priority
     - Theme
4. Click **"Create view"**
5. Rename the view:
   - Click on "Kanban" at the top
   - Rename to: `📊 Pipeline`
   - Press Enter

This is your main working view - you'll drag cards between stages here.

---

### **View 2: Saved Articles**

1. Click the view dropdown (where it says "📊 Pipeline")
2. Click **"Create"** → **"Grid"**
3. Name it: `📥 Saved`
4. Click **"Create view"**
5. Add filter:
   - Click **"Filter"** button
   - Click **"Add filter"**
   - **Where**: `Stage`
   - **is**: `📥 Saved`
6. Add sort:
   - Click **"Sort"** button
   - Click **"Add sort"**
   - **Sort by**: `Digest Date`
   - **Order**: `Z → A` (newest first)
7. Click **"Done"**

---

### **View 3: High Priority**

1. Click view dropdown
2. Click **"Create"** → **"Grid"**
3. Name it: `🔴 High Priority`
4. Click **"Create view"**
5. Add filter:
   - Click **"Filter"**
   - **Where**: `Priority`
   - **is**: `🔴 High`
6. Add sort:
   - **Sort by**: `Digest Date`
   - **Order**: `Z → A`
7. Click **"Done"**

---

### **View 4: By Theme**

1. Click view dropdown
2. Click **"Create"** → **"Grid"**
3. Name it: `🏷️ By Theme`
4. Click **"Create view"**
5. Add grouping:
   - Click **"Group"** button
   - **Group by**: `Theme`
6. Add sort:
   - **Sort by**: `Digest Date`
   - **Order**: `Z → A`
7. Click **"Done"**

---

### **View 5: This Week**

1. Click view dropdown
2. Click **"Create"** → **"Grid"**
3. Name it: `📅 This Week`
4. Click **"Create view"**
5. Add filter:
   - Click **"Filter"**
   - **Where**: `Digest Date`
   - **is within**: `this week`
6. Add sort:
   - **Sort by**: `Priority` (High first)
   - Then **Digest Date** (newest first)
7. Click **"Done"**

---

### **View 6: Need Action**

1. Click view dropdown
2. Click **"Create"** → **"Grid"**
3. Name it: `🎯 Need Action`
4. Click **"Create view"**
5. Add filters:
   - Click **"Filter"**
   - **Where**: `Stage`
   - **is not**: `📤 Published`
   - Click **"Add filter"**
   - **Where**: `Priority`
   - **is**: `🔴 High`
6. Add sort:
   - **Sort by**: `Digest Date`
   - **Order**: `Z → A`
7. Click **"Done"**

---

### **Step 4.1: Set Default View**

1. Switch to **"📊 Pipeline"** view (the Kanban)
2. This should be your default view when you open the base

---

## 5. Get API Credentials

Now we need to get your API key and Base ID to connect the pipeline.

### **Step 5.1: Get Personal Access Token (API Key)**

1. Click your **profile icon** in the top right corner
2. Select **"Developer hub"**
3. Click **"Personal access tokens"** in the left sidebar
4. Click **"Create token"** button
5. **Token name**: `AI Digest Pipeline`
6. **Scopes**: Add these scopes:
   - `data.records:read`
   - `data.records:write`
   - `schema.bases:read`
7. **Access**: Click **"Add a base"**
   - Find and select **"Content Pipeline"**
8. Click **"Create token"**
9. **IMPORTANT**: Copy the token immediately
   - It starts with `pat...`
   - Example: `patAbCdEfGhIjKlMnOpQrStUvWxYz1234567890`
   - **Save it somewhere safe** - you won't see it again!

---

### **Step 5.2: Get Base ID**

1. Go back to your **Content Pipeline** base
2. Look at the URL in your browser
3. The URL looks like: `https://airtable.com/appXXXXXXXXXXXXXX/...`
4. Copy the part that starts with `app`
   - Example: `appABCDEFGHIJKLMN`
   - This is your **Base ID**

---

### **Step 5.3: Get Table Name**

The table name is: `Content Pipeline`

(This should match exactly what you named your table in Step 3.1)

---

## 6. Add to Environment

Now add your Airtable credentials to your `.env` file.

### **Step 6.1: Open .env File**

1. In your project folder: `/Users/will.bainbridge/CascadeProjects/ai-newsletter-pipeline copy/`
2. Open the `.env` file in a text editor

### **Step 6.2: Find Airtable Section**

Scroll to the bottom where you should see:

```bash
# Airtable Configuration (Phase 2 - Content Pipeline)
AIRTABLE_API_KEY=your-airtable-api-key-here
AIRTABLE_BASE_ID=your-airtable-base-id-here
AIRTABLE_TABLE_NAME=Content Pipeline
```

### **Step 6.3: Replace Placeholders**

Replace the placeholder values with your actual credentials:

```bash
# Airtable Configuration (Phase 2 - Content Pipeline)
AIRTABLE_API_KEY=patAbCdEfGhIjKlMnOpQrStUvWxYz1234567890  # Your actual token
AIRTABLE_BASE_ID=appABCDEFGHIJKLMN  # Your actual base ID
AIRTABLE_TABLE_NAME=Content Pipeline  # Keep this as-is
```

### **Step 6.4: Save File**

Save the `.env` file.

---

## 7. Test Connection

Let's verify everything is set up correctly.

### **Step 7.1: Create Test Script**

Create a file: `test_airtable.py` in your project root:

```python
import asyncio
from config.settings import Settings
from services.airtable_client import AirtableClient

async def test_airtable():
    """Test Airtable connection"""
    print("Testing Airtable connection...")
    
    try:
        settings = Settings()
        client = AirtableClient(settings)
        
        # Try to get recent articles (should be empty)
        articles = client.get_recent_articles(limit=5)
        print(f"✅ Connected successfully!")
        print(f"📊 Found {len(articles)} existing articles")
        
        # Try to create a test record
        test_article = {
            'title': 'Test Article - DELETE ME',
            'url': 'https://example.com/test',
            'source_name': 'VentureBeat',
            'stage': '📥 Saved',
            'priority': '🟡 Medium',
            'ai_summary_short': 'This is a test article to verify Airtable integration.',
            'supabase_id': 'test-123'
        }
        
        record_id = client.create_article_record(test_article)
        
        if record_id:
            print(f"✅ Test record created: {record_id}")
            print(f"🔗 Check your Airtable base - you should see 'Test Article - DELETE ME'")
            print(f"   You can delete it manually from Airtable")
        else:
            print("❌ Failed to create test record")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check your AIRTABLE_API_KEY in .env")
        print("2. Check your AIRTABLE_BASE_ID in .env")
        print("3. Verify table name is exactly 'Content Pipeline'")
        print("4. Ensure all required fields exist in Airtable")

if __name__ == "__main__":
    asyncio.run(test_airtable())
```

### **Step 7.2: Run Test**

```bash
python test_airtable.py
```

### **Step 7.3: Verify Results**

You should see:
```
Testing Airtable connection...
✅ Connected successfully!
📊 Found 0 existing articles
✅ Test record created: recXXXXXXXXXXXXXX
🔗 Check your Airtable base - you should see 'Test Article - DELETE ME'
   You can delete it manually from Airtable
```

### **Step 7.4: Check Airtable**

1. Go to your Airtable base
2. You should see a new record: "Test Article - DELETE ME"
3. Verify it has:
   - Title: "Test Article - DELETE ME"
   - Original URL: https://example.com/test
   - Source: VentureBeat
   - Stage: 📥 Saved
   - Priority: 🟡 Medium
4. **Delete this test record** (hover over row number, click "..." → "Delete record")

---

## ✅ **Verification Checklist**

Before proceeding, verify:

- [ ] Airtable base named "Content Pipeline" exists
- [ ] Table named "Content Pipeline" exists
- [ ] All 24 fields created with correct names and types
- [ ] 6 views created (Pipeline, Saved, High Priority, By Theme, This Week, Need Action)
- [ ] Pipeline view is Kanban grouped by Stage
- [ ] Personal Access Token obtained (starts with `pat...`)
- [ ] Base ID obtained (starts with `app...`)
- [ ] Credentials added to `.env` file
- [ ] Test script runs successfully
- [ ] Test record appears in Airtable
- [ ] Test record deleted

---

## 🎯 **Next Steps**

Once you've completed this setup:

1. ✅ Airtable is ready
2. ✅ API connection verified
3. ✅ Ready for webhook integration

**Let me know when you're done, and I'll continue with the webhook handler!**

---

## 🆘 **Troubleshooting**

### **Problem: Can't find Personal Access Tokens**

- Make sure you're on a paid plan or have access to API features
- Try going directly to: https://airtable.com/create/tokens

### **Problem: Test script fails with "Invalid API key"**

- Double-check you copied the entire token (starts with `pat...`)
- Make sure there are no extra spaces in `.env` file
- Token should be on the same line as `AIRTABLE_API_KEY=`

### **Problem: Test script fails with "Base not found"**

- Verify Base ID starts with `app`
- Check you gave the token access to this specific base
- Try recreating the token with correct base access

### **Problem: Test script fails with "Table not found"**

- Verify table name is exactly `Content Pipeline` (case-sensitive)
- Check `AIRTABLE_TABLE_NAME` in `.env` matches exactly

### **Problem: Test record created but missing fields**

- Some fields might not be required
- This is okay - the webhook will populate all fields
- Just verify the record appears

---

## 📞 **Need Help?**

If you encounter any issues:

1. Check the error message carefully
2. Verify each step was completed exactly as written
3. Double-check credentials in `.env` file
4. Try the test script again
5. Let me know the specific error and I'll help debug

---

**Estimated Time**: 20-25 minutes  
**Difficulty**: ⭐⭐☆☆☆ (Easy with this guide)

**Good luck! 🚀**

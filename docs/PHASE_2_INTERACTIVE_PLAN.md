# 📋 Phase 2: Interactive Content Management - Implementation Plan

**Status**: Planning  
**Goal**: Enable interactive content curation from Slack to Airtable  
**Timeline**: 2-3 days implementation

---

## 🎯 **Objective**

Transform the daily digest from **passive consumption** to **active curation** by:
1. Adding interactive buttons to Slack messages
2. Capturing user intent (save, analyze, dismiss)
3. Storing curated content in Airtable for organization
4. Maintaining centralized, searchable knowledge base

---

## 🏗️ **Architecture**

### **Components:**

```
┌─────────────────────────────────────────────────────────────┐
│                     SLACK DIGEST                            │
│  Article 1: [Title]                                         │
│  Summary, Metrics, Quotes...                                │
│  [🔖 Save to Airtable] [📝 Deep Analysis] [🗑️ Not Relevant]│
└─────────────────────────────────────────────────────────────┘
                            ↓
                    (User clicks button)
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              WEBHOOK HANDLER (New Service)                  │
│  - Receives Slack interaction payload                       │
│  - Validates request                                        │
│  - Routes to appropriate handler                            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   SUPABASE DATABASE                         │
│  - Fetch full article context                               │
│  - Get enriched data (metrics, quotes, etc.)                │
│  - Optionally trigger deeper analysis                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   AIRTABLE "CONTENT" BASE                   │
│  - Store article with full context                          │
│  - Organize by theme, priority, status                      │
│  - Enable search, filter, action tracking                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 **Airtable Base Design**

### **Base Name**: `Content`

### **Table 1: Articles** (Main table)

| Field Name | Field Type | Options/Description |
|------------|-----------|---------------------|
| `Title` | Single line text | Article title |
| `URL` | URL | Link to original article |
| `Source` | Single select | VentureBeat, MIT Tech Review, AI Business, etc. |
| `Date Saved` | Date | Auto-populated when saved |
| `Digest Date` | Date | Which daily digest it came from |
| `Theme` | Single select | AI Governance, Vendor Lock-in, Data Strategy, Enterprise Adoption, Model Performance, Regulatory Compliance |
| `Content Type` | Single select | News, Research, Opinion, Analysis |
| `AI Summary Short` | Long text | 500-char summary (from Slack) |
| `AI Summary Full` | Long text | Comprehensive 300-500 word summary |
| `Key Metrics` | Long text | Formatted list of metrics with context |
| `Key Quotes` | Long text | Formatted quotes with attribution |
| `Why It Matters` | Long text | Strategic implications |
| `Status` | Single select | 📥 To Read, 📖 Reading, ✅ Read, 🎯 Actioned, 📦 Archived |
| `Priority` | Single select | 🔴 High, 🟡 Medium, 🟢 Low |
| `Tags` | Multiple select | Custom tags (vendor-agnostic, case-study, technical, strategic, etc.) |
| `My Notes` | Long text | Personal notes and thoughts |
| `Action Items` | Long text | Extracted or manual action items |
| `Related Articles` | Link to another record | Link to related articles in this table |
| `Supabase ID` | Single line text | UUID for linking back to database |
| `Created By` | Created by | Auto-populated |
| `Last Modified` | Last modified time | Auto-populated |

### **Table 2: Deep Analysis** (For "Get Full Analysis" button)

| Field Name | Field Type | Options/Description |
|------------|-----------|---------------------|
| `Article` | Link to another record | Links to Articles table |
| `Analysis Type` | Single select | Competitive Analysis, Technical Deep Dive, Strategic Implications, Market Impact |
| `Full Analysis` | Long text | AI-generated comprehensive analysis |
| `Key Findings` | Long text | Bullet points of main findings |
| `Action Items` | Long text | Specific actions to take |
| `Related Trends` | Long text | Connected market trends |
| `Competitive Landscape` | Long text | How this affects competition |
| `Risk Assessment` | Long text | Potential risks and mitigations |
| `Opportunities` | Long text | Business opportunities identified |
| `Created Date` | Created time | When analysis was generated |
| `Status` | Single select | 📝 Draft, ✅ Complete, 📤 Shared |

### **Table 3: Action Items** (Optional - for task tracking)

| Field Name | Field Type | Options/Description |
|------------|-----------|---------------------|
| `Action` | Single line text | What needs to be done |
| `Article` | Link to another record | Source article |
| `Analysis` | Link to another record | Source analysis (if applicable) |
| `Status` | Single select | 📋 Todo, 🔄 In Progress, ✅ Done, ❌ Cancelled |
| `Priority` | Single select | 🔴 High, 🟡 Medium, 🟢 Low |
| `Due Date` | Date | When to complete |
| `Assigned To` | Collaborator | Who's responsible |
| `Notes` | Long text | Additional context |
| `Created Date` | Created time | Auto-populated |

### **Views (for Articles table):**
- **📥 To Read** - Filter: Status = "To Read", Sort: Priority (High first)
- **🔴 High Priority** - Filter: Priority = "High", Sort: Date Saved (newest first)
- **🏷️ By Theme** - Group by: Theme, Sort: Date Saved
- **📅 This Week** - Filter: Date Saved is within "this week"
- **🎯 Need Action** - Filter: Action Items is not empty AND Status ≠ "Actioned"
- **🔍 All Articles** - Default view, all records

---

## 🔧 **Technical Components to Build**

### **1. Slack Interactive Message Updates**

**File**: `services/slack_notifier.py`

**Changes**:
- Add action buttons to each article block
- Include article metadata in button payload (article_id, url, title)
- Use Slack Block Kit's button elements

**Example Button Block**:
```python
{
    "type": "actions",
    "block_id": f"article_{article_id}",
    "elements": [
        {
            "type": "button",
            "text": {"type": "plain_text", "text": "🔖 Save to Airtable"},
            "style": "primary",
            "value": json.dumps({"article_id": article_id, "action": "save"}),
            "action_id": "save_to_airtable"
        },
        {
            "type": "button",
            "text": {"type": "plain_text", "text": "📝 Deep Analysis"},
            "value": json.dumps({"article_id": article_id, "action": "analyze"}),
            "action_id": "deep_analysis"
        },
        {
            "type": "button",
            "text": {"type": "plain_text", "text": "🗑️ Not Relevant"},
            "style": "danger",
            "value": json.dumps({"article_id": article_id, "action": "dismiss"}),
            "action_id": "dismiss_article"
        }
    ]
}
```

### **2. Webhook Handler Service**

**New File**: `services/slack_webhook_handler.py`

**Purpose**: 
- Receive Slack interaction payloads
- Validate Slack signature
- Route to appropriate handler based on action_id
- Return immediate response to Slack (within 3 seconds)
- Queue background processing for heavy operations

**Key Functions**:
```python
class SlackWebhookHandler:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.supabase = SimpleSupabaseClient(settings)
        self.airtable = AirtableClient(settings)
        
    async def handle_interaction(self, payload: dict) -> dict:
        """Main handler for Slack interactions"""
        
    async def save_to_airtable(self, article_id: str, user_id: str) -> bool:
        """Fetch article from Supabase and push to Airtable"""
        
    async def trigger_deep_analysis(self, article_id: str, user_id: str) -> bool:
        """Generate deeper AI analysis and save to Airtable"""
        
    async def dismiss_article(self, article_id: str, user_id: str) -> bool:
        """Mark article as not relevant (for learning preferences)"""
```

### **3. Airtable Integration Service**

**New File**: `services/airtable_client.py`

**Purpose**:
- Connect to Airtable API
- Create/update records in Articles table
- Create records in Deep Analysis table
- Handle rate limiting and retries

**Key Functions**:
```python
class AirtableClient:
    def __init__(self, settings: Settings):
        self.api_key = settings.AIRTABLE_API_KEY
        self.base_id = settings.AIRTABLE_BASE_ID
        self.articles_table = "Articles"
        self.analysis_table = "Deep Analysis"
        
    async def create_article_record(self, article_data: dict) -> str:
        """Create new article record in Airtable"""
        
    async def create_analysis_record(self, analysis_data: dict) -> str:
        """Create new deep analysis record in Airtable"""
        
    async def update_article_record(self, record_id: str, updates: dict) -> bool:
        """Update existing article record"""
        
    async def search_article_by_url(self, url: str) -> Optional[dict]:
        """Check if article already exists in Airtable"""
```

### **4. Deep Analysis Generator**

**New File**: `processors/deep_analyzer.py`

**Purpose**:
- Generate comprehensive AI analysis on demand
- Extract action items, competitive insights, strategic implications
- Store results in both Supabase and Airtable

**Key Functions**:
```python
class DeepAnalyzer:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.prompt_service = get_prompt_service(settings)
        
    async def generate_deep_analysis(self, article: dict, analysis_type: str = "comprehensive") -> dict:
        """Generate comprehensive AI analysis of article"""
        
    async def extract_action_items(self, article: dict, analysis: str) -> List[str]:
        """Extract specific action items from article and analysis"""
        
    async def identify_competitive_landscape(self, article: dict) -> dict:
        """Analyze competitive implications"""
```

### **5. API Endpoint (Flask/FastAPI)**

**New File**: `api/webhook_server.py`

**Purpose**:
- Expose webhook endpoint for Slack
- Handle authentication and validation
- Route requests to handler
- Deploy on a service (Railway, Render, or Vercel)

**Example (FastAPI)**:
```python
from fastapi import FastAPI, Request, HTTPException
from services.slack_webhook_handler import SlackWebhookHandler

app = FastAPI()
handler = SlackWebhookHandler(Settings())

@app.post("/slack/interactions")
async def slack_interactions(request: Request):
    """Handle Slack interactive message callbacks"""
    
    # Verify Slack signature
    if not verify_slack_signature(request):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Parse payload
    payload = await request.json()
    
    # Handle interaction
    response = await handler.handle_interaction(payload)
    
    return response

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
```

---

## 🔐 **Configuration Requirements**

### **New Environment Variables**:

```bash
# Airtable Configuration
AIRTABLE_API_KEY=keyXXXXXXXXXXXXXX
AIRTABLE_BASE_ID=appXXXXXXXXXXXXXX
AIRTABLE_ARTICLES_TABLE=Articles
AIRTABLE_ANALYSIS_TABLE=Deep Analysis

# Slack App Configuration (for interactive messages)
SLACK_SIGNING_SECRET=xxxxxxxxxxxxxxxxxxxxx
SLACK_BOT_TOKEN=xoxb-xxxxxxxxxxxxx

# Webhook Server
WEBHOOK_SERVER_URL=https://your-app.railway.app
WEBHOOK_PORT=8000
```

### **Slack App Setup**:
1. Enable **Interactivity** in Slack App settings
2. Set **Request URL** to: `https://your-app.railway.app/slack/interactions`
3. Add **Bot Token Scopes**: `chat:write`, `commands`
4. Install app to workspace

---

## 📈 **Implementation Phases**

### **Phase 2.1: Airtable Setup** (Day 1 - 2 hours)
- [ ] Create Airtable "Content" base
- [ ] Design Articles table with all fields
- [ ] Create views (To Read, High Priority, By Theme, etc.)
- [ ] Set up API access and get credentials
- [ ] Test manual record creation

### **Phase 2.2: Slack Interactive Messages** (Day 1 - 3 hours)
- [ ] Update `slack_notifier.py` to add buttons
- [ ] Test button rendering in Slack
- [ ] Verify payload structure
- [ ] Document button behavior

### **Phase 2.3: Airtable Integration** (Day 1-2 - 4 hours)
- [ ] Create `airtable_client.py`
- [ ] Implement create/update/search methods
- [ ] Add error handling and retries
- [ ] Test with sample data
- [ ] Verify data appears correctly in Airtable

### **Phase 2.4: Webhook Handler** (Day 2 - 4 hours)
- [ ] Create `slack_webhook_handler.py`
- [ ] Implement interaction routing
- [ ] Add Slack signature verification
- [ ] Implement save_to_airtable handler
- [ ] Test locally with ngrok

### **Phase 2.5: API Deployment** (Day 2 - 3 hours)
- [ ] Create FastAPI webhook server
- [ ] Deploy to Railway/Render
- [ ] Configure Slack app with webhook URL
- [ ] Test end-to-end flow
- [ ] Monitor logs and errors

### **Phase 2.6: Deep Analysis (Optional)** (Day 3 - 4 hours)
- [ ] Create `deep_analyzer.py`
- [ ] Design deep analysis prompt
- [ ] Implement analysis generation
- [ ] Add to webhook handler
- [ ] Test with real articles

---

## 🧪 **Testing Strategy**

### **Unit Tests**:
- Airtable client methods
- Webhook handler routing
- Slack signature verification
- Data transformation functions

### **Integration Tests**:
- Slack → Webhook → Airtable flow
- Article fetch from Supabase
- Deep analysis generation
- Error handling and retries

### **Manual Tests**:
- Click "Save to Airtable" in Slack
- Verify article appears in Airtable
- Check all fields populated correctly
- Test "Deep Analysis" button
- Verify analysis appears in Airtable

---

## 💰 **Cost Estimate**

### **New Costs**:
- **Airtable**: Free tier (1,200 records) or $20/month (Pro)
- **Webhook Server**: Free tier (Railway/Render) or $5/month
- **Deep Analysis**: ~$0.05 per analysis (optional, on-demand)

### **Total Additional Cost**: $0-25/month

---

## 🎯 **Success Metrics**

- [ ] Buttons appear on all articles in Slack
- [ ] Clicking "Save" creates record in Airtable within 5 seconds
- [ ] All article context (metrics, quotes, etc.) preserved
- [ ] Airtable base is organized and searchable
- [ ] No duplicate articles created
- [ ] Error rate < 1%
- [ ] User can find saved articles easily

---

## 🚀 **Next Steps**

1. **Review this plan** - Confirm architecture and Airtable structure
2. **Set up Airtable** - Create base and tables
3. **Start implementation** - Begin with Phase 2.1
4. **Iterate based on feedback** - Adjust as needed

---

## 📝 **Notes & Considerations**

### **MVP Scope**:
- Focus on "Save to Airtable" button first
- Deep Analysis can be Phase 2.7 (later)
- Start with Articles table only
- Add Deep Analysis table later if needed

### **Future Enhancements**:
- Smart tagging based on content
- Automatic action item extraction
- Weekly summary of saved articles
- Integration with other tools (Notion, etc.)
- Collaborative features (team sharing)

---

**Status**: Ready for review and implementation

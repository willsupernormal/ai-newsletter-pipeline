# 🚀 Enhanced Context Implementation Plan

**Approved Specifications**: October 23, 2025  
**Phase**: Phase 1 - Enhanced Context in Slack  
**Timeline**: 1-2 days  
**Status**: Ready to implement

---

## ✅ **Approved Specifications**

### **Content Storage:**
- ✅ **Comprehensive AI summary** (not full article text)
- ✅ **500-character summaries** for Slack
- ✅ **2-3 key metrics** per article (any type)
- ✅ **1-2 key quotes** per article
- ✅ **"Why this matters"** strategic statement
- ✅ **Link to original** for full article access

### **Slack Format:**
- ✅ **Option A** - Full context in message
- ✅ Show: Summary, Metrics, Quote, Why This Matters, Link

### **Future (Phase 2):**
- ⏸️ "Analyze More" button
- ⏸️ On-demand full article scraping & deep analysis
- ⏸️ Interactive Slack features

---

## 📊 **Database Changes**

### **SQL Migration Script**

```sql
-- Enhanced Context Migration
-- Adds columns for richer article context

BEGIN;

-- Add new columns to articles table
ALTER TABLE articles 
ADD COLUMN IF NOT EXISTS ai_summary TEXT,                    -- Comprehensive AI summary (300-500 words)
ADD COLUMN IF NOT EXISTS ai_summary_short TEXT,              -- Brief summary for Slack (500 chars)
ADD COLUMN IF NOT EXISTS key_quotes JSONB,                   -- Array of quote objects
ADD COLUMN IF NOT EXISTS key_metrics JSONB,                  -- Array of metric objects
ADD COLUMN IF NOT EXISTS why_it_matters TEXT,                -- Strategic context (1-2 sentences)
ADD COLUMN IF NOT EXISTS primary_theme TEXT,                 -- Main theme/topic
ADD COLUMN IF NOT EXISTS content_type TEXT;                  -- Type: news/research/opinion/analysis

-- Add comments for documentation
COMMENT ON COLUMN articles.ai_summary IS 'Comprehensive AI-generated summary (300-500 words)';
COMMENT ON COLUMN articles.ai_summary_short IS 'Brief summary for Slack display (500 chars max)';
COMMENT ON COLUMN articles.key_quotes IS 'Array of {quote, speaker, context} objects';
COMMENT ON COLUMN articles.key_metrics IS 'Array of {metric, value, context} objects';
COMMENT ON COLUMN articles.why_it_matters IS 'Strategic implications and relevance (1-2 sentences)';
COMMENT ON COLUMN articles.primary_theme IS 'Primary theme/topic of the article';
COMMENT ON COLUMN articles.content_type IS 'Content type: news, research, opinion, or analysis';

-- Create indexes for searching
CREATE INDEX IF NOT EXISTS idx_articles_primary_theme ON articles(primary_theme);
CREATE INDEX IF NOT EXISTS idx_articles_content_type ON articles(content_type);
CREATE INDEX IF NOT EXISTS idx_articles_ai_summary_fulltext ON articles USING gin(to_tsvector('english', ai_summary));

-- Update existing articles to have empty arrays/nulls (non-breaking)
UPDATE articles 
SET 
  key_quotes = '[]'::jsonb,
  key_metrics = '[]'::jsonb
WHERE key_quotes IS NULL OR key_metrics IS NULL;

COMMIT;
```

**JSONB Structure:**

```json
// key_quotes format
[
  {
    "quote": "Without proper governance, AI becomes a liability",
    "speaker": "Chief Risk Officer, Fortune 500 Financial Services",
    "context": "Discussing enterprise AI governance frameworks",
    "relevance": "Highlights importance of governance for risk management"
  }
]

// key_metrics format
[
  {
    "metric": "Compliance overhead reduction",
    "value": "40%",
    "context": "Early adopters of governance framework",
    "significance": "Significant operational efficiency gain"
  },
  {
    "metric": "Enterprises lacking AI governance",
    "value": "73%",
    "context": "Current market state",
    "significance": "Large market opportunity for governance solutions"
  }
]
```

---

## 🤖 **AI Prompt Updates**

### **New Stage 2.5: Context Enrichment Prompt**

```python
CONTEXT_ENRICHMENT_PROMPT = """
You are analyzing articles for an executive AI newsletter focused on:
- Vendor-agnostic AI strategies
- Data preparation and governance
- Avoiding vendor lock-in
- Enterprise AI decision-making

For each article, extract:

1. COMPREHENSIVE SUMMARY (300-500 words)
   - Main topic and key arguments
   - Important findings or developments
   - Evidence and examples provided
   - Implications for enterprise AI strategy

2. BRIEF SUMMARY (500 characters max)
   - Concise overview for Slack display
   - Focus on most important points
   - Must be under 500 characters

3. KEY METRICS (2-3 maximum)
   - Specific numbers, percentages, or statistics
   - Context for each metric
   - Why it's significant
   - If no metrics available, leave empty array

4. KEY QUOTES (1-2 maximum)
   - Direct quotes that capture essence
   - Include speaker/source
   - Explain relevance
   - If no notable quotes, leave empty array

5. WHY IT MATTERS (1-2 sentences)
   - Strategic implications for enterprise AI
   - Relevance to vendor independence
   - Connection to data strategy
   - Action-oriented insight

6. PRIMARY THEME
   - Single main theme/topic
   - Examples: "AI Governance", "Vendor Lock-in", "Data Strategy", 
     "Model Performance", "Enterprise Adoption", "Regulatory Compliance"

7. CONTENT TYPE
   - One of: "news", "research", "opinion", "analysis"

Return as JSON:
{
  "ai_summary": "Comprehensive 300-500 word summary...",
  "ai_summary_short": "Brief 500 char summary...",
  "key_metrics": [
    {
      "metric": "Metric name",
      "value": "40%",
      "context": "Context for this metric",
      "significance": "Why this matters"
    }
  ],
  "key_quotes": [
    {
      "quote": "Direct quote text",
      "speaker": "Person/Organization",
      "context": "Context of the quote",
      "relevance": "Why this quote matters"
    }
  ],
  "why_it_matters": "1-2 sentence strategic implication...",
  "primary_theme": "Theme name",
  "content_type": "news|research|opinion|analysis"
}

Article to analyze:
Title: {title}
Source: {source}
Content: {content}
"""
```

---

## 💻 **Code Changes**

### **1. Update `processors/multi_stage_digest.py`**

Add new Stage 2.5 between Stage 2 and final selection:

```python
async def stage_2_5_context_enrichment(
    self, 
    selected_articles: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Stage 2.5: Enrich selected articles with detailed context
    
    For each article, generate:
    - Comprehensive summary
    - Brief summary (500 chars)
    - Key metrics (2-3)
    - Key quotes (1-2)
    - Why it matters
    - Theme classification
    """
    
    enriched_articles = []
    
    for article in selected_articles:
        try:
            # Get context enrichment prompt
            prompt = await self.prompt_service.get_formatted_prompt(
                'context_enrichment_prompt',
                title=article['title'],
                source=article['source_name'],
                content=article.get('content_excerpt', '')
            )
            
            # Call OpenAI for context enrichment
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse JSON response
            if content.startswith('```json'):
                content = content.replace('```json', '').replace('```', '').strip()
            elif content.startswith('```'):
                content = content.replace('```', '').strip()
            
            context = json.loads(content)
            
            # Merge context into article
            enriched_article = article.copy()
            enriched_article.update({
                'ai_summary': context.get('ai_summary', ''),
                'ai_summary_short': context.get('ai_summary_short', '')[:500],  # Enforce limit
                'key_metrics': context.get('key_metrics', []),
                'key_quotes': context.get('key_quotes', []),
                'why_it_matters': context.get('why_it_matters', ''),
                'primary_theme': context.get('primary_theme', ''),
                'content_type': context.get('content_type', 'news')
            })
            
            enriched_articles.append(enriched_article)
            
            self.logger.info(f"Enriched context for: {article['title']}")
            
        except Exception as e:
            self.logger.error(f"Failed to enrich context for {article['title']}: {e}")
            # Fall back to original article
            enriched_articles.append(article)
    
    return enriched_articles
```

Update `create_daily_digest` method:

```python
async def create_daily_digest(self, all_articles: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Complete multi-stage digest creation process"""
    
    # Stage 1: Initial filtering
    stage_1_articles = await self.stage_1_filtering(all_articles)
    
    # Stage 2: Final selection
    final_articles, digest_text, key_insights, article_summaries = await self.stage_2_final_selection(stage_1_articles)
    
    # Stage 2.5: Context enrichment (NEW)
    enriched_articles = await self.stage_2_5_context_enrichment(final_articles)
    
    return {
        'selected_articles': enriched_articles,  # Use enriched articles
        'digest_text': digest_text,
        'key_insights': key_insights,
        'article_summaries': article_summaries,
        'total_processed': len(all_articles),
        'stage_1_count': len(stage_1_articles),
        'final_count': len(enriched_articles)
    }
```

### **2. Update `database/digest_storage.py`**

Update `store_daily_digest` to save enriched context:

```python
async def store_daily_digest(
    self, 
    digest_date: date,
    summary_text: str,
    key_insights: List[str],
    selected_articles: List[Dict[str, Any]],
    total_processed: int,
    ai_reasoning: str = "",
    article_summaries: List[Dict[str, Any]] = None
) -> str:
    """Store daily digest with enriched article context"""
    
    try:
        article_ids = []
        for article in selected_articles:
            article_data = {
                'title': article['title'],
                'content_excerpt': article.get('content_excerpt', ''),
                'url': article['url'],
                'source_name': article['source_name'],
                'source_type': article['source_type'],
                'published_at': article.get('published_date'),
                'week_start_date': self._get_week_start(digest_date).isoformat(),
                'tags': article.get('tags', []),
                'relevance_score': article.get('relevance_score', 60.0),
                'business_impact_score': article.get('business_impact_score', 55.0),
                'selected_for_digest': True,
                'scraped_at': datetime.now().isoformat(),
                
                # NEW: Enhanced context fields
                'ai_summary': article.get('ai_summary', ''),
                'ai_summary_short': article.get('ai_summary_short', ''),
                'key_quotes': article.get('key_quotes', []),
                'key_metrics': article.get('key_metrics', []),
                'why_it_matters': article.get('why_it_matters', ''),
                'primary_theme': article.get('primary_theme', ''),
                'content_type': article.get('content_type', 'news')
            }
            
            # Store article...
            article_id = await self.db_client.insert_article(article_data)
            article_ids.append(article_id)
        
        # Rest of the method remains the same...
```

### **3. Update `services/slack_notifier.py`**

Update `format_digest_message` to use enriched context:

```python
def format_digest_message(
    self, 
    digest_date: date,
    summary_text: str,
    key_insights: List[str],
    selected_articles: List[Dict[str, Any]],
    total_processed: int,
    rss_count: int = 0,
    twitter_count: int = 0
) -> Dict:
    """Format daily digest with enhanced context"""
    
    blocks = []
    
    # Header, Summary, Key Insights (same as before)
    # ...
    
    # Individual articles with enhanced context
    for idx, article in enumerate(selected_articles[:5], 1):
        number_emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
        
        # Use ai_summary_short (500 chars) instead of content_excerpt
        summary = article.get('ai_summary_short', article.get('content_excerpt', ''))[:500]
        
        # Build article text with enhanced context
        article_text = f"*{number_emojis[idx-1]} {article['title']}*\n_{article['source_name']}_\n\n"
        
        # Add summary
        article_text += f"📝 {summary}\n\n"
        
        # Add key metrics (if available)
        metrics = article.get('key_metrics', [])
        if metrics:
            article_text += "📊 *Key Data:*\n"
            for metric in metrics[:3]:  # Max 3 metrics
                article_text += f"• {metric.get('metric', 'Metric')}: {metric.get('value', 'N/A')}\n"
            article_text += "\n"
        
        # Add key quote (if available)
        quotes = article.get('key_quotes', [])
        if quotes and len(quotes) > 0:
            quote = quotes[0]  # Use first quote
            article_text += f"💬 *Quote:* \"{quote.get('quote', '')}\"\n"
            if quote.get('speaker'):
                article_text += f"   _{quote.get('speaker', '')}_\n"
            article_text += "\n"
        
        # Add "Why This Matters"
        why_matters = article.get('why_it_matters', '')
        if why_matters:
            article_text += f"🎯 *Why This Matters:* {why_matters}\n\n"
        
        # Add link
        article_text += f"<{article['url']}|🔗 Read Full Article>"
        
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": article_text
            }
        })
        
        # Divider between articles
        if idx < len(selected_articles[:5]):
            blocks.append({"type": "divider"})
    
    # Stats footer (same as before)
    # ...
    
    return {"blocks": blocks}
```

---

## 🧪 **Testing Plan**

### **Phase 1: Database Migration**

```bash
# 1. Test migration on development database
# Create test migration file
cat > test_migration.sql << 'EOF'
-- Test migration script
BEGIN;

ALTER TABLE articles 
ADD COLUMN IF NOT EXISTS ai_summary TEXT,
ADD COLUMN IF NOT EXISTS ai_summary_short TEXT,
ADD COLUMN IF NOT EXISTS key_quotes JSONB,
ADD COLUMN IF NOT EXISTS key_metrics JSONB,
ADD COLUMN IF NOT EXISTS why_it_matters TEXT,
ADD COLUMN IF NOT EXISTS primary_theme TEXT,
ADD COLUMN IF NOT EXISTS content_type TEXT;

-- Verify columns added
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'articles' 
AND column_name IN ('ai_summary', 'key_quotes', 'key_metrics');

ROLLBACK;  -- Don't commit yet, just test
EOF

# 2. Run test migration
# (Execute in Supabase SQL Editor)
```

### **Phase 2: Code Testing**

```bash
# 1. Test context enrichment with sample article
python3 -c "
import asyncio
from processors.multi_stage_digest import MultiStageDigestProcessor
from config.settings import Settings

async def test():
    settings = Settings()
    processor = MultiStageDigestProcessor(settings)
    
    sample_article = {
        'title': 'Test Article',
        'source_name': 'Test Source',
        'content_excerpt': 'Sample content for testing...'
    }
    
    enriched = await processor.stage_2_5_context_enrichment([sample_article])
    print('Enriched article:', enriched[0])

asyncio.run(test())
"

# 2. Test Slack formatting
python3 test_slack_integration.py

# 3. Test full pipeline
python3 run_ai_digest_pipeline.py
```

### **Phase 3: Validation**

- [ ] Verify database columns created
- [ ] Verify enriched context stored correctly
- [ ] Verify Slack message formatting
- [ ] Check message length (under Slack limits)
- [ ] Verify links work
- [ ] Test with articles that have no metrics/quotes
- [ ] Monitor AI API costs

---

## 📋 **Implementation Checklist**

### **Step 1: Database Migration**
- [ ] Review migration SQL script
- [ ] Test on development database
- [ ] Execute migration on production
- [ ] Verify columns added successfully
- [ ] Check indexes created

### **Step 2: Add Context Enrichment Prompt**
- [ ] Create prompt in Supabase `ai_prompts` table
- [ ] Test prompt with sample articles
- [ ] Verify JSON output format
- [ ] Adjust prompt if needed

### **Step 3: Update Code**
- [ ] Add `stage_2_5_context_enrichment` to `multi_stage_digest.py`
- [ ] Update `create_daily_digest` to call Stage 2.5
- [ ] Update `digest_storage.py` to save enriched fields
- [ ] Update `slack_notifier.py` to format enhanced context
- [ ] Add error handling for missing fields

### **Step 4: Testing**
- [ ] Test context enrichment with sample articles
- [ ] Test Slack message formatting
- [ ] Test full pipeline locally
- [ ] Verify database storage
- [ ] Check Slack message appears correctly

### **Step 5: Deployment**
- [ ] Commit changes with descriptive message
- [ ] Push to GitHub
- [ ] Monitor first automated run
- [ ] Verify Slack messages look good
- [ ] Check AI API costs

### **Step 6: Monitoring**
- [ ] Monitor AI API usage for 1 week
- [ ] Collect feedback on context quality
- [ ] Adjust prompts if needed
- [ ] Document any issues

---

## 💰 **Cost Monitoring**

**Expected Costs:**
- Current: ~$0.25/day
- Enhanced: ~$0.45/day (+$0.20)
- Monthly: ~$13.50 (+$6)

**Monitor:**
- OpenAI API dashboard
- Token usage per article
- Total daily cost
- Adjust if exceeding budget

---

## 📊 **Success Metrics**

**Quantitative:**
- [ ] All 5 articles have enriched context
- [ ] 80%+ articles have at least 1 metric
- [ ] 60%+ articles have at least 1 quote
- [ ] 100% articles have "why it matters"
- [ ] Slack messages under character limits
- [ ] AI costs within budget (+$6/month)

**Qualitative:**
- [ ] Context is relevant and useful
- [ ] Metrics are meaningful
- [ ] Quotes add value
- [ ] "Why it matters" is actionable
- [ ] Slack messages are readable

---

## 🔮 **Phase 2 Preparation**

**Document for Future:**

### **Interactive Features (Phase 2)**

**"Analyze More" Button:**
- On-click: Scrape full article text
- Generate deep analysis (1000+ words)
- Extract all quotes, metrics, implications
- Show in expanded Slack message or thread

**Implementation Notes:**
- Use Slack Block Kit buttons
- Set up webhook endpoint for button clicks
- Add article scraping service
- Store deep analysis in separate table
- Cache to avoid re-scraping

**Cost Estimate:**
- Full article scraping: ~$0.05 per article
- Deep analysis: ~$0.10 per article
- Only charged when button clicked
- Estimated: $5-10/month (if 50-100 deep dives)

**Timeline:**
- 1-2 weeks after Phase 1 stable
- Requires Slack Bot API (not webhooks)
- Requires webhook endpoint (AWS Lambda/Vercel)

---

## 🚀 **Next Steps**

1. **Review this plan** - Confirm approach
2. **Execute database migration** - Add new columns
3. **Add context enrichment prompt** - To Supabase
4. **Update code** - All three files
5. **Test thoroughly** - Local testing first
6. **Deploy carefully** - Monitor closely
7. **Iterate** - Adjust based on results

---

**Status**: ⏸️ Ready to implement - Awaiting final approval

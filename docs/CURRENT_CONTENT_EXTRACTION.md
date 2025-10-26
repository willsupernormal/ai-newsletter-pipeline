# 📄 Current Content Extraction Analysis

**Date**: October 26, 2025  
**Status**: Analysis Complete

---

## 🔍 **What We're Currently Doing**

### **RSS Feed Scraping Process:**

```
1. Fetch RSS Feed XML
   ↓
2. Parse with feedparser
   ↓
3. Extract from RSS entry:
   - entry.content (if available)
   - OR entry.summary
   - OR entry.description
   ↓
4. Clean HTML content:
   - Remove <script>, <style>, <nav>, <footer>, <aside>
   - Extract text with BeautifulSoup
   - Clean whitespace
   ↓
5. Truncate to 500 characters
   ↓
6. Store as 'content_excerpt'
```

---

## 📊 **Current Data Captured**

### **From RSS Feed:**
- ✅ **Title** - Full article title
- ✅ **URL** - Link to original article
- ✅ **Content Excerpt** - **ONLY 500 characters** (truncated)
- ✅ **Source Name** - Feed name (VentureBeat, MIT Tech Review, etc.)
- ✅ **Published Date** - When article was published
- ✅ **Tags** - Auto-extracted keywords

### **What We DON'T Have:**
- ❌ **Full Article Text** - We only get 500 chars from RSS
- ❌ **Full Article Body** - Not scraped from original URL
- ❌ **Images** - Not captured
- ❌ **Author** - Not always in RSS feed

---

## 🎯 **Key Finding**

**We are NOT scraping full articles right now!**

The RSS feed only provides:
1. A summary/description (varies by feed)
2. We truncate it to **500 characters**
3. This becomes the `content_excerpt`

**This is what the AI uses for:**
- Stage 1 filtering (100+ → 20)
- Stage 2 selection (20 → 5)
- Stage 2.5 context enrichment (summaries, metrics, quotes)

---

## 💡 **Implications for Phase 2**

### **Current Limitation:**
The AI is generating summaries, metrics, and quotes from **only 500 characters** of content!

This means:
- ✅ Good enough for relevance filtering
- ✅ Good enough for basic summaries
- ⚠️ **Limited** for extracting detailed metrics
- ⚠️ **Limited** for finding good quotes
- ❌ **Not enough** for comprehensive analysis

### **Why This Matters for Airtable:**
When you click "Add to Pipeline", you'll get:
- ✅ AI-generated context (based on 500 chars)
- ❌ Full article text (unless we scrape it)

---

## 🚀 **Recommendation for Phase 2**

### **Option 1: Scrape on Demand (Recommended)**
When user clicks "Add to Pipeline":
1. Fetch full article from URL
2. Extract full text with `newspaper3k` or `trafilatura`
3. Store in Airtable as "Full Article Text"
4. Keep existing AI context (already generated)

**Pros:**
- Only scrape articles you actually want
- Saves bandwidth and time
- Full article available for your research

**Cons:**
- Slight delay when clicking button (2-5 seconds)
- Some sites may block scraping

### **Option 2: Scrape Everything Upfront**
Scrape all 148 articles during daily pipeline:
1. After RSS scraping, visit each URL
2. Extract full article text
3. Store in Supabase
4. Use for AI analysis

**Pros:**
- Instant "Add to Pipeline" (already scraped)
- Better AI analysis (more context)
- More accurate metrics/quotes

**Cons:**
- Much slower pipeline (5-10 minutes longer)
- More bandwidth usage
- Some scraping may fail

### **Option 3: Hybrid Approach**
1. Use 500 chars for filtering (current)
2. Scrape full article for final 5 selected articles
3. Re-run Stage 2.5 enrichment with full text
4. Store both excerpt and full text

**Pros:**
- Best of both worlds
- Better AI context for selected articles
- Reasonable performance

**Cons:**
- More complex
- Pipeline takes a bit longer

---

## 🎯 **My Recommendation**

**For Phase 2 MVP: Option 1 (Scrape on Demand)**

Why:
- ✅ Simple to implement
- ✅ Fast pipeline (no change)
- ✅ Only scrape what you need
- ✅ Full article available in Airtable
- ✅ Can upgrade to Option 3 later if needed

---

## 🔧 **Implementation Plan**

### **What We'll Build:**

```python
# New file: scrapers/article_scraper.py

class ArticleScraper:
    """Scrape full article text from URL"""
    
    async def scrape_article(self, url: str) -> dict:
        """
        Scrape full article from URL
        
        Returns:
        {
            'full_text': 'Complete article text...',
            'word_count': 1500,
            'author': 'John Doe',
            'images': ['url1', 'url2'],
            'success': True
        }
        """
```

### **When User Clicks "Add to Pipeline":**

```
1. Get article_id from button
2. Fetch article from Supabase (get URL + existing context)
3. Scrape full article from URL
4. Combine:
   - Existing AI context (summary, metrics, quotes)
   - Full article text (scraped)
5. Push to Airtable
6. Confirm in Slack
```

---

## 📋 **Airtable Fields (Updated)**

### **From Current Pipeline:**
- Title, URL, Source, Theme, Content Type
- AI Summary Short (500 chars)
- AI Summary Full (300-500 words) - **based on 500 char excerpt**
- Key Metrics - **extracted from 500 chars**
- Key Quotes - **extracted from 500 chars**
- Why It Matters
- Supabase ID

### **NEW - From On-Demand Scrape:**
- **Full Article Text** - Complete article (2000-5000 words)
- **Word Count** - Actual article length
- **Author** - If available
- **Scraped At** - When we scraped it

---

## ✅ **Decision Needed**

**Which option do you prefer?**

1. **Option 1**: Scrape on-demand when clicking "Add to Pipeline" ← **Recommended**
2. **Option 2**: Scrape all 148 articles during pipeline
3. **Option 3**: Scrape only final 5 selected articles

**My vote: Option 1** - Simple, fast, and gives you full article when you need it.

---

**Let me know and I'll implement it!** 🚀

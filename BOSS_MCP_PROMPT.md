# AI Newsletter Database - Boss Interaction Guide

## 🤖 **CLAUDE SYSTEM PROMPT** (Copy this into your Claude Project)

```
You are an AI assistant helping a business executive interact with their AI Newsletter Pipeline database via Supabase MCP. Your role is to help them efficiently find, analyze, and curate AI/business content for their newsletter.

CONTEXT:
- The database contains daily AI-curated digests with top 5 articles from 50+ sources
- Articles are scored 0-100 for business relevance (80+ = newsletter-worthy)
- Content focuses on "Don't panic. Prepare your data. Stay agnostic." philosophy
- Daily digests are created automatically each morning with AI-generated summaries

PRIMARY TABLE: daily_digests
- This is the main entry point - always start here
- Contains daily summaries, key insights, and selected article IDs
- Each digest has 5 carefully chosen articles from that day's collection

KEY WORKFLOWS:
1. MORNING ROUTINE: Check today's digest and key insights
2. WEEKLY CURATION: Review week's themes, search specific topics, mark articles for newsletter
3. PERFORMANCE ANALYSIS: Track source quality and content trends

IMPORTANT PRINCIPLES:
- Always start with daily_digests table for context
- Use natural language to translate business needs into database queries
- Focus on high-relevance articles (score 80+) for newsletter selection
- Help identify trending themes and actionable business insights
- Prioritize vendor-agnostic, data strategy, and executive decision-making content

SAFETY:
- Only update: selected_for_newsletter, newsletter_priority, curator_notes fields
- Never modify article content, scores, or source data
- Always confirm before making bulk updates

Be proactive in suggesting relevant queries based on the user's needs and help them efficiently navigate the content for their business newsletter.
```

## Overview
This database contains your AI newsletter pipeline data, organized for easy interaction via Claude's Supabase MCP integration. The system runs daily, collecting and processing AI/business articles, then creating daily digests with the top 5 most relevant articles.

## 🎯 **START HERE - Your Primary Table: `daily_digests`**

**This is your main entry point.** Every day, the AI creates a comprehensive digest with:
- **5 carefully selected articles** from 50+ sources
- **AI-generated summary** of key themes
- **Key insights** highlighting important trends
- **Links to all selected articles**

### Essential Daily Queries

```sql
-- Today's digest (start here every morning)
SELECT * FROM daily_digests 
WHERE digest_date = CURRENT_DATE 
ORDER BY created_at DESC LIMIT 1;

-- Last 7 days of digests
SELECT digest_date, summary_text, key_insights, 
       array_length(selected_article_ids, 1) as article_count
FROM daily_digests 
WHERE digest_date >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY digest_date DESC;

-- This week's digest overview
SELECT 
    digest_date,
    LEFT(summary_text, 150) || '...' as summary_preview,
    array_length(selected_article_ids, 1) as articles_selected,
    total_articles_processed
FROM daily_digests 
WHERE digest_date >= DATE_TRUNC('week', CURRENT_DATE)
ORDER BY digest_date DESC;
```

## 📊 **Key Database Tables**

### 1. `daily_digests` - Your Main Dashboard
- **Purpose**: Daily AI-curated summaries with top 5 articles
- **Key Fields**: 
  - `digest_date`: Date of digest
  - `summary_text`: AI-generated overview of the day's themes
  - `key_insights`: Array of important takeaways
  - `selected_article_ids`: IDs of the 5 chosen articles
  - `total_articles_processed`: How many articles were considered
  - `ai_reasoning`: Why these articles were selected

### 2. `articles` - Individual Article Details
- **Purpose**: Full text and metadata for all collected articles
- **Key Fields**:
  - `title`, `url`, `content_excerpt`: Article basics
  - `source_name`, `source_type`: Where it came from (RSS, Twitter, Gmail)
  - `relevance_score`: AI rating (0-100, higher = more relevant)
  - `published_at`, `scraped_at`: Timing information
  - `selected_for_newsletter`: Articles you've marked for publication
  - `newsletter_priority`: Your ranking (1=lead story, 2-5=supporting)

### 3. `current_week_articles` - This Week's Content (View)
- **Purpose**: Pre-filtered view of this week's articles with priority levels
- **Automatically shows**: Only current week, sorted by relevance

### 4. `newsletter_articles` - Your Selected Content (View)
- **Purpose**: Articles you've marked for newsletter publication
- **Automatically shows**: Only selected articles, sorted by your priority

## 🚀 **Common Boss Workflows**

### Morning Routine (5 minutes)
```sql
-- 1. Check today's digest
SELECT digest_date, summary_text, key_insights 
FROM daily_digests 
WHERE digest_date = CURRENT_DATE;

-- 2. See today's selected articles
SELECT a.title, a.source_name, a.url, a.relevance_score
FROM articles a
JOIN daily_digests d ON a.id = ANY(d.selected_article_ids)
WHERE d.digest_date = CURRENT_DATE
ORDER BY a.relevance_score DESC;
```

### Weekly Newsletter Curation (15 minutes)
```sql
-- 1. See this week's top themes
SELECT digest_date, key_insights
FROM daily_digests 
WHERE digest_date >= DATE_TRUNC('week', CURRENT_DATE)
ORDER BY digest_date DESC;

-- 2. Find articles by topic (example: vendor lock-in)
SELECT title, source_name, relevance_score, url
FROM current_week_articles 
WHERE LOWER(title) LIKE '%vendor%' 
   OR LOWER(content_excerpt) LIKE '%lock-in%'
   OR 'vendor_lockin' = ANY(tags)
ORDER BY relevance_score DESC;

-- 3. Mark articles for newsletter (replace with actual IDs)
UPDATE articles 
SET selected_for_newsletter = TRUE, 
    newsletter_priority = 1,
    curator_notes = 'Lead story - excellent vendor lock-in analysis'
WHERE id = 'your-article-id-here';
```

### Performance Analysis (Monthly)
```sql
-- Source performance this month
SELECT 
    source_name,
    COUNT(*) as articles_collected,
    AVG(relevance_score) as avg_relevance,
    COUNT(*) FILTER (WHERE selected_for_newsletter) as newsletter_selected
FROM articles 
WHERE scraped_at >= DATE_TRUNC('month', CURRENT_DATE)
GROUP BY source_name
ORDER BY avg_relevance DESC;

-- Trending topics this month
SELECT 
    unnest(tags) as topic,
    COUNT(*) as frequency,
    AVG(relevance_score) as avg_relevance
FROM articles 
WHERE scraped_at >= DATE_TRUNC('month', CURRENT_DATE)
  AND tags IS NOT NULL
GROUP BY topic
HAVING COUNT(*) >= 3
ORDER BY frequency DESC, avg_relevance DESC;
```

## 🎯 **Natural Language Query Examples**

Use these phrases with Claude MCP:

### Daily Digest Queries
- *"Show me today's daily digest"*
- *"What were the key insights from yesterday?"*
- *"Give me the last 3 days of digest summaries"*
- *"What themes are trending this week based on daily digests?"*

### Article Discovery
- *"Find all articles about vendor lock-in from this week"*
- *"Show me high-scoring data strategy articles"*
- *"What AI governance stories do we have with relevance score above 80?"*
- *"Find articles from MIT Technology Review this week"*

### Newsletter Curation
- *"Mark article ID abc123 for newsletter with priority 1"*
- *"Show me all articles I've selected for this week's newsletter"*
- *"What's the best article about enterprise AI from this week?"*
- *"Set these 3 articles as my newsletter selection: [list IDs]"*

### Analytics & Insights
- *"Which sources performed best this week?"*
- *"Show me relevance score trends over the past month"*
- *"What topics appear most frequently in high-scoring articles?"*
- *"How many articles did we process each day this week?"*

## 🔧 **Pro Tips**

### 1. **Start with Daily Digests**
Always begin with `daily_digests` table - it's your curated entry point.

### 2. **Use the Views**
- `current_week_articles`: Pre-filtered for this week
- `newsletter_articles`: Shows your selections
- `source_performance`: Source quality metrics

### 3. **Relevance Scores Guide**
- **90-100**: Exceptional, must-read content
- **80-89**: High quality, newsletter-worthy
- **70-79**: Good content, worth reviewing
- **60-69**: Decent, but may not make newsletter
- **Below 60**: Lower priority

### 4. **Search Tips**
- Use `ILIKE` for case-insensitive searches: `title ILIKE '%AI%'`
- Search tags array: `'data_strategy' = ANY(tags)`
- Date ranges: `scraped_at >= CURRENT_DATE - INTERVAL '7 days'`

### 5. **Newsletter Workflow**
1. Review daily digests for the week
2. Search for specific themes you want to cover
3. Mark articles with `selected_for_newsletter = TRUE`
4. Set `newsletter_priority` (1=lead, 2-5=supporting)
5. Add `curator_notes` for context

## 🚨 **Important Notes**

- **Daily Digests**: Created automatically each morning with top 5 articles
- **Article Scoring**: AI evaluates based on business relevance, data strategy themes, and actionability
- **Weekly Organization**: All content is organized by week starting Monday
- **Source Tracking**: System monitors which sources deliver the best content
- **Safe Updates**: You can safely update `selected_for_newsletter`, `newsletter_priority`, and `curator_notes`

## 📞 **Need Help?**

If you need specific queries or have questions about the data structure, just ask Claude using natural language. The MCP integration understands the database schema and can help you find exactly what you're looking for.

**Remember**: Start with daily digests, then drill down to individual articles as needed. The AI has already done the heavy lifting of finding the most relevant content each day.

# Weekly Newsletter Curation Workflow

A guide for using the AI newsletter pipeline with Claude MCP integration for efficient content curation.

## Overview

The pipeline runs automatically daily at 7 AM UTC, collecting and scoring content. Your weekly workflow focuses on curation during weekends using natural language queries through Claude MCP integration.

## Daily Automation (Hands-off)

### What Happens Automatically
- **7:00 AM UTC Daily:** Pipeline scrapes RSS feeds, Twitter, and Gmail newsletters
- **Content Processing:** Articles are cleaned, deduplicated, and AI-scored
- **Weekly Organization:** Content is organized by week (Monday-Sunday cycles)
- **Database Storage:** Only articles meeting relevance threshold (50+) are stored

### Monitoring (Optional)
- Check GitHub Actions for any failures
- Automatic issue creation on failures
- Weekly cleanup runs on Mondays

## Weekend Curation Workflow

### Monday Morning Check (5 minutes)

Start your week by understanding what content was collected:

```sql
-- Quick weekly overview
SELECT 
  COUNT(*) as total_articles,
  AVG(relevance_score) as avg_score,
  COUNT(*) FILTER (WHERE relevance_score >= 80) as high_quality
FROM current_week_articles;
```

**Claude Query:** *"Show me this week's content summary and top 10 highest scored articles"*

### Mid-week Monitoring (As needed)

Stay updated on developing stories:

```sql
-- Check recent high-quality articles
SELECT title, source_name, relevance_score, published_at, url
FROM current_week_articles 
WHERE relevance_score >= 75
ORDER BY published_at DESC 
LIMIT 15;
```

**Claude Queries:**
- *"Any new vendor lock-in stories this week?"*
- *"What are the latest enterprise AI implementation articles?"*
- *"Show me this week's highest engagement Twitter posts"*

### Weekend Curation (15-20 minutes)

#### Step 1: Theme Analysis

Understand the week's major themes:

```sql
-- Get theme distribution
SELECT unnest(tags) as theme, COUNT(*) as frequency
FROM current_week_articles 
GROUP BY theme 
ORDER BY frequency DESC 
LIMIT 15;
```

**Claude Query:** *"What are the main themes and trends from this week's content?"*

#### Step 2: Content Selection by Category

Find the best articles in key categories:

```sql
-- Vendor lock-in focus
SELECT title, source_name, relevance_score, url, content_excerpt
FROM current_week_articles 
WHERE (tags @> ARRAY['vendor_lock_in'] OR 
       title ILIKE '%vendor%' OR 
       title ILIKE '%lock%' OR
       content_excerpt ILIKE '%vendor lock%')
ORDER BY relevance_score DESC 
LIMIT 10;
```

**Claude Queries:**
- *"Show me the top 5 vendor lock-in stories from this week"*
- *"What are the best data strategy articles this week?"*
- *"Find enterprise AI implementation stories with business impact"*
- *"Show me platform-agnostic technology articles from this week"*

#### Step 3: Source Quality Review

Check which sources delivered the best content:

```sql
-- Source performance this week
SELECT source_name, 
       COUNT(*) as articles,
       AVG(relevance_score) as avg_score,
       MAX(relevance_score) as best_score
FROM current_week_articles 
GROUP BY source_name 
ORDER BY avg_score DESC;
```

**Claude Query:** *"Which sources had the highest quality content this week?"*

#### Step 4: Article Selection

Select 3-5 articles for your newsletter:

```sql
-- Mark articles for newsletter
UPDATE articles 
SET selected_for_newsletter = TRUE,
    newsletter_priority = $1,
    curator_notes = $2
WHERE id = $3;
```

**Claude Workflow:**
1. *"Select articles with IDs abc123, def456, ghi789 for this week's newsletter"*
2. *"Set article abc123 as priority 1 (lead story)"*
3. *"Add curator note to article def456 about enterprise implications"*

#### Step 5: Newsletter Preview

Review your selections:

```sql
-- Preview newsletter content
SELECT title, source_name, newsletter_priority, curator_notes, relevance_score
FROM newsletter_articles 
ORDER BY newsletter_priority, relevance_score DESC;
```

**Claude Query:** *"Show me all selected articles for this week's newsletter with priorities"*

## Advanced Curation Techniques

### Cross-Source Story Tracking

Track how the same story appears across sources:

```sql
-- Find related articles by similar titles
SELECT title, source_name, relevance_score, published_at
FROM current_week_articles 
WHERE title ILIKE '%AI breakthrough%' OR title ILIKE '%OpenAI%'
ORDER BY relevance_score DESC;
```

### Engagement Analysis (Twitter)

Focus on high-engagement social content:

```sql
-- Top Twitter engagement
SELECT title, source_name, 
       twitter_metrics->>'engagement_rate' as engagement,
       twitter_metrics->>'likes' as likes,
       url
FROM current_week_articles 
WHERE source_type = 'twitter'
ORDER BY (twitter_metrics->>'engagement_rate')::float DESC 
LIMIT 10;
```

**Claude Query:** *"Show me this week's most engaging Twitter posts about AI"*

### Newsletter Source Analysis

Identify valuable newsletter sources:

```sql
-- Newsletter content quality
SELECT source_name,
       COUNT(*) as articles,
       AVG(relevance_score) as avg_score
FROM current_week_articles 
WHERE source_type = 'gmail_newsletter'
GROUP BY source_name
ORDER BY avg_score DESC;
```

## Monthly Review Workflow

### Performance Analysis

```sql
-- 4-week performance comparison
SELECT week_start_date,
       articles_collected,
       articles_curated,
       average_relevance_score
FROM weekly_trends 
ORDER BY week_start_date DESC 
LIMIT 4;
```

**Claude Query:** *"Compare this month's content collection with last month"*

### Source Optimization

```sql
-- Source performance over time
SELECT cs.name,
       cs.type,
       cs.success_count,
       cs.average_relevance_score,
       COUNT(a.id) as recent_articles
FROM content_sources cs
LEFT JOIN articles a ON a.source_name = cs.name 
  AND a.scraped_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY cs.id, cs.name, cs.type, cs.success_count, cs.average_relevance_score
ORDER BY cs.average_relevance_score DESC NULLS LAST;
```

**Claude Query:** *"Which sources consistently deliver the highest quality content?"*

### Content Pattern Analysis

```sql
-- Theme trending over time
SELECT week_start_date, 
       unnest(top_themes) as theme
FROM weekly_cycles 
WHERE week_start_date >= CURRENT_DATE - INTERVAL '8 weeks'
ORDER BY week_start_date DESC;
```

**Claude Query:** *"What themes have been trending over the past 2 months?"*

## Optimization Tips

### Improving Content Quality

1. **Adjust Relevance Threshold:**
   - If too many low-quality articles: Increase `MIN_RELEVANCE_SCORE`
   - If missing good content: Decrease threshold

2. **Refine AI Scoring:**
   - Monitor which articles you consistently select/reject
   - Adjust the scoring prompt in settings

3. **Source Management:**
   - Remove consistently low-performing sources
   - Add high-quality sources you discover

### Efficiency Improvements

1. **Template Queries:**
   Save frequently used queries as views in Supabase

2. **Notification Setup:**
   Create alerts for exceptionally high-scoring articles (90+)

3. **Batch Processing:**
   Process similar articles together (e.g., all vendor lock-in stories)

## Common Curation Patterns

### Weekly Newsletter Structure

**Lead Story (Priority 1):** Highest impact business story
**Featured Articles (Priority 2):** 2-3 supporting stories with different angles
**Brief Mentions (Priority 3):** Notable updates worth tracking

### Content Categories

- **Strategy & Business Impact:** Enterprise decisions, ROI, market analysis
- **Implementation Reality:** Real-world experiences, challenges, solutions  
- **Vendor Independence:** Platform choices, avoiding lock-in, open alternatives
- **Data & Infrastructure:** Preparation, governance, architecture decisions

### Quality Indicators to Look For

- **Actionable insights** over pure research
- **Business implications** clearly explained
- **Multiple perspectives** on controversial topics
- **Concrete examples** and case studies
- **Independent analysis** rather than vendor marketing

## Troubleshooting Common Issues

### No Content This Week
```sql
-- Check what was collected
SELECT source_type, COUNT(*), AVG(relevance_score)
FROM articles 
WHERE week_start_date = DATE_TRUNC('week', CURRENT_DATE)::DATE
GROUP BY source_type;
```

### Quality Seems Low
```sql
-- Analyze scoring patterns
SELECT 
  CASE 
    WHEN relevance_score >= 80 THEN 'High (80+)'
    WHEN relevance_score >= 60 THEN 'Medium (60-79)'
    ELSE 'Low (<60)'
  END as score_range,
  COUNT(*) as count
FROM current_week_articles
GROUP BY 1;
```

### Missing Expected Stories
Check if articles were filtered out due to:
- Low relevance scores
- Deduplication
- Source issues (RSS feed problems, API limits)

This workflow ensures you spend minimal time on curation while maintaining high newsletter quality through systematic content analysis and selection. 📊
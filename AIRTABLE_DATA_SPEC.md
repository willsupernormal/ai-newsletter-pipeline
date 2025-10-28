# 📊 Airtable Data Specification

**What Gets Added to Your Airtable Content Pipeline**

---

## 🎯 Complete Field List

When you click "Add to Pipeline" on a Slack digest article, these fields are added to Airtable:

### **Core Article Information**

| Field | Type | Example | Source |
|-------|------|---------|--------|
| **Title** | Text | "OpenAI Announces GPT-5: Major Breakthrough" | RSS Feed |
| **URL** | URL | https://techcrunch.com/article | RSS Feed |
| **Source** | Text | "TechCrunch" | RSS Feed |
| **Author** | Text | "Jane Smith" | RSS Feed |
| **Published Date** | Date | 2025-10-27 | RSS Feed |

### **AI-Generated Insights**

| Field | Type | Example | Source |
|-------|------|---------|--------|
| **Relevance Score** | Number (0-100) | 92 | AI Evaluator |
| **Category** | Text | "AI/ML - Large Language Models" | AI Evaluator |
| **Key Topics** | Text (comma-separated) | "GPT-5, OpenAI, reasoning, AI" | AI Evaluator |
| **Summary** | Long Text | "OpenAI announces GPT-5 with major improvements..." | AI Evaluator |
| **Business Impact** | Single Select | "high" / "medium" / "low" | AI Evaluator |
| **Sentiment** | Single Select | "positive" / "neutral" / "negative" | AI Evaluator |

### **Content Details**

| Field | Type | Example | Source |
|-------|------|---------|--------|
| **Excerpt** | Long Text | First 500 characters of article | Content Processor |
| **Word Count** | Number | 847 | Content Processor |

### **Pipeline Management**

| Field | Type | Example | Source |
|-------|------|---------|--------|
| **Status** | Single Select | "New" | System (default) |
| **Date Added** | DateTime | 2025-10-27 19:13:29 | System (timestamp) |
| **Added By** | Text | "AI Digest Bot" | System (bot name) |

---

## 🔄 Complete Data Flow

```
┌─────────────┐
│  RSS Feed   │ → Title, URL, Content, Date, Source, Author
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│ Content Processor   │ → Word Count, Excerpt, Cleaned Content
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│   AI Evaluator      │ → Relevance Score, Category, Topics, Summary,
└──────┬──────────────┘   Business Impact, Sentiment
       │
       ▼
┌─────────────────────┐
│     Supabase        │ → Stores complete article with all metadata
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│      Slack          │ → Posts digest with "Add to Pipeline" button
└──────┬──────────────┘
       │
       │ (User clicks button)
       ▼
┌─────────────────────┐
│     Railway         │ → Receives button click, fetches article
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│     Airtable        │ → Adds article with ALL fields listed above
└─────────────────────┘
```

---

## 📋 Example Airtable Record

Here's what an actual record looks like in Airtable:

```
Title: OpenAI Announces GPT-5: Major Breakthrough in AI Reasoning
URL: https://example.com/gpt5-announcement
Source: TechCrunch
Author: Jane Smith
Published Date: 2025-10-27
Category: AI/ML - Large Language Models
Relevance Score: 92
Key Topics: GPT-5, OpenAI, reasoning, artificial intelligence
Summary: OpenAI announces GPT-5 with major improvements in reasoning 
         and problem-solving capabilities.
Excerpt: OpenAI today announced GPT-5, marking a significant advancement 
         in artificial intelligence capabilities. The new model demonstrates 
         unprecedented reasoning abilities...
Business Impact: high
Sentiment: positive
Word Count: 847
Status: New
Date Added: 2025-10-27 19:13:29
Added By: AI Digest Bot
```

---

## 🎯 Field Purposes

### **For Content Curation:**
- **Title, URL, Source** - Identify and access the article
- **Published Date** - Know when it was published
- **Author** - Track content creators

### **For AI-Powered Filtering:**
- **Relevance Score** - Prioritize most relevant content (0-100)
- **Category** - Organize by topic area
- **Key Topics** - Tag and search by specific subjects
- **Summary** - Quick overview without reading full article

### **For Editorial Decisions:**
- **Business Impact** - Prioritize high-impact stories
- **Sentiment** - Balance positive/negative coverage
- **Excerpt** - Preview content quality

### **For Workflow Management:**
- **Status** - Track progress (New → In Progress → Published)
- **Date Added** - Sort by recency
- **Added By** - Know it came from AI Digest Bot

---

## ✅ Recommended Airtable Setup

### **Views to Create:**

1. **All Articles** - Default view showing all records
2. **High Priority** - Filter: Relevance Score ≥ 80
3. **By Category** - Group by: Category
4. **This Week** - Filter: Date Added (this week)
5. **To Review** - Filter: Status = "New"

### **Automations to Add:**

1. **Slack Notification** - When new record added, notify team
2. **Status Reminder** - If Status = "New" for > 3 days, send reminder
3. **Weekly Summary** - Every Monday, send summary of last week's additions

### **Additional Fields You Might Want:**

- **Assigned To** (User) - Who's working on this
- **Notes** (Long Text) - Editorial notes
- **Scheduled Date** (Date) - When to publish
- **Newsletter Issue** (Link) - Which newsletter it appeared in
- **Social Posts** (Link) - Links to social media posts about it

---

## 🔍 Data Quality

### **What's Guaranteed:**
- ✅ Title (always present)
- ✅ URL (always present)
- ✅ Source (always present)
- ✅ Date Added (always present)
- ✅ Added By (always "AI Digest Bot")

### **What's Usually Present:**
- ✅ Published Date (from RSS feed)
- ✅ Relevance Score (from AI)
- ✅ Category (from AI)
- ✅ Summary (from AI)

### **What's Sometimes Missing:**
- ⚠️ Author (not all RSS feeds include this)
- ⚠️ Excerpt (if content is very short)
- ⚠️ Word Count (if content couldn't be extracted)

---

## 🎯 Using the Data

### **For Newsletter Creation:**

1. Filter by **Relevance Score ≥ 80**
2. Group by **Category**
3. Select top 5-10 articles
4. Use **Summary** for newsletter descriptions
5. Update **Status** to "In Progress"

### **For Content Analysis:**

1. Track **Key Topics** over time
2. Monitor **Business Impact** distribution
3. Analyze **Sentiment** trends
4. Review **Source** diversity

### **For Team Collaboration:**

1. Assign articles using **Assigned To**
2. Add **Notes** for editorial guidance
3. Set **Scheduled Date** for publication
4. Update **Status** as work progresses

---

## ✅ Summary

**Every article added to Airtable includes:**
- ✅ Complete article metadata (title, URL, source, date, author)
- ✅ AI-generated insights (score, category, topics, summary)
- ✅ Content analysis (excerpt, word count, sentiment)
- ✅ Pipeline management (status, date added, added by)

**This gives you everything you need to:**
- 📊 Prioritize content by relevance
- 🏷️ Organize by category and topics
- 📝 Create newsletters efficiently
- 👥 Collaborate with your team
- 📈 Track content trends over time

---

**Your content pipeline is now fully automated from RSS → AI evaluation → Slack → Airtable!** 🎉

#!/usr/bin/env python3
"""
Test theme extraction on real articles
"""

import asyncio
from processors.theme_extractor import ThemeExtractor
from database.supabase_simple import SimpleSupabaseClient
from config.settings import Settings

async def test_theme_extraction():
    """Test theme extraction on stored articles"""
    
    settings = Settings()
    db_client = SimpleSupabaseClient(settings)
    theme_extractor = ThemeExtractor()
    
    # Get some articles from database
    articles = await db_client.execute_query(
        'articles', 
        'select',
        columns='title, content_excerpt, tags, source_name',
        limit=10
    )
    
    print("=== Theme Extraction Test ===\n")
    
    for i, article in enumerate(articles[:5], 1):
        title = article['title']
        content = article.get('content_excerpt', '')
        tags = article.get('tags', [])
        
        # Extract themes
        themes = theme_extractor.extract_themes(title, content, tags)
        
        print(f"{i}. {title}")
        print(f"   Source: {article['source_name']}")
        print(f"   Original tags: {tags}")
        print(f"   Extracted themes: {themes}")
        print()
    
    # Show theme frequency
    all_themes = []
    for article in articles:
        themes = theme_extractor.extract_themes(
            article['title'], 
            article.get('content_excerpt', ''), 
            article.get('tags', [])
        )
        all_themes.extend(themes)
    
    from collections import Counter
    theme_counts = Counter(all_themes)
    
    print("=== Most Common Themes ===")
    for theme, count in theme_counts.most_common(10):
        print(f"  {theme}: {count}")

if __name__ == "__main__":
    asyncio.run(test_theme_extraction())

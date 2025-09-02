#!/usr/bin/env python3
"""
Manually add a newsletter to the pipeline
No IMAP required - just paste the content
"""

import asyncio
from datetime import datetime, timedelta
from supabase import create_client
from config.settings import Settings
from processors.content_processor import ContentProcessor
from processors.ai_evaluator import AIEvaluator

async def add_newsletter():
    """Manually add a newsletter article"""
    
    print("=" * 60)
    print("MANUAL NEWSLETTER ADDER")
    print("=" * 60)
    
    # Get newsletter details
    print("\nPaste your newsletter details:")
    title = input("Title: ").strip()
    if not title:
        print("Title is required!")
        return
    
    source = input("Source (e.g., TechCrunch): ").strip() or "Newsletter"
    
    print("\nContent (paste newsletter text, then press Enter twice):")
    lines = []
    empty_count = 0
    while empty_count < 2:
        line = input()
        if line:
            lines.append(line)
            empty_count = 0
        else:
            empty_count += 1
    
    content = '\n'.join(lines).strip()
    
    if not content:
        print("Content is required!")
        return
    
    url = input("\nURL (optional, press Enter to skip): ").strip()
    
    # Create article
    article = {
        'title': title,
        'content_excerpt': content[:2000],  # Limit content length
        'source_type': 'gmail_newsletter',
        'source_name': source,
        'url': url or f"manual-newsletter-{datetime.now().timestamp()}",
        'published_at': datetime.now().isoformat(),
        'tags': ['newsletter', 'manual']
    }
    
    print("\n" + "=" * 60)
    print("Processing newsletter...")
    
    try:
        # Initialize components
        settings = Settings()
        content_processor = ContentProcessor()
        ai_evaluator = AIEvaluator(settings)
        
        # Process
        processed = content_processor.process_article(article)
        
        # Add week info
        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())
        processed['week_start_date'] = week_start.isoformat()
        
        # Evaluate with AI
        print("Evaluating with AI...")
        evaluated = await ai_evaluator.evaluate_article(processed)
        
        print(f"\n📊 AI Evaluation:")
        print(f"  Relevance Score: {evaluated.get('relevance_score', 0)}/100")
        print(f"  Business Impact: {evaluated.get('business_impact_score', 0)}/100")
        
        if evaluated.get('relevance_score', 0) >= settings.MIN_RELEVANCE_SCORE:
            print("\n✓ Article meets quality threshold!")
            
            save = input("\nSave to database? (y/n): ").lower()
            if save == 'y':
                # Clean fields for database
                evaluated['scraped_at'] = datetime.now().isoformat()
                evaluated['week_start_date'] = week_start.isoformat()
                
                # Convert datetime fields
                for field in ['published_at']:
                    if field in evaluated and isinstance(evaluated[field], datetime):
                        evaluated[field] = evaluated[field].isoformat()
                
                # Keep only schema fields
                allowed_fields = [
                    'title', 'url', 'content_excerpt', 'source_type', 'source_name',
                    'published_at', 'scraped_at', 'week_start_date', 'relevance_score',
                    'business_impact_score', 'tags'
                ]
                
                cleaned = {k: v for k, v in evaluated.items() if k in allowed_fields}
                
                # Save to database
                supabase = create_client(
                    settings.SUPABASE_URL,
                    settings.SUPABASE_SERVICE_KEY
                )
                
                response = supabase.table('articles').insert(cleaned).execute()
                
                if response.data:
                    print("✓ Newsletter saved successfully!")
                else:
                    print("✗ Failed to save newsletter")
        else:
            print(f"\n✗ Article below threshold (minimum: {settings.MIN_RELEVANCE_SCORE})")
            
    except Exception as e:
        print(f"\n✗ Error: {e}")

if __name__ == "__main__":
    asyncio.run(add_newsletter())
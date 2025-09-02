#!/usr/bin/env python3
"""Test AI evaluation with OpenAI"""

import asyncio
import logging
from config.settings import Settings
from processors.ai_evaluator import AIEvaluator

logging.basicConfig(level=logging.INFO)

async def test_ai_evaluation():
    """Test AI scoring with a sample article"""
    settings = Settings()
    evaluator = AIEvaluator(settings)
    
    # Sample article to test
    test_article = {
        'title': 'OpenAI Announces New Enterprise Data Platform for Vendor-Agnostic AI Deployment',
        'content_excerpt': 'OpenAI today unveiled a new enterprise platform designed to help companies deploy AI models across multiple cloud providers without vendor lock-in. The platform emphasizes data portability and allows businesses to maintain control of their data infrastructure while leveraging various AI capabilities.',
        'source_name': 'MIT Technology Review',
        'source_type': 'rss',
        'tags': ['ai', 'enterprise', 'platform']
    }
    
    print("Testing AI Evaluator with OpenAI...")
    print(f"Model: {settings.OPENAI_MODEL}")
    print(f"\nArticle: {test_article['title']}")
    print(f"Content: {test_article['content_excerpt'][:150]}...")
    
    try:
        print("\nEvaluating article...")
        result = await evaluator.evaluate_article(test_article)
        
        print(f"\n✓ Evaluation successful!")
        print(f"  Relevance Score: {result['relevance_score']}/100")
        print(f"  Business Impact Score: {result['business_impact_score']}/100")
        print(f"  Key Themes: {', '.join(result['tags'])}")
        print(f"  Reasoning: {result.get('ai_reasoning', 'N/A')}")
        
        return result
    except Exception as e:
        print(f"\n✗ Evaluation failed: {e}")
        raise

if __name__ == "__main__":
    result = asyncio.run(test_ai_evaluation())
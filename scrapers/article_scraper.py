"""
Full article scraper for on-demand content extraction
Uses newspaper3k and trafilatura for robust article extraction
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime
import aiohttp
import asyncio
from newspaper import Article
import trafilatura

class ArticleScraper:
    """Scrape full article text from URLs on-demand"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.timeout = aiohttp.ClientTimeout(total=30)
    
    async def scrape_article(self, url: str) -> Dict[str, Any]:
        """
        Scrape full article from URL using multiple methods
        
        Args:
            url: Article URL to scrape
            
        Returns:
            dict with:
                - full_text: Complete article text
                - word_count: Number of words
                - author: Author name (if available)
                - publish_date: Publication date (if available)
                - top_image: Main image URL (if available)
                - success: Boolean indicating success
                - error: Error message if failed
                - method: Which scraping method succeeded
        """
        
        self.logger.info(f"Scraping article: {url}")
        
        # Try newspaper3k first (better for news sites)
        result = await self._scrape_with_newspaper(url)
        if result['success']:
            return result
        
        # Fallback to trafilatura (better for blogs/general content)
        result = await self._scrape_with_trafilatura(url)
        if result['success']:
            return result
        
        # Both failed
        self.logger.error(f"Failed to scrape article: {url}")
        return {
            'full_text': '',
            'word_count': 0,
            'author': None,
            'publish_date': None,
            'top_image': None,
            'success': False,
            'error': 'All scraping methods failed',
            'method': None
        }
    
    async def _scrape_with_newspaper(self, url: str) -> Dict[str, Any]:
        """Scrape using newspaper3k library"""
        try:
            # Run in executor since newspaper3k is synchronous
            loop = asyncio.get_event_loop()
            article = await loop.run_in_executor(None, self._newspaper_sync, url)
            
            if article and article.text:
                word_count = len(article.text.split())
                
                self.logger.info(f"✓ Scraped with newspaper3k: {word_count} words")
                
                return {
                    'full_text': article.text,
                    'word_count': word_count,
                    'author': ', '.join(article.authors) if article.authors else None,
                    'publish_date': article.publish_date.isoformat() if article.publish_date else None,
                    'top_image': article.top_image if article.top_image else None,
                    'success': True,
                    'error': None,
                    'method': 'newspaper3k'
                }
            
            return {
                'success': False,
                'error': 'No text extracted',
                'method': 'newspaper3k'
            }
            
        except Exception as e:
            self.logger.warning(f"newspaper3k failed for {url}: {e}")
            return {
                'success': False,
                'error': str(e),
                'method': 'newspaper3k'
            }
    
    def _newspaper_sync(self, url: str) -> Optional[Article]:
        """Synchronous newspaper3k scraping (run in executor)"""
        try:
            article = Article(url)
            article.download()
            article.parse()
            return article
        except Exception as e:
            self.logger.debug(f"newspaper3k error: {e}")
            return None
    
    async def _scrape_with_trafilatura(self, url: str) -> Dict[str, Any]:
        """Scrape using trafilatura library"""
        try:
            # Fetch HTML
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(url, headers={'User-Agent': 'Mozilla/5.0'}) as response:
                    if response.status != 200:
                        return {
                            'success': False,
                            'error': f'HTTP {response.status}',
                            'method': 'trafilatura'
                        }
                    
                    html = await response.text()
            
            # Extract text with trafilatura
            text = trafilatura.extract(
                html,
                include_comments=False,
                include_tables=False,
                no_fallback=False
            )
            
            if text:
                word_count = len(text.split())
                
                self.logger.info(f"✓ Scraped with trafilatura: {word_count} words")
                
                return {
                    'full_text': text,
                    'word_count': word_count,
                    'author': None,  # trafilatura doesn't extract author easily
                    'publish_date': None,
                    'top_image': None,
                    'success': True,
                    'error': None,
                    'method': 'trafilatura'
                }
            
            return {
                'success': False,
                'error': 'No text extracted',
                'method': 'trafilatura'
            }
            
        except Exception as e:
            self.logger.warning(f"trafilatura failed for {url}: {e}")
            return {
                'success': False,
                'error': str(e),
                'method': 'trafilatura'
            }
    
    async def scrape_multiple(self, urls: list[str]) -> Dict[str, Dict[str, Any]]:
        """
        Scrape multiple articles concurrently
        
        Args:
            urls: List of URLs to scrape
            
        Returns:
            dict mapping URL to scrape result
        """
        tasks = [self.scrape_article(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            url: result if not isinstance(result, Exception) else {
                'success': False,
                'error': str(result),
                'full_text': '',
                'word_count': 0
            }
            for url, result in zip(urls, results)
        }

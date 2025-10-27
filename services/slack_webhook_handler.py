"""
Slack webhook handler for interactive button actions
Processes button clicks and routes to appropriate handlers
"""

import logging
import json
import hmac
import hashlib
import asyncio
import requests
from typing import Dict, Any, Optional
from datetime import datetime

from config.settings import Settings
from database.supabase_simple import SimpleSupabaseClient
from services.airtable_client import AirtableClient
from scrapers.article_scraper import ArticleScraper


class SlackWebhookHandler:
    """Handle Slack interactive message callbacks"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        self.supabase = SimpleSupabaseClient(settings)
        self.airtable = AirtableClient(settings)
        self.scraper = ArticleScraper()
        
        if not settings.SLACK_SIGNING_SECRET:
            raise ValueError("SLACK_SIGNING_SECRET not configured")
    
    def verify_slack_signature(self, timestamp: str, body: str, signature: str) -> bool:
        """
        Verify that request came from Slack
        
        Args:
            timestamp: X-Slack-Request-Timestamp header
            body: Raw request body
            signature: X-Slack-Signature header
            
        Returns:
            True if signature is valid
        """
        try:
            # Check timestamp is recent (within 5 minutes)
            request_timestamp = int(timestamp)
            current_timestamp = int(datetime.now().timestamp())
            
            if abs(current_timestamp - request_timestamp) > 60 * 5:
                self.logger.warning("Request timestamp too old")
                return False
            
            # Compute signature
            sig_basestring = f"v0:{timestamp}:{body}"
            my_signature = 'v0=' + hmac.new(
                self.settings.SLACK_SIGNING_SECRET.encode(),
                sig_basestring.encode(),
                hashlib.sha256
            ).hexdigest()
            
            # Compare signatures
            return hmac.compare_digest(my_signature, signature)
            
        except Exception as e:
            self.logger.error(f"Error verifying Slack signature: {e}")
            return False
    
    async def handle_interaction(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main handler for Slack interactions
        
        Responds immediately to Slack (< 3 seconds) and processes in background
        
        Args:
            payload: Slack interaction payload
            
        Returns:
            Response dict for Slack
        """
        try:
            action_id = payload.get('actions', [{}])[0].get('action_id')
            user_id = payload.get('user', {}).get('id')
            user_name = payload.get('user', {}).get('username', 'Unknown')
            response_url = payload.get('response_url')  # For async updates
            
            self.logger.info(f"Received action: {action_id} from user: {user_name}")
            
            # Route to appropriate handler
            if action_id == 'add_to_pipeline':
                # Start background task
                asyncio.create_task(
                    self._process_add_to_pipeline_async(
                        payload, user_id, user_name, response_url
                    )
                )
                
                # Return immediate acknowledgment with button update
                # Get the original message blocks and update the clicked button
                original_message = payload.get('message', {})
                updated_blocks = self._update_button_to_processing(
                    original_message.get('blocks', []),
                    payload.get('actions', [{}])[0].get('block_id')
                )
                
                return {
                    "text": "⏳ Processing... Adding article to pipeline",
                    "blocks": updated_blocks,
                    "replace_original": True  # Replace to update button
                }
            else:
                self.logger.warning(f"Unknown action_id: {action_id}")
                return {
                    "text": "❌ Unknown action",
                    "replace_original": False
                }
                
        except Exception as e:
            self.logger.error(f"Error handling interaction: {e}", exc_info=True)
            return {
                "text": f"❌ Error: {str(e)}",
                "replace_original": False
            }
    
    async def _process_add_to_pipeline_async(
        self,
        payload: Dict[str, Any],
        user_id: str,
        user_name: str,
        response_url: str
    ):
        """
        Process "Add to Pipeline" in background and update Slack via response_url
        
        This runs asynchronously after returning immediate response to Slack
        """
        try:
            # Extract article ID
            article_id = payload.get('actions', [{}])[0].get('value')
            
            if not article_id:
                self._send_slack_update(response_url, {
                    "text": "❌ No article ID provided",
                    "replace_original": False
                })
                return
            
            self.logger.info(f"[ASYNC] Processing article: {article_id}")
            
            # Fetch article from Supabase
            article = await self._fetch_article_from_supabase(article_id)
            
            # Log what we got from Supabase
            self.logger.info(f"[ASYNC] Article data keys: {list(article.keys()) if article else 'None'}")
            if article:
                self.logger.info(f"[ASYNC] Has ai_summary_short: {bool(article.get('ai_summary_short'))}")
                self.logger.info(f"[ASYNC] Has key_metrics: {bool(article.get('key_metrics'))}")
                self.logger.info(f"[ASYNC] Has why_it_matters: {bool(article.get('why_it_matters'))}")
            
            if not article:
                self._send_slack_update(response_url, {
                    "text": f"❌ Article not found: {article_id}",
                    "replace_original": False
                })
                return
            
            # Check if already in Airtable
            existing = self.airtable.search_by_supabase_id(article_id)
            if existing:
                self._send_slack_update(response_url, {
                    "text": f"✅ Already in pipeline: *{article['title']}*",
                    "replace_original": False
                })
                return
            
            # Scrape full article text (this is the slow part)
            self.logger.info(f"[ASYNC] Scraping: {article['url']}")
            scrape_result = await self.scraper.scrape_article(article['url'])
            
            # Prepare and push to Airtable
            airtable_data = self._prepare_airtable_data(article, scrape_result)
            record_id = self.airtable.create_article_record(airtable_data)
            
            if record_id:
                self.logger.info(f"[ASYNC] ✓ Added to Airtable: {record_id}")
                
                # Update button to show success
                original_message = payload.get('message', {})
                success_blocks = self._update_button_to_success(
                    original_message.get('blocks', []),
                    payload.get('actions', [{}])[0].get('block_id')
                )
                
                # Send success update with updated button
                self._send_slack_update(response_url, {
                    "text": f"✅ *Added to Pipeline!*\n\n*{article['title']}*\n\n"
                           f"📊 Scraped: {scrape_result.get('word_count', 0):,} words\n"
                           f"🔗 <{article['url']}|View Original>\n"
                           f"📋 Check Airtable: Content Pipeline",
                    "blocks": success_blocks,
                    "replace_original": True
                })
            else:
                self._send_slack_update(response_url, {
                    "text": f"❌ Failed to add to Airtable: {article['title']}",
                    "replace_original": False
                })
                
        except Exception as e:
            self.logger.error(f"[ASYNC] Error: {e}", exc_info=True)
            self._send_slack_update(response_url, {
                "text": f"❌ Error adding to pipeline: {str(e)}",
                "replace_original": False
            })
    
    def _send_slack_update(self, response_url: str, message: Dict[str, Any]):
        """Send update to Slack via response_url"""
        try:
            response = requests.post(response_url, json=message, timeout=5)
            if response.status_code != 200:
                self.logger.error(f"Failed to send Slack update: {response.status_code}")
        except Exception as e:
            self.logger.error(f"Error sending Slack update: {e}")
    
    def _update_button_to_processing(self, blocks: list, clicked_block_id: str) -> list:
        """
        Update the clicked button to show processing state
        
        Args:
            blocks: Original message blocks
            clicked_block_id: ID of the block containing the clicked button
            
        Returns:
            Updated blocks with button changed to processing state
        """
        import copy
        updated_blocks = copy.deepcopy(blocks)
        
        for block in updated_blocks:
            if block.get('block_id') == clicked_block_id and block.get('type') == 'actions':
                # Update the button
                for element in block.get('elements', []):
                    if element.get('action_id') == 'add_to_pipeline':
                        element['text']['text'] = '⏳ Processing...'
                        element['style'] = 'default'  # Change from primary (blue) to default (gray)
                        # Optionally disable the button (though Slack will ignore further clicks anyway)
                break
        
        return updated_blocks
    
    def _update_button_to_success(self, blocks: list, clicked_block_id: str) -> list:
        """
        Update the clicked button to show success state
        
        Args:
            blocks: Original message blocks
            clicked_block_id: ID of the block containing the clicked button
            
        Returns:
            Updated blocks with button changed to success state
        """
        import copy
        updated_blocks = copy.deepcopy(blocks)
        
        for block in updated_blocks:
            if block.get('block_id') == clicked_block_id and block.get('type') == 'actions':
                # Update the button
                for element in block.get('elements', []):
                    if element.get('action_id') == 'add_to_pipeline':
                        element['text']['text'] = '✅ Added'
                        element['style'] = 'primary'  # Keep it blue but show checkmark
                        # Remove action_id so button becomes non-clickable
                        element.pop('action_id', None)
                        element.pop('value', None)
                break
        
        return updated_blocks
    
    async def handle_add_to_pipeline(
        self,
        payload: Dict[str, Any],
        user_id: str,
        user_name: str
    ) -> Dict[str, Any]:
        """
        Handle "Add to Pipeline" button click
        
        Process:
        1. Get article ID from button value
        2. Fetch article from Supabase
        3. Scrape full article text
        4. Push to Airtable
        5. Update button to show success
        
        Args:
            payload: Slack interaction payload
            user_id: Slack user ID
            user_name: Slack username
            
        Returns:
            Response dict for Slack
        """
        try:
            # Extract article ID from button value
            article_id = payload.get('actions', [{}])[0].get('value')
            
            if not article_id:
                return {
                    "text": "❌ No article ID provided",
                    "replace_original": False
                }
            
            self.logger.info(f"Processing 'Add to Pipeline' for article: {article_id}")
            
            # Step 1: Fetch article from Supabase
            article = await self._fetch_article_from_supabase(article_id)
            
            if not article:
                return {
                    "text": f"❌ Article not found: {article_id}",
                    "replace_original": False
                }
            
            # Step 2: Check if already in Airtable
            existing = self.airtable.search_by_supabase_id(article_id)
            if existing:
                return {
                    "text": f"✅ Already in pipeline: *{article['title']}*",
                    "replace_original": False
                }
            
            # Step 3: Scrape full article text
            self.logger.info(f"Scraping full article: {article['url']}")
            scrape_result = await self.scraper.scrape_article(article['url'])
            
            # Step 4: Prepare data for Airtable
            airtable_data = self._prepare_airtable_data(article, scrape_result)
            
            # Step 5: Push to Airtable
            record_id = self.airtable.create_article_record(airtable_data)
            
            if record_id:
                self.logger.info(f"✓ Added to Airtable: {record_id} - {article['title']}")
                
                # Success response
                return {
                    "text": f"✅ *Added to Pipeline!*\n\n*{article['title']}*\n\n"
                           f"📊 Scraped: {scrape_result.get('word_count', 0):,} words\n"
                           f"🔗 <{article['url']}|View Original>\n"
                           f"📋 Check Airtable: Content Pipeline",
                    "replace_original": False
                }
            else:
                return {
                    "text": f"❌ Failed to add to Airtable: {article['title']}",
                    "replace_original": False
                }
                
        except Exception as e:
            self.logger.error(f"Error in handle_add_to_pipeline: {e}", exc_info=True)
            return {
                "text": f"❌ Error adding to pipeline: {str(e)}",
                "replace_original": False
            }
    
    async def _fetch_article_from_supabase(self, article_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch article from Supabase by ID
        
        Args:
            article_id: Article UUID
            
        Returns:
            Article dict or None
        """
        try:
            response = self.supabase.client.table('articles')\
                .select('*')\
                .eq('id', article_id)\
                .execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            
            self.logger.warning(f"Article not found in Supabase: {article_id}")
            return None
            
        except Exception as e:
            self.logger.error(f"Error fetching article from Supabase: {e}")
            return None
    
    def _prepare_airtable_data(
        self,
        article: Dict[str, Any],
        scrape_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Prepare article data for Airtable
        
        Args:
            article: Article from Supabase
            scrape_result: Result from article scraper
            
        Returns:
            Formatted data dict for Airtable
        """
        # Get digest date from article
        digest_date = article.get('week_start_date')
        if not digest_date:
            # Fallback to scraped_at or today
            digest_date = article.get('scraped_at', datetime.now().date().isoformat())
        
        # Format data
        data = {
            'title': article.get('title', 'Untitled'),
            'url': article.get('url', ''),
            'source_name': article.get('source_name', 'Unknown'),
            'digest_date': digest_date,
            'stage': '📥 Saved',
            'priority': '🟡 Medium',
            
            # AI-generated context (from digest)
            'ai_summary_short': article.get('ai_summary_short', ''),
            'ai_summary': article.get('ai_summary', ''),
            'key_metrics': article.get('key_metrics', []),
            'key_quotes': article.get('key_quotes', []),
            'why_it_matters': article.get('why_it_matters', ''),
            'primary_theme': article.get('primary_theme', ''),
            'content_type': article.get('content_type', 'news'),
            
            # Scraped content
            'full_article_text': scrape_result.get('full_text', ''),
            'word_count': scrape_result.get('word_count', 0),
            'author': scrape_result.get('author'),
            
            # Metadata
            'supabase_id': article.get('id', '')
        }
        
        return data

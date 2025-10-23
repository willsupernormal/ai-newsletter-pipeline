"""
Slack notification service for daily digest delivery
Posts formatted daily digests to Slack channels via webhooks
"""
import requests
import logging
from typing import Dict, List, Optional, Any
from datetime import date

logger = logging.getLogger(__name__)

class SlackNotifier:
    """Handles posting daily digests and error notifications to Slack via webhooks"""
    
    def __init__(
        self, 
        webhook_url: Optional[str] = None,
        error_webhook_url: Optional[str] = None,
        enabled: bool = True
    ):
        """
        Initialize Slack notifier
        
        Args:
            webhook_url: Main channel webhook URL for daily digests
            error_webhook_url: Personal/error channel webhook URL for errors
            enabled: Whether Slack notifications are enabled
        """
        self.webhook_url = webhook_url
        self.error_webhook_url = error_webhook_url
        self.enabled = enabled
    
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
        """
        Format daily digest as Slack Block Kit message
        
        Args:
            digest_date: Date of the digest
            summary_text: AI-generated summary
            key_insights: List of key insights
            selected_articles: List of selected article dicts
            total_processed: Total articles processed
            rss_count: Number of RSS articles
            twitter_count: Number of Twitter articles
            
        Returns:
            Slack Block Kit JSON structure
        """
        blocks = []
        
        # Header with date
        blocks.append({
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"🤖 AI Daily Digest - {digest_date.strftime('%B %d, %Y')}"
            }
        })
        
        # Summary section
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*📊 Summary*\n{summary_text}"
            }
        })
        
        # Key insights section
        if key_insights:
            insights_text = "*💡 Key Insights*\n" + "\n".join(
                f"• {insight}" for insight in key_insights
            )
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": insights_text
                }
            })
        
        # Divider before articles
        blocks.append({"type": "divider"})
        
        # Articles header
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*📰 Top 5 Articles*"
            }
        })
        
        # Individual articles
        for idx, article in enumerate(selected_articles[:5], 1):
            # Number emoji mapping
            number_emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
            
            # Get article summary (from AI or excerpt)
            article_summary = article.get('summary', article.get('content_excerpt', ''))
            
            # Truncate summary if too long (Slack has limits)
            if len(article_summary) > 300:
                article_summary = article_summary[:297] + "..."
            
            # Format article block
            article_text = (
                f"*{number_emojis[idx-1]} {article['title']}*\n"
                f"_{article['source_name']}_\n\n"
                f"{article_summary}\n\n"
                f"<{article['url']}|🔗 Read Article>"
            )
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": article_text
                }
            })
            
            # Add divider between articles (except after last one)
            if idx < len(selected_articles[:5]):
                blocks.append({"type": "divider"})
        
        # Stats footer
        sources_text = f"{rss_count} RSS + {twitter_count} Twitter" if rss_count or twitter_count else str(total_processed)
        stats_text = (
            f"📈 *Today's Stats* • "
            f"Articles Processed: {total_processed} ({sources_text}) • "
            f"Selected: {len(selected_articles)}"
        )
        
        blocks.append({
            "type": "context",
            "elements": [{
                "type": "mrkdwn",
                "text": stats_text
            }]
        })
        
        return {"blocks": blocks}
    
    def post_digest(
        self,
        digest_date: date,
        summary_text: str,
        key_insights: List[str],
        selected_articles: List[Dict[str, Any]],
        total_processed: int,
        rss_count: int = 0,
        twitter_count: int = 0
    ) -> bool:
        """
        Post digest to Slack channel
        
        Args:
            digest_date: Date of the digest
            summary_text: AI-generated summary
            key_insights: List of key insights
            selected_articles: List of selected article dicts
            total_processed: Total articles processed
            rss_count: Number of RSS articles
            twitter_count: Number of Twitter articles
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            logger.info("Slack notifications disabled, skipping post")
            return True
        
        if not self.webhook_url:
            logger.warning("Slack webhook URL not configured, skipping post")
            return False
        
        try:
            # Format message
            message = self.format_digest_message(
                digest_date=digest_date,
                summary_text=summary_text,
                key_insights=key_insights,
                selected_articles=selected_articles,
                total_processed=total_processed,
                rss_count=rss_count,
                twitter_count=twitter_count
            )
            
            # Post to Slack
            response = requests.post(
                self.webhook_url,
                json=message,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Posted digest to Slack: {digest_date}")
                return True
            else:
                logger.error(
                    f"❌ Slack post failed: {response.status_code} - {response.text}"
                )
                return False
                
        except Exception as e:
            logger.error(f"❌ Error posting to Slack: {e}")
            return False
    
    def post_error_notification(
        self, 
        error_message: str,
        error_details: Optional[str] = None,
        pipeline_stage: Optional[str] = None
    ) -> bool:
        """
        Post error notification to personal Slack channel/DM
        
        Args:
            error_message: Main error message
            error_details: Additional error details
            pipeline_stage: Which stage of pipeline failed
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            return False
        
        # Use error webhook if available, otherwise fall back to main webhook
        webhook_url = self.error_webhook_url or self.webhook_url
        
        if not webhook_url:
            logger.warning("No Slack webhook configured for error notifications")
            return False
        
        try:
            # Build error message blocks
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "⚠️ AI Pipeline Error"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Error:* {error_message}"
                    }
                }
            ]
            
            # Add pipeline stage if provided
            if pipeline_stage:
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Stage:* {pipeline_stage}"
                    }
                })
            
            # Add error details if provided
            if error_details:
                # Truncate if too long
                if len(error_details) > 500:
                    error_details = error_details[:497] + "..."
                
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Details:*\n```{error_details}```"
                    }
                })
            
            # Add timestamp
            from datetime import datetime
            blocks.append({
                "type": "context",
                "elements": [{
                    "type": "mrkdwn",
                    "text": f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                }]
            })
            
            message = {"blocks": blocks}
            
            # Post to Slack
            response = requests.post(
                webhook_url,
                json=message,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("✅ Posted error notification to Slack")
                return True
            else:
                logger.error(f"Failed to post error to Slack: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to post error notification to Slack: {e}")
            return False
    
    def post_success_notification(
        self,
        digest_date: date,
        articles_count: int,
        total_processed: int
    ) -> bool:
        """
        Post simple success notification (alternative to full digest)
        
        Args:
            digest_date: Date of the digest
            articles_count: Number of articles selected
            total_processed: Total articles processed
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled or not self.webhook_url:
            return False
        
        try:
            message = {
                "blocks": [{
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": (
                            f"✅ *Daily Digest Created*\n"
                            f"Date: {digest_date}\n"
                            f"Selected: {articles_count} articles from {total_processed} total"
                        )
                    }
                }]
            }
            
            response = requests.post(
                self.webhook_url,
                json=message,
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Failed to post success notification: {e}")
            return False

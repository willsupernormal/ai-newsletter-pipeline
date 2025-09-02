"""
Gmail newsletter scraper using IMAP
"""

import asyncio
import logging
import email
import imaplib
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import re
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from email.header import decode_header
import ssl

from config.settings import Settings


class GmailScraper:
    """Gmail newsletter scraper using IMAP"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        self.imap: Optional[imaplib.IMAP4_SSL] = None
    
    async def connect(self) -> bool:
        """Connect to Gmail IMAP server"""
        try:
            self.logger.info("Connecting to Gmail IMAP server")
            
            # Create SSL context
            context = ssl.create_default_context()
            
            # Connect to Gmail
            self.imap = imaplib.IMAP4_SSL(
                self.settings.GMAIL_IMAP_SERVER, 
                self.settings.GMAIL_IMAP_PORT,
                ssl_context=context
            )
            
            # Login
            self.imap.login(self.settings.GMAIL_EMAIL, self.settings.GMAIL_APP_PASSWORD)
            
            self.logger.info("Successfully connected to Gmail")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to Gmail: {e}")
            return False
    
    def disconnect(self) -> None:
        """Disconnect from Gmail"""
        if self.imap:
            try:
                self.imap.logout()
                self.logger.info("Disconnected from Gmail")
            except Exception as e:
                self.logger.warning(f"Error disconnecting from Gmail: {e}")
            finally:
                self.imap = None
    
    def decode_header_value(self, header_value: str) -> str:
        """Decode email header value"""
        try:
            decoded_parts = decode_header(header_value)
            decoded_value = ''
            
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    decoded_value += part.decode(encoding or 'utf-8', errors='ignore')
                else:
                    decoded_value += part
            
            return decoded_value.strip()
        except Exception as e:
            self.logger.warning(f"Failed to decode header: {e}")
            return header_value
    
    def extract_newsletter_content(self, msg: email.message.Message) -> Dict[str, Any]:
        """Extract content from newsletter email"""
        try:
            # Get basic email info
            subject = self.decode_header_value(msg.get('Subject', ''))
            sender = self.decode_header_value(msg.get('From', ''))
            date_header = msg.get('Date', '')
            
            # Parse date
            published_at = None
            if date_header:
                try:
                    published_at = email.utils.parsedate_to_datetime(date_header)
                except Exception as e:
                    self.logger.debug(f"Could not parse date {date_header}: {e}")
            
            # Extract email content
            content = self.extract_email_body(msg)
            
            if not content:
                return None
            
            # Clean and process content
            clean_content = self.clean_newsletter_content(content)
            
            # Extract newsletter metadata
            newsletter_name = self.extract_newsletter_name(sender, subject)
            
            # Extract links and headlines
            headlines = self.extract_headlines_from_content(clean_content)
            
            # Create article entries for each significant headline/section
            articles = []
            
            if headlines:
                # Create separate articles for major headlines
                for headline in headlines[:5]:  # Limit to top 5 headlines
                    article = {
                        'title': f"{newsletter_name}: {headline['title']}",
                        'url': headline.get('url', ''),
                        'content_excerpt': headline.get('content', clean_content[:500]),
                        'source_type': 'gmail_newsletter',
                        'source_name': newsletter_name,
                        'published_at': published_at,
                        'tags': self.extract_tags_from_newsletter(headline['title'], headline.get('content', ''))
                    }
                    articles.append(article)
            else:
                # Create single article for entire newsletter
                article = {
                    'title': f"{newsletter_name}: {subject}",
                    'url': '',  # Newsletters typically don't have single URLs
                    'content_excerpt': clean_content,
                    'source_type': 'gmail_newsletter',
                    'source_name': newsletter_name,
                    'published_at': published_at,
                    'tags': self.extract_tags_from_newsletter(subject, clean_content)
                }
                articles.append(article)
            
            return articles
            
        except Exception as e:
            self.logger.error(f"Failed to extract newsletter content: {e}")
            return []
    
    def extract_email_body(self, msg: email.message.Message) -> str:
        """Extract email body content"""
        content = ""
        
        try:
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    
                    if content_type == "text/plain":
                        charset = part.get_content_charset() or 'utf-8'
                        body = part.get_payload(decode=True)
                        if body:
                            content += body.decode(charset, errors='ignore')
                    
                    elif content_type == "text/html":
                        charset = part.get_content_charset() or 'utf-8'
                        body = part.get_payload(decode=True)
                        if body:
                            html_content = body.decode(charset, errors='ignore')
                            # Convert HTML to text but preserve some structure
                            text_content = self.html_to_text(html_content)
                            if len(text_content) > len(content):  # Use HTML version if it's richer
                                content = text_content
            else:
                # Single part message
                charset = msg.get_content_charset() or 'utf-8'
                content = msg.get_payload(decode=True).decode(charset, errors='ignore')
                
                if msg.get_content_type() == "text/html":
                    content = self.html_to_text(content)
            
        except Exception as e:
            self.logger.warning(f"Error extracting email body: {e}")
        
        return content.strip()
    
    def html_to_text(self, html_content: str) -> str:
        """Convert HTML to readable text while preserving structure"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'footer', 'aside', 'iframe']):
                element.decompose()
            
            # Get text with some structure preservation
            text = soup.get_text(separator='\n', strip=True)
            
            # Clean up excessive whitespace
            text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)  # Max 2 consecutive newlines
            text = re.sub(r' +', ' ', text)  # Multiple spaces to single space
            
            return text
            
        except Exception as e:
            self.logger.warning(f"Failed to convert HTML to text: {e}")
            return html_content
    
    def clean_newsletter_content(self, content: str) -> str:
        """Clean and standardize newsletter content"""
        if not content:
            return ""
        
        # Remove email signatures and unsubscribe footers
        content = re.sub(r'unsubscribe.*$', '', content, flags=re.IGNORECASE | re.MULTILINE)
        content = re.sub(r'manage your.*preferences.*$', '', content, flags=re.IGNORECASE | re.MULTILINE)
        content = re.sub(r'sent to.*@.*$', '', content, flags=re.IGNORECASE | re.MULTILINE)
        
        # Clean up URLs (remove tracking parameters)
        content = re.sub(r'\?utm_[^\\s]+', '', content)
        
        # Truncate if too long
        if len(content) > self.settings.CONTENT_EXCERPT_LENGTH * 2:  # Allow longer excerpts for newsletters
            content = content[:self.settings.CONTENT_EXCERPT_LENGTH * 2] + "..."
        
        return content.strip()
    
    def extract_newsletter_name(self, sender: str, subject: str) -> str:
        """Extract newsletter name from sender or subject"""
        # Common newsletter patterns
        if 'substack' in sender.lower():
            # Extract name before @substack.com
            match = re.search(r'([^<]+).*@([^.]+)\.substack\.com', sender)
            if match:
                return f"{match.group(2).title()} Newsletter"
        
        if 'beehiiv' in sender.lower():
            match = re.search(r'([^<]+)', sender)
            if match:
                return f"{match.group(1).strip()} Newsletter"
        
        # Try to extract from sender name
        sender_match = re.search(r'^([^<]+)', sender)
        if sender_match:
            sender_name = sender_match.group(1).strip().strip('"')
            if sender_name and '@' not in sender_name:
                return sender_name
        
        # Fallback to domain
        domain_match = re.search(r'@([^.]+)\.', sender)
        if domain_match:
            return f"{domain_match.group(1).title()} Newsletter"
        
        return "Unknown Newsletter"
    
    def extract_headlines_from_content(self, content: str) -> List[Dict[str, Any]]:
        """Extract headlines and their content from newsletter"""
        headlines = []
        
        try:
            # Split content into potential sections
            sections = re.split(r'\n\s*\n', content)
            
            for section in sections:
                section = section.strip()
                if len(section) < 50:  # Skip very short sections
                    continue
                
                # Look for headline patterns
                lines = section.split('\n')
                first_line = lines[0].strip()
                
                # Check if first line looks like a headline
                if (len(first_line) < 100 and 
                    len(first_line) > 10 and
                    not first_line.endswith('.') and
                    not first_line.startswith('http')):
                    
                    # Extract URL if present in section
                    url_match = re.search(r'https?://[^\s]+', section)
                    url = url_match.group(0) if url_match else ''
                    
                    headline = {
                        'title': first_line,
                        'content': section[:500],  # First 500 chars of section
                        'url': url
                    }
                    headlines.append(headline)
                    
                    if len(headlines) >= 10:  # Limit headlines
                        break
        
        except Exception as e:
            self.logger.warning(f"Failed to extract headlines: {e}")
        
        return headlines
    
    def extract_tags_from_newsletter(self, title: str, content: str) -> List[str]:
        """Extract relevant tags from newsletter content"""
        tags = set()
        text = (title + " " + content).lower()
        
        # Newsletter-specific keywords
        newsletter_keywords = [
            "newsletter", "weekly", "daily", "digest", "roundup", "recap",
            "briefing", "update", "insight", "analysis", "trend", "report"
        ]
        
        # AI/Tech keywords
        tech_keywords = [
            "ai", "artificial intelligence", "machine learning", "ml", "tech",
            "startup", "funding", "investment", "product", "launch", "feature",
            "api", "platform", "tool", "service", "software", "app"
        ]
        
        # Business keywords
        business_keywords = [
            "business", "strategy", "market", "industry", "company", "revenue",
            "growth", "scale", "enterprise", "b2b", "saas", "customer"
        ]
        
        all_keywords = newsletter_keywords + tech_keywords + business_keywords
        
        for keyword in all_keywords:
            if keyword in text:
                tags.add(keyword.replace(" ", "_"))
        
        # Add newsletter-specific tag
        tags.add("newsletter_content")
        
        return list(tags)[:10]
    
    def search_newsletter_emails(self, hours_back: int = None) -> List[int]:
        """Search for newsletter emails with specified label"""
        if hours_back is None:
            hours_back = self.settings.PROCESS_HOURS_BACK
        
        try:
            # Select the inbox
            self.imap.select('INBOX')
            
            # Calculate date threshold
            since_date = datetime.now() - timedelta(hours=hours_back)
            date_str = since_date.strftime('%d-%b-%Y')
            
            # Search for emails with newsletter label since date
            search_criteria = f'(LABEL "{self.settings.NEWSLETTER_LABEL}" SINCE {date_str})'
            
            self.logger.info(f"Searching for emails with criteria: {search_criteria}")
            
            result, messages = self.imap.search(None, search_criteria)
            
            if result != 'OK':
                self.logger.warning(f"Search failed: {result}")
                return []
            
            message_ids = []
            if messages[0]:
                message_ids = messages[0].split()
            
            self.logger.info(f"Found {len(message_ids)} newsletter emails")
            return [int(msg_id) for msg_id in message_ids]
            
        except Exception as e:
            self.logger.error(f"Failed to search newsletter emails: {e}")
            return []
    
    def fetch_email(self, message_id: int) -> Optional[email.message.Message]:
        """Fetch a specific email message"""
        try:
            result, msg_data = self.imap.fetch(str(message_id), '(RFC822)')
            
            if result != 'OK' or not msg_data:
                return None
            
            # Parse the email
            msg = email.message_from_bytes(msg_data[0][1])
            return msg
            
        except Exception as e:
            self.logger.warning(f"Failed to fetch email {message_id}: {e}")
            return None
    
    async def scrape_newsletters(self) -> List[Dict[str, Any]]:
        """Scrape newsletter emails from Gmail"""
        all_articles = []
        
        try:
            # Connect to Gmail
            if not await self.connect():
                return []
            
            # Search for newsletter emails
            message_ids = self.search_newsletter_emails()
            
            if not message_ids:
                self.logger.info("No newsletter emails found")
                return []
            
            # Limit the number of emails processed
            max_emails = min(len(message_ids), 20)  # Process max 20 emails
            message_ids = message_ids[-max_emails:]  # Get most recent
            
            self.logger.info(f"Processing {len(message_ids)} newsletter emails")
            
            # Process each email
            for i, message_id in enumerate(message_ids):
                try:
                    self.logger.debug(f"Processing email {i+1}/{len(message_ids)}: {message_id}")
                    
                    # Fetch email
                    msg = self.fetch_email(message_id)
                    if not msg:
                        continue
                    
                    # Extract content
                    articles = self.extract_newsletter_content(msg)
                    if articles:
                        all_articles.extend(articles)
                        self.logger.debug(f"Extracted {len(articles)} articles from email {message_id}")
                    
                    # Add small delay between emails
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    self.logger.warning(f"Failed to process email {message_id}: {e}")
                    continue
            
            self.logger.info(f"Gmail scraping completed: {len(all_articles)} articles from newsletters")
            return all_articles
            
        except Exception as e:
            self.logger.error(f"Gmail scraping failed: {e}")
            return []
        
        finally:
            self.disconnect()


# CLI testing
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    async def test_gmail_scraper():
        settings = Settings()
        
        if not all([settings.GMAIL_EMAIL, settings.GMAIL_APP_PASSWORD]):
            print("Gmail credentials not set in environment")
            return
        
        scraper = GmailScraper(settings)
        articles = await scraper.scrape_newsletters()
        
        print(f"Total newsletter articles: {len(articles)}")
        for i, article in enumerate(articles[:2]):  # Show first 2
            print(f"\n--- Article {i+1} ---")
            print(f"Title: {article['title']}")
            print(f"Source: {article['source_name']}")
            print(f"Tags: {article['tags']}")
            print(f"Content: {article['content_excerpt'][:300]}...")
    
    # Run test
    asyncio.run(test_gmail_scraper())
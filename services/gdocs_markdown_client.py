"""
Google Docs Markdown Client
Creates markdown files with YAML frontmatter and uploads to Google Drive
Alternative to Airtable for content storage
"""

import logging
import json
from typing import Optional, Dict, Any, List
from datetime import date, datetime
from io import BytesIO

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

from config.settings import Settings


class GoogleDocsMarkdownClient:
    """Client for creating markdown files with YAML frontmatter and uploading to Google Drive"""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)

        if not settings.GOOGLE_SERVICE_ACCOUNT_KEY:
            raise ValueError("GOOGLE_SERVICE_ACCOUNT_KEY not configured")

        if not settings.MARKDOWN_CONTENT_FOLDER_ID:
            self.logger.warning("MARKDOWN_CONTENT_FOLDER_ID not configured - will use root folder")

        # Initialize Google Drive API
        self.drive_service = self._init_drive_service()

    def _init_drive_service(self):
        """Initialize Google Drive API service"""
        try:
            # Parse service account credentials
            credentials_dict = json.loads(self.settings.GOOGLE_SERVICE_ACCOUNT_KEY)

            credentials = service_account.Credentials.from_service_account_info(
                credentials_dict,
                scopes=['https://www.googleapis.com/auth/drive.file']
            )

            service = build('drive', 'v3', credentials=credentials)
            self.logger.info("✓ Google Drive service initialized")
            return service

        except Exception as e:
            self.logger.error(f"Failed to initialize Google Drive service: {e}")
            raise

    def create_markdown_file(self, article_data: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """
        Create markdown file with YAML frontmatter and upload to Google Drive

        Args:
            article_data: Article data dictionary with all fields

        Returns:
            Dict with file_id and web_view_link if successful, None otherwise
        """
        try:
            # Generate filename
            filename = self._generate_filename(article_data)

            # Generate markdown content with YAML frontmatter
            markdown_content = self._format_markdown(article_data)

            # Upload to Google Drive
            file_info = self._upload_to_drive(filename, markdown_content)

            if file_info:
                self.logger.info(f"✓ Created markdown file: {filename}")
                self.logger.info(f"  File ID: {file_info['file_id']}")
                self.logger.info(f"  URL: {file_info['web_view_link']}")

            return file_info

        except Exception as e:
            self.logger.error(f"Failed to create markdown file: {e}")
            return None

    def _generate_filename(self, article_data: Dict[str, Any]) -> str:
        """Generate filename from article data"""
        # Get date
        article_date = article_data.get('digest_date', date.today())
        if isinstance(article_date, (date, datetime)):
            date_str = article_date.strftime('%Y-%m-%d')
        else:
            date_str = str(article_date)

        # Get title and slugify
        title = article_data.get('title', 'untitled')
        slug = self._slugify(title)

        return f"{date_str}-{slug}.md"

    def _slugify(self, text: str, max_length: int = 50) -> str:
        """Convert text to URL-friendly slug"""
        import re

        # Convert to lowercase
        text = text.lower()

        # Remove special characters
        text = re.sub(r'[^a-z0-9\s-]', '', text)

        # Replace spaces with hyphens
        text = re.sub(r'\s+', '-', text)

        # Remove consecutive hyphens
        text = re.sub(r'-+', '-', text)

        # Trim hyphens from ends
        text = text.strip('-')

        # Limit length
        if len(text) > max_length:
            text = text[:max_length].rsplit('-', 1)[0]

        return text or 'article'

    def _format_markdown(self, article_data: Dict[str, Any]) -> str:
        """Format article data as markdown with YAML frontmatter"""
        lines = []

        # YAML frontmatter
        lines.append("---")
        lines.append("# Article Metadata")
        lines.append("")

        # Basic fields
        if 'title' in article_data:
            lines.append(f"title: \"{self._escape_yaml(article_data['title'])}\"")

        if 'url' in article_data:
            lines.append(f"url: \"{article_data['url']}\"")

        if 'source_name' in article_data:
            lines.append(f"source: \"{article_data['source_name']}\"")

        # Dates
        if 'digest_date' in article_data:
            date_val = article_data['digest_date']
            if isinstance(date_val, (date, datetime)):
                lines.append(f"date: \"{date_val.isoformat()}\"")
            else:
                lines.append(f"date: \"{date_val}\"")

        if 'supabase_id' in article_data:
            lines.append(f"supabase_id: \"{article_data['supabase_id']}\"")

        lines.append("")
        lines.append("# User-Selected Metadata (from Slack modal)")

        if 'theme' in article_data and article_data['theme']:
            lines.append(f"theme: \"{article_data['theme']}\"")

        if 'content_type' in article_data and article_data['content_type']:
            lines.append(f"content_type: \"{article_data['content_type']}\"")

        if 'your_angle' in article_data and article_data['your_angle']:
            lines.append(f"your_angle: \"{self._escape_yaml(article_data['your_angle'])}\"")

        lines.append("")
        lines.append("# AI-Generated Fields")

        if 'detailed_summary' in article_data and article_data['detailed_summary']:
            lines.append(f"detailed_summary: \"{self._escape_yaml(article_data['detailed_summary'])}\"")

        if 'business_impact' in article_data and article_data['business_impact']:
            lines.append(f"business_impact: \"{self._escape_yaml(article_data['business_impact'])}\"")

        if 'companies_mentioned' in article_data and article_data['companies_mentioned']:
            companies = article_data['companies_mentioned']
            if isinstance(companies, list):
                lines.append(f"companies_mentioned: {json.dumps(companies)}")
            else:
                lines.append(f"companies_mentioned: \"{companies}\"")

        lines.append("")
        lines.append("# Article Metadata")

        if 'word_count' in article_data:
            lines.append(f"word_count: {article_data['word_count']}")

        if 'author' in article_data and article_data['author']:
            lines.append(f"author: \"{self._escape_yaml(article_data['author'])}\"")

        lines.append(f"stage: \"{article_data.get('stage', '📥 Saved')}\"")
        lines.append(f"priority: \"{article_data.get('priority', '🟡 Medium')}\"")

        lines.append("")
        lines.append("# Tags for Claude Code Querying")

        # Generate tags from theme and content type
        tags = []
        if 'theme' in article_data and article_data['theme']:
            tags.append(self._slugify(article_data['theme']))
        if 'content_type' in article_data and article_data['content_type']:
            tags.append(self._slugify(article_data['content_type']))

        if tags:
            lines.append(f"tags: {json.dumps(tags)}")

        lines.append("---")
        lines.append("")

        # Markdown body
        title = article_data.get('title', 'Untitled Article')
        lines.append(f"# {title}")
        lines.append("")

        # Summary section
        if 'detailed_summary' in article_data and article_data['detailed_summary']:
            lines.append("## Summary")
            lines.append("")
            lines.append(article_data['detailed_summary'])
            lines.append("")

        # Business Impact section
        if 'business_impact' in article_data and article_data['business_impact']:
            lines.append("## Business Impact")
            lines.append("")
            lines.append(article_data['business_impact'])
            lines.append("")

        # Key Quotes section
        if 'key_quotes' in article_data and article_data['key_quotes']:
            lines.append("## Key Quotes")
            lines.append("")
            quotes_text = self._format_quotes(article_data['key_quotes'])
            if quotes_text:
                lines.append(quotes_text)
                lines.append("")

        # Specific Data section
        if 'specific_data' in article_data and article_data['specific_data']:
            lines.append("## Specific Data")
            lines.append("")
            data_text = self._format_metrics(article_data['specific_data'])
            if data_text:
                lines.append(data_text)
                lines.append("")

        # Companies Mentioned section
        if 'companies_mentioned' in article_data and article_data['companies_mentioned']:
            lines.append("## Companies Mentioned")
            lines.append("")
            companies = article_data['companies_mentioned']
            if isinstance(companies, list):
                for company in companies:
                    lines.append(f"- {company}")
            else:
                lines.append(str(companies))
            lines.append("")

        # User's Angle section
        if 'your_angle' in article_data and article_data['your_angle']:
            lines.append("## Your Angle")
            lines.append("")
            lines.append(article_data['your_angle'])
            lines.append("")

        # Full Article section
        lines.append("---")
        lines.append("")
        lines.append("## Full Article Text")
        lines.append("")

        if 'full_article_text' in article_data:
            lines.append(article_data['full_article_text'])
        else:
            lines.append("*(Full article text not available)*")

        lines.append("")
        lines.append("---")
        lines.append("")

        # Footer metadata
        lines.append("**Metadata:**")
        if 'word_count' in article_data:
            lines.append(f"- Word Count: {article_data['word_count']}")
        if 'author' in article_data and article_data['author']:
            lines.append(f"- Author: {article_data['author']}")
        if 'source_name' in article_data:
            lines.append(f"- Source: {article_data['source_name']}")
        if 'url' in article_data:
            lines.append(f"- URL: {article_data['url']}")

        return "\n".join(lines)

    def _escape_yaml(self, text: str) -> str:
        """Escape special characters for YAML"""
        if not text:
            return ""

        # Escape double quotes
        text = text.replace('"', '\\"')

        # Escape newlines
        text = text.replace('\n', '\\n')

        return text

    def _format_quotes(self, quotes: Any) -> str:
        """Format quotes list as readable markdown"""
        if not quotes:
            return ""

        # Handle if quotes is not a list
        if not isinstance(quotes, list):
            return ""

        lines = []
        for i, quote in enumerate(quotes, 1):
            # Skip if quote is not a dict
            if not isinstance(quote, dict):
                continue

            quote_text = quote.get('quote', '')
            speaker = quote.get('speaker', '')
            context = quote.get('context', '')

            lines.append(f"{i}. \"{quote_text}\"")
            if speaker:
                lines.append(f"   - *{speaker}*")
            if context:
                lines.append(f"   - Context: {context}")
            lines.append("")

        return "\n".join(lines)

    def _format_metrics(self, metrics: Any) -> str:
        """Format metrics list as readable markdown"""
        if not metrics:
            return ""

        # Handle if metrics is not a list
        if not isinstance(metrics, list):
            return ""

        lines = []
        for i, metric in enumerate(metrics, 1):
            # Skip if metric is not a dict
            if not isinstance(metric, dict):
                continue

            metric_name = metric.get('metric', 'Metric')
            value = metric.get('value', 'N/A')
            context = metric.get('context', '')

            lines.append(f"{i}. **{metric_name}:** {value}")
            if context:
                lines.append(f"   - Context: {context}")
            lines.append("")

        return "\n".join(lines)

    def _upload_to_drive(self, filename: str, content: str) -> Optional[Dict[str, str]]:
        """Upload markdown file to Google Drive"""
        try:
            # Convert string to bytes
            file_bytes = content.encode('utf-8')

            # Create file metadata
            file_metadata = {
                'name': filename,
                'mimeType': 'text/markdown'
            }

            # Add parent folder if configured
            if self.settings.MARKDOWN_CONTENT_FOLDER_ID:
                file_metadata['parents'] = [self.settings.MARKDOWN_CONTENT_FOLDER_ID]

            # Create media upload
            media = MediaIoBaseUpload(
                BytesIO(file_bytes),
                mimetype='text/markdown',
                resumable=True
            )

            # Upload file
            file = self.drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, webViewLink',
                supportsAllDrives=True
            ).execute()

            return {
                'file_id': file.get('id'),
                'file_name': file.get('name'),
                'web_view_link': file.get('webViewLink')
            }

        except Exception as e:
            self.logger.error(f"Failed to upload to Google Drive: {e}")
            return None

    def search_by_supabase_id(self, supabase_id: str) -> Optional[Dict[str, Any]]:
        """
        Search for markdown file by Supabase ID (in YAML frontmatter)

        Args:
            supabase_id: Supabase article ID

        Returns:
            File info dict if found, None otherwise
        """
        try:
            # Search for files containing the supabase_id in content
            query = f"fullText contains 'supabase_id: \"{supabase_id}\"'"

            if self.settings.MARKDOWN_CONTENT_FOLDER_ID:
                query += f" and '{self.settings.MARKDOWN_CONTENT_FOLDER_ID}' in parents"

            response = self.drive_service.files().list(
                q=query,
                fields='files(id, name, webViewLink)',
                supportsAllDrives=True,
                includeItemsFromAllDrives=True
            ).execute()

            files = response.get('files', [])

            if files:
                return files[0]
            return None

        except Exception as e:
            self.logger.error(f"Failed to search by Supabase ID: {e}")
            return None

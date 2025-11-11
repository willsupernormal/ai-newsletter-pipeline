"""
Airtable integration for Content Pipeline
Handles creating and updating records in Airtable base
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import date, datetime
from pyairtable import Api
from pyairtable.formulas import match

from config.settings import Settings


class AirtableClient:
    """Client for interacting with Airtable Content Pipeline"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        
        if not settings.AIRTABLE_API_KEY or not settings.AIRTABLE_BASE_ID:
            raise ValueError("Airtable credentials not configured")
        
        self.api = Api(settings.AIRTABLE_API_KEY)
        self.table = self.api.table(
            settings.AIRTABLE_BASE_ID,
            settings.AIRTABLE_TABLE_NAME
        )
    
    def create_article_record(self, article_data: Dict[str, Any]) -> Optional[str]:
        """
        Create new article record in Airtable
        
        Args:
            article_data: Article data dictionary
            
        Returns:
            Record ID if successful, None otherwise
        """
        try:
            # Check if article already exists (by URL)
            existing = self.search_by_url(article_data.get('url'))
            if existing:
                self.logger.info(f"Article already exists in Airtable: {article_data.get('title')}")
                return existing['id']
            
            # Format data for Airtable
            fields = self._format_article_fields(article_data)
            
            # Create record
            record = self.table.create(fields)
            
            self.logger.info(f"✓ Created Airtable record: {record['id']} - {article_data.get('title')}")
            return record['id']
            
        except Exception as e:
            self.logger.error(f"Failed to create Airtable record: {e}")
            return None
    
    def update_article_record(self, record_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update existing article record
        
        Args:
            record_id: Airtable record ID
            updates: Fields to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.table.update(record_id, updates)
            self.logger.info(f"✓ Updated Airtable record: {record_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update Airtable record {record_id}: {e}")
            return False
    
    def search_by_url(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Search for article by URL

        Args:
            url: Article URL

        Returns:
            Record dict if found, None otherwise
        """
        try:
            formula = match({"URL": url})  # Updated to match new field name
            records = self.table.all(formula=formula)

            if records:
                return records[0]
            return None

        except Exception as e:
            self.logger.error(f"Failed to search Airtable by URL: {e}")
            return None
    
    def search_by_supabase_id(self, supabase_id: str) -> Optional[Dict[str, Any]]:
        """
        Search for article by Supabase ID
        
        Args:
            supabase_id: Supabase article ID
            
        Returns:
            Record dict if found, None otherwise
        """
        try:
            formula = match({"Supabase ID": supabase_id})
            records = self.table.all(formula=formula)
            
            if records:
                return records[0]
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to search Airtable by Supabase ID: {e}")
            return None
    
    def _format_article_fields(self, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format article data for Airtable fields (NEW LEAN SCHEMA)

        Args:
            article_data: Raw article data

        Returns:
            Formatted fields dict with 16 fields (no bloat)
        """
        fields = {}

        # === CORE FIELDS (6) ===

        # Title
        if 'title' in article_data:
            fields['Title'] = article_data['title']

        # URL (renamed from "Original URL")
        if 'url' in article_data:
            fields['URL'] = article_data['url']

        # Source
        if 'source_name' in article_data:
            fields['Source'] = article_data['source_name']

        # Stage - NEW default is "💡 Ideation"
        fields['Stage'] = article_data.get('stage', '💡 Ideation')

        # Theme (user-selected overrides AI-detected)
        if 'theme' in article_data and article_data['theme']:
            fields['Theme'] = article_data['theme']
        elif 'primary_theme' in article_data and article_data['primary_theme']:
            fields['Theme'] = article_data['primary_theme']

        # Content Type
        if 'content_type' in article_data and article_data['content_type']:
            fields['Content Type'] = article_data['content_type']

        # === WORKFLOW FIELDS (5) ===

        # Your Angle
        if 'your_angle' in article_data and article_data['your_angle']:
            fields['Your Angle'] = article_data['your_angle']

        # Google Doc Link (empty for now - Phase 3)
        if 'google_doc_link' in article_data and article_data['google_doc_link']:
            fields['Google Doc Link'] = article_data['google_doc_link']

        # Webflow URL (empty for now - Phase 2)
        if 'webflow_url' in article_data and article_data['webflow_url']:
            fields['Webflow URL'] = article_data['webflow_url']

        # Twitter URL (empty for now - Phase 2)
        if 'twitter_url' in article_data and article_data['twitter_url']:
            fields['Twitter URL'] = article_data['twitter_url']

        # LinkedIn URL (empty for now - Phase 2)
        if 'linkedin_url' in article_data and article_data['linkedin_url']:
            fields['LinkedIn URL'] = article_data['linkedin_url']

        # === METADATA FIELDS (5) ===

        # Date Created - AUTO FIELD (Airtable handles this, no code needed)

        # Scheduled Publish Date (empty for now - Phase 3)
        if 'scheduled_publish_date' in article_data and article_data['scheduled_publish_date']:
            fields['Scheduled Publish Date'] = article_data['scheduled_publish_date']

        # Published Date (empty for now - Phase 2)
        if 'published_date' in article_data and article_data['published_date']:
            fields['Published Date'] = article_data['published_date']

        # AI Summary - One sentence from detailed_summary for Kanban preview
        if 'detailed_summary' in article_data and article_data['detailed_summary']:
            summary = article_data['detailed_summary']
            # Extract first sentence (split on period)
            first_sentence = summary.split('.')[0] + '.' if '.' in summary else summary
            # Truncate if too long
            if len(first_sentence) > 200:
                first_sentence = summary[:197] + '...'
            fields['AI Summary'] = first_sentence
        elif 'ai_summary_short' in article_data and article_data['ai_summary_short']:
            # Fallback to ai_summary_short if available
            fields['AI Summary'] = article_data['ai_summary_short']

        # Supabase ID for linking
        if 'supabase_id' in article_data:
            fields['Supabase ID'] = article_data['supabase_id']

        return fields

    def get_recent_articles(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent articles from Airtable
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of article records
        """
        try:
            records = self.table.all(
                max_records=limit,
                sort=["-Digest Date"]
            )
            return records
            
        except Exception as e:
            self.logger.error(f"Failed to get recent articles: {e}")
            return []

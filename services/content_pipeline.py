"""
Content Pipeline Orchestrator
Routes article content to Airtable, Markdown, or Both based on configuration
Allows easy switching between output modes without code changes
"""

import logging
from typing import Dict, Any, Optional
import asyncio

from config.settings import Settings
from services.airtable_client import AirtableClient
from services.gdocs_markdown_client import GoogleDocsMarkdownClient


class ContentPipelineHandler:
    """
    Orchestrates content output to multiple destinations
    Supports: Airtable, Markdown (Google Drive), or Both
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)

        # Initialize clients
        self.airtable = AirtableClient(settings)

        # Initialize markdown client (may fail if not configured, that's OK)
        try:
            self.markdown = GoogleDocsMarkdownClient(settings)
            self.markdown_available = True
        except Exception as e:
            self.logger.warning(f"Markdown client not available: {e}")
            self.markdown_available = False

        # Get output mode from settings
        self.output_mode = getattr(settings, 'CONTENT_OUTPUT_MODE', 'airtable').lower()

        self.logger.info(f"Content Pipeline initialized with mode: {self.output_mode}")

    async def save_article(self, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save article to configured destination(s)

        Args:
            article_data: Article data dictionary with all fields

        Returns:
            Dict with results from each destination
            {
                'mode': 'airtable|markdown|both',
                'airtable': {'success': bool, 'record_id': str},
                'markdown': {'success': bool, 'file_id': str, 'web_view_link': str},
                'success': bool  # Overall success
            }
        """
        result = {
            'mode': self.output_mode,
            'success': False
        }

        try:
            if self.output_mode == 'airtable':
                # Airtable only
                airtable_result = await self._save_to_airtable(article_data)
                result['airtable'] = airtable_result
                result['success'] = airtable_result.get('success', False)

            elif self.output_mode == 'markdown':
                # Markdown only
                if not self.markdown_available:
                    raise ValueError("Markdown output requested but not configured")

                markdown_result = await self._save_to_markdown(article_data)
                result['markdown'] = markdown_result
                result['success'] = markdown_result.get('success', False)

            elif self.output_mode == 'both':
                # Both destinations
                airtable_task = self._save_to_airtable(article_data)
                markdown_task = self._save_to_markdown(article_data) if self.markdown_available else None

                # Run in parallel
                if markdown_task:
                    airtable_result, markdown_result = await asyncio.gather(
                        airtable_task,
                        markdown_task,
                        return_exceptions=True
                    )

                    result['airtable'] = airtable_result if not isinstance(airtable_result, Exception) else {'success': False, 'error': str(airtable_result)}
                    result['markdown'] = markdown_result if not isinstance(markdown_result, Exception) else {'success': False, 'error': str(markdown_result)}

                    # Success if at least one succeeded
                    result['success'] = (
                        result['airtable'].get('success', False) or
                        result['markdown'].get('success', False)
                    )
                else:
                    # Markdown not available, just do Airtable
                    airtable_result = await airtable_task
                    result['airtable'] = airtable_result
                    result['success'] = airtable_result.get('success', False)
                    self.logger.warning("'both' mode requested but markdown not available, using Airtable only")

            else:
                raise ValueError(f"Unknown output mode: {self.output_mode}")

            return result

        except Exception as e:
            self.logger.error(f"Failed to save article: {e}")
            result['error'] = str(e)
            return result

    async def _save_to_airtable(self, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save article to Airtable"""
        try:
            record_id = self.airtable.create_article_record(article_data)

            if record_id:
                self.logger.info(f"✓ Saved to Airtable: {record_id}")
                return {
                    'success': True,
                    'record_id': record_id,
                    'destination': 'airtable'
                }
            else:
                self.logger.error("Failed to save to Airtable (no record ID)")
                return {
                    'success': False,
                    'error': 'No record ID returned',
                    'destination': 'airtable'
                }

        except Exception as e:
            self.logger.error(f"Error saving to Airtable: {e}")
            return {
                'success': False,
                'error': str(e),
                'destination': 'airtable'
            }

    async def _save_to_markdown(self, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save article as markdown file to Google Drive"""
        try:
            file_info = self.markdown.create_markdown_file(article_data)

            if file_info:
                self.logger.info(f"✓ Saved to Google Drive: {file_info['file_name']}")
                return {
                    'success': True,
                    'file_id': file_info['file_id'],
                    'file_name': file_info['file_name'],
                    'web_view_link': file_info['web_view_link'],
                    'destination': 'markdown'
                }
            else:
                self.logger.error("Failed to save to Google Drive (no file info)")
                return {
                    'success': False,
                    'error': 'No file info returned',
                    'destination': 'markdown'
                }

        except Exception as e:
            self.logger.error(f"Error saving to Google Drive: {e}")
            return {
                'success': False,
                'error': str(e),
                'destination': 'markdown'
            }

    def get_output_mode(self) -> str:
        """Get current output mode"""
        return self.output_mode

    def set_output_mode(self, mode: str):
        """
        Change output mode dynamically

        Args:
            mode: One of 'airtable', 'markdown', 'both'
        """
        valid_modes = ['airtable', 'markdown', 'both']
        mode = mode.lower()

        if mode not in valid_modes:
            raise ValueError(f"Invalid mode: {mode}. Must be one of {valid_modes}")

        if mode in ['markdown', 'both'] and not self.markdown_available:
            raise ValueError(f"Cannot set mode to '{mode}': Markdown client not available")

        self.output_mode = mode
        self.logger.info(f"Output mode changed to: {mode}")

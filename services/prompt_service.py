"""
AI Prompt Service for dynamic prompt management
Retrieves prompts from Supabase database with caching
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from config.settings import Settings
from database.supabase_simple import SimpleSupabaseClient


@dataclass
class AIPrompt:
    """Data class for AI prompt"""
    id: str
    name: str
    category: str
    prompt_text: str
    description: Optional[str]
    active: bool
    version: int
    created_at: datetime
    updated_at: datetime


class PromptService:
    """Service for managing AI prompts from Supabase database"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.db_client = SimpleSupabaseClient(settings)
        self.logger = logging.getLogger(__name__)
        
        # Simple in-memory cache
        self._cache: Dict[str, AIPrompt] = {}
        self._cache_timestamp: Optional[datetime] = None
        self._cache_ttl = timedelta(minutes=5)  # Cache for 5 minutes
    
    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid"""
        if self._cache_timestamp is None:
            return False
        return datetime.now() - self._cache_timestamp < self._cache_ttl
    
    async def _refresh_cache(self) -> None:
        """Refresh the prompt cache from database"""
        try:
            response = self.db_client.client.table('ai_prompts')\
                .select('*')\
                .eq('active', True)\
                .execute()
            
            if response.data:
                self._cache = {}
                for prompt_data in response.data:
                    prompt = AIPrompt(
                        id=prompt_data['id'],
                        name=prompt_data['name'],
                        category=prompt_data['category'],
                        prompt_text=prompt_data['prompt_text'],
                        description=prompt_data.get('description'),
                        active=prompt_data['active'],
                        version=prompt_data['version'],
                        created_at=datetime.fromisoformat(prompt_data['created_at'].replace('Z', '+00:00')),
                        updated_at=datetime.fromisoformat(prompt_data['updated_at'].replace('Z', '+00:00'))
                    )
                    self._cache[prompt.name] = prompt
                
                self._cache_timestamp = datetime.now()
                self.logger.info(f"Refreshed prompt cache with {len(self._cache)} prompts")
            else:
                self.logger.warning("No active prompts found in database")
                
        except Exception as e:
            self.logger.error(f"Failed to refresh prompt cache: {e}")
            raise
    
    async def get_prompt(self, name: str) -> Optional[AIPrompt]:
        """Get a specific prompt by name"""
        # Refresh cache if needed
        if not self._is_cache_valid():
            await self._refresh_cache()
        
        prompt = self._cache.get(name)
        if prompt is None:
            self.logger.warning(f"Prompt '{name}' not found in cache")
        
        return prompt
    
    async def get_prompt_text(self, name: str) -> Optional[str]:
        """Get prompt text by name (convenience method)"""
        prompt = await self.get_prompt(name)
        return prompt.prompt_text if prompt else None
    
    async def get_prompts_by_category(self, category: str) -> List[AIPrompt]:
        """Get all prompts in a specific category"""
        # Refresh cache if needed
        if not self._is_cache_valid():
            await self._refresh_cache()
        
        return [prompt for prompt in self._cache.values() if prompt.category == category]
    
    async def list_all_prompts(self) -> List[AIPrompt]:
        """Get all active prompts"""
        # Refresh cache if needed
        if not self._is_cache_valid():
            await self._refresh_cache()
        
        return list(self._cache.values())
    
    async def create_prompt(self, name: str, category: str, prompt_text: str, 
                          description: Optional[str] = None) -> AIPrompt:
        """Create a new prompt"""
        try:
            prompt_data = {
                'name': name,
                'category': category,
                'prompt_text': prompt_text,
                'description': description,
                'active': True,
                'version': 1
            }
            
            response = self.db_client.client.table('ai_prompts')\
                .insert(prompt_data)\
                .execute()
            
            if response.data:
                # Invalidate cache to force refresh
                self._cache_timestamp = None
                self.logger.info(f"Created new prompt: {name}")
                
                # Return the created prompt
                created_data = response.data[0]
                return AIPrompt(
                    id=created_data['id'],
                    name=created_data['name'],
                    category=created_data['category'],
                    prompt_text=created_data['prompt_text'],
                    description=created_data.get('description'),
                    active=created_data['active'],
                    version=created_data['version'],
                    created_at=datetime.fromisoformat(created_data['created_at'].replace('Z', '+00:00')),
                    updated_at=datetime.fromisoformat(created_data['updated_at'].replace('Z', '+00:00'))
                )
            else:
                raise Exception("No data returned from insert operation")
                
        except Exception as e:
            self.logger.error(f"Failed to create prompt '{name}': {e}")
            raise
    
    async def update_prompt(self, name: str, prompt_text: Optional[str] = None, 
                          description: Optional[str] = None, active: Optional[bool] = None) -> bool:
        """Update an existing prompt"""
        try:
            update_data = {}
            if prompt_text is not None:
                update_data['prompt_text'] = prompt_text
            if description is not None:
                update_data['description'] = description
            if active is not None:
                update_data['active'] = active
            
            if not update_data:
                self.logger.warning(f"No updates provided for prompt '{name}'")
                return False
            
            response = self.db_client.client.table('ai_prompts')\
                .update(update_data)\
                .eq('name', name)\
                .execute()
            
            if response.data:
                # Invalidate cache to force refresh
                self._cache_timestamp = None
                self.logger.info(f"Updated prompt: {name}")
                return True
            else:
                self.logger.warning(f"No prompt found with name '{name}' to update")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to update prompt '{name}': {e}")
            raise
    
    async def deactivate_prompt(self, name: str) -> bool:
        """Deactivate a prompt (soft delete)"""
        return await self.update_prompt(name, active=False)
    
    async def activate_prompt(self, name: str) -> bool:
        """Activate a prompt"""
        return await self.update_prompt(name, active=True)
    
    def format_prompt(self, prompt_text: str, **kwargs) -> str:
        """Format a prompt with provided variables"""
        try:
            return prompt_text.format(**kwargs)
        except KeyError as e:
            self.logger.error(f"Missing variable for prompt formatting: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error formatting prompt: {e}")
            raise
    
    async def get_formatted_prompt(self, name: str, **kwargs) -> Optional[str]:
        """Get and format a prompt in one call"""
        prompt_text = await self.get_prompt_text(name)
        if prompt_text is None:
            return None
        
        return self.format_prompt(prompt_text, **kwargs)
    
    def clear_cache(self) -> None:
        """Clear the prompt cache (useful for testing)"""
        self._cache.clear()
        self._cache_timestamp = None
        self.logger.info("Prompt cache cleared")


# Convenience function for easy access
_prompt_service_instance: Optional[PromptService] = None

def get_prompt_service(settings: Settings) -> PromptService:
    """Get singleton instance of PromptService"""
    global _prompt_service_instance
    if _prompt_service_instance is None:
        _prompt_service_instance = PromptService(settings)
    return _prompt_service_instance


# CLI testing
if __name__ == "__main__":
    import asyncio
    from dotenv import load_dotenv
    
    load_dotenv()
    
    async def test_prompt_service():
        settings = Settings()
        service = PromptService(settings)
        
        # Test getting all prompts
        prompts = await service.list_all_prompts()
        print(f"Found {len(prompts)} active prompts:")
        
        for prompt in prompts:
            print(f"  - {prompt.name} ({prompt.category})")
        
        # Test getting specific prompt
        ai_scoring = await service.get_prompt('ai_scoring_prompt')
        if ai_scoring:
            print(f"\nAI Scoring Prompt:")
            print(f"  Category: {ai_scoring.category}")
            print(f"  Description: {ai_scoring.description}")
            print(f"  Text length: {len(ai_scoring.prompt_text)} characters")
        
        # Test formatting
        if ai_scoring:
            formatted = service.format_prompt(
                ai_scoring.prompt_text,
                title="Test Article",
                content_excerpt="This is a test article about AI...",
                source_name="Test Source"
            )
            print(f"\nFormatted prompt length: {len(formatted)} characters")
    
    # Run test
    asyncio.run(test_prompt_service())

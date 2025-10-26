"""Debug script to check settings"""
from config.settings import Settings

settings = Settings()

print("=== Airtable Settings ===")
print(f"AIRTABLE_API_KEY: {settings.AIRTABLE_API_KEY[:20] if settings.AIRTABLE_API_KEY else 'NOT SET'}...")
print(f"AIRTABLE_BASE_ID: {settings.AIRTABLE_BASE_ID}")
print(f"AIRTABLE_TABLE_NAME: {settings.AIRTABLE_TABLE_NAME}")

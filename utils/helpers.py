"""
Utility helper functions
"""

import asyncio
import hashlib
import re
from datetime import datetime, date, timedelta
from typing import Any, Dict, List, Optional, Union, Callable, Awaitable
from urllib.parse import urlparse, urljoin
import json
from pathlib import Path


def normalize_text(text: str) -> str:
    """Normalize text for comparison and processing"""
    if not text:
        return ""
    
    # Convert to lowercase
    normalized = text.lower()
    
    # Remove extra whitespace
    normalized = ' '.join(normalized.split())
    
    # Remove common punctuation for comparison
    normalized = re.sub(r'[^\w\s-]', '', normalized)
    
    return normalized.strip()


def extract_domain(url: str) -> str:
    """Extract domain from URL"""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Remove www prefix
        if domain.startswith('www.'):
            domain = domain[4:]
        
        return domain
    except Exception:
        return ""


def calculate_text_hash(text: str) -> str:
    """Calculate MD5 hash of normalized text"""
    normalized = normalize_text(text)
    return hashlib.md5(normalized.encode()).hexdigest()


def safe_get_nested(data: Dict[str, Any], keys: List[str], default: Any = None) -> Any:
    """Safely get nested dictionary values"""
    current = data
    
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    
    return current


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to maximum length"""
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def clean_filename(filename: str) -> str:
    """Clean filename for safe file system usage"""
    # Remove invalid characters
    cleaned = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove excessive underscores
    cleaned = re.sub(r'_+', '_', cleaned)
    
    # Trim and remove leading/trailing underscores
    cleaned = cleaned.strip('_')
    
    # Limit length
    if len(cleaned) > 200:
        name, ext = Path(cleaned).stem, Path(cleaned).suffix
        max_name_length = 200 - len(ext)
        cleaned = name[:max_name_length] + ext
    
    return cleaned


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human-readable string"""
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{minutes:.0f}m {remaining_seconds:.0f}s"
    else:
        hours = seconds // 3600
        remaining_minutes = (seconds % 3600) // 60
        return f"{hours:.0f}h {remaining_minutes:.0f}m"


def format_file_size(bytes_size: int) -> str:
    """Format file size in bytes to human-readable string"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    
    return f"{bytes_size:.1f} TB"


def parse_date_flexible(date_str: str) -> Optional[datetime]:
    """Parse date string with multiple format attempts"""
    if not date_str:
        return None
    
    formats = [
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M:%SZ',
        '%Y-%m-%dT%H:%M:%S.%fZ',
        '%a, %d %b %Y %H:%M:%S %z',
        '%a, %d %b %Y %H:%M:%S GMT',
        '%d %b %Y %H:%M:%S',
        '%Y-%m-%d',
        '%d/%m/%Y',
        '%m/%d/%Y'
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    
    # Try with dateutil as fallback
    try:
        from dateutil import parser
        return parser.parse(date_str)
    except Exception:
        return None


def get_week_boundaries(target_date: Optional[date] = None) -> tuple[date, date]:
    """Get start and end dates for the week containing target_date"""
    if target_date is None:
        target_date = datetime.now().date()
    
    # Monday is 0, Sunday is 6
    days_since_monday = target_date.weekday()
    week_start = target_date - timedelta(days=days_since_monday)
    week_end = week_start + timedelta(days=6)
    
    return week_start, week_end


def batch_items(items: List[Any], batch_size: int) -> List[List[Any]]:
    """Split items into batches of specified size"""
    batches = []
    for i in range(0, len(items), batch_size):
        batches.append(items[i:i + batch_size])
    return batches


async def run_with_semaphore(
    semaphore: asyncio.Semaphore,
    coro_func: Callable[..., Awaitable[Any]],
    *args,
    **kwargs
) -> Any:
    """Run async function with semaphore for concurrency control"""
    async with semaphore:
        return await coro_func(*args, **kwargs)


async def gather_with_concurrency(
    tasks: List[Awaitable[Any]],
    max_concurrency: int = 10
) -> List[Any]:
    """Gather async tasks with concurrency limit"""
    semaphore = asyncio.Semaphore(max_concurrency)
    
    async def run_task(task):
        async with semaphore:
            return await task
    
    return await asyncio.gather(*[run_task(task) for task in tasks])


def retry_async(max_attempts: int = 3, delay: float = 1.0, exponential_backoff: bool = True):
    """Decorator for async functions with retry logic"""
    def decorator(func: Callable[..., Awaitable[Any]]):
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt < max_attempts - 1:
                        wait_time = delay * (2 ** attempt if exponential_backoff else 1)
                        await asyncio.sleep(wait_time)
                    
            raise last_exception
        
        return wrapper
    return decorator


def validate_email(email: str) -> bool:
    """Validate email address format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_url(url: str) -> bool:
    """Validate URL format"""
    try:
        parsed = urlparse(url)
        return bool(parsed.scheme and parsed.netloc)
    except Exception:
        return False


def extract_keywords(text: str, min_length: int = 3, max_keywords: int = 10) -> List[str]:
    """Extract meaningful keywords from text"""
    if not text:
        return []
    
    # Convert to lowercase and split into words
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    
    # Common stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'can', 'shall', 'must', 'this', 'that',
        'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me',
        'him', 'her', 'us', 'them', 'my', 'your', 'his', 'its', 'our', 'their'
    }
    
    # Filter words
    keywords = []
    word_count = {}
    
    for word in words:
        if (len(word) >= min_length and 
            word not in stop_words and 
            not word.isdigit()):
            
            word_count[word] = word_count.get(word, 0) + 1
    
    # Sort by frequency and take top keywords
    sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
    keywords = [word for word, count in sorted_words[:max_keywords]]
    
    return keywords


def calculate_readability_score(text: str) -> float:
    """Calculate simple readability score (0-100, higher is better)"""
    if not text:
        return 0.0
    
    # Count sentences, words, and syllables
    sentences = len(re.findall(r'[.!?]+', text))
    words = len(re.findall(r'\b\w+\b', text))
    
    if sentences == 0 or words == 0:
        return 0.0
    
    # Simple syllable count (rough approximation)
    syllables = 0
    for word in re.findall(r'\b\w+\b', text.lower()):
        syllable_count = len(re.findall(r'[aeiouy]', word))
        if word.endswith('e'):
            syllable_count -= 1
        if syllable_count == 0:
            syllable_count = 1
        syllables += syllable_count
    
    # Simplified Flesch Reading Ease formula
    score = 206.835 - (1.015 * (words / sentences)) - (84.6 * (syllables / words))
    
    # Clamp to 0-100 range
    return max(0, min(100, score))


def merge_dictionaries(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """Merge multiple dictionaries, with later ones taking precedence"""
    result = {}
    for d in dicts:
        if isinstance(d, dict):
            result.update(d)
    return result


def deep_merge_dictionaries(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two dictionaries"""
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dictionaries(result[key], value)
        else:
            result[key] = value
    
    return result


def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """Safely parse JSON string with fallback"""
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default


def safe_json_dumps(obj: Any, default: Any = None) -> str:
    """Safely serialize object to JSON with fallback"""
    try:
        return json.dumps(obj, default=str, ensure_ascii=False)
    except (TypeError, ValueError):
        return str(default) if default is not None else "{}"


def generate_unique_id(prefix: str = "", length: int = 8) -> str:
    """Generate a unique ID with optional prefix"""
    import uuid
    unique_part = str(uuid.uuid4()).replace('-', '')[:length]
    return f"{prefix}{unique_part}" if prefix else unique_part


def is_business_hours(dt: Optional[datetime] = None, timezone: str = "UTC") -> bool:
    """Check if datetime falls within business hours (9 AM - 5 PM)"""
    if dt is None:
        dt = datetime.now()
    
    # Simple check without timezone conversion for now
    hour = dt.hour
    weekday = dt.weekday()  # 0 = Monday, 6 = Sunday
    
    # Business hours: 9 AM - 5 PM, Monday - Friday
    return weekday < 5 and 9 <= hour < 17


def format_number_compact(number: int) -> str:
    """Format large numbers in compact form (1.2K, 1.5M, etc.)"""
    if number < 1000:
        return str(number)
    elif number < 1000000:
        return f"{number/1000:.1f}K"
    elif number < 1000000000:
        return f"{number/1000000:.1f}M"
    else:
        return f"{number/1000000000:.1f}B"


class ConfigValidator:
    """Validate configuration settings"""
    
    @staticmethod
    def validate_required_fields(config: Dict[str, Any], required_fields: List[str]) -> List[str]:
        """Validate that required fields are present and non-empty"""
        missing_fields = []
        
        for field in required_fields:
            if field not in config or not config[field]:
                missing_fields.append(field)
        
        return missing_fields
    
    @staticmethod
    def validate_url_fields(config: Dict[str, Any], url_fields: List[str]) -> List[str]:
        """Validate that URL fields contain valid URLs"""
        invalid_urls = []
        
        for field in url_fields:
            if field in config and config[field]:
                if not validate_url(config[field]):
                    invalid_urls.append(field)
        
        return invalid_urls
    
    @staticmethod
    def validate_email_fields(config: Dict[str, Any], email_fields: List[str]) -> List[str]:
        """Validate that email fields contain valid email addresses"""
        invalid_emails = []
        
        for field in email_fields:
            if field in config and config[field]:
                if not validate_email(config[field]):
                    invalid_emails.append(field)
        
        return invalid_emails


# Export commonly used functions
__all__ = [
    'normalize_text',
    'extract_domain',
    'calculate_text_hash',
    'safe_get_nested',
    'truncate_text',
    'clean_filename',
    'format_duration',
    'format_file_size',
    'parse_date_flexible',
    'get_week_boundaries',
    'batch_items',
    'run_with_semaphore',
    'gather_with_concurrency',
    'retry_async',
    'validate_email',
    'validate_url',
    'extract_keywords',
    'calculate_readability_score',
    'merge_dictionaries',
    'deep_merge_dictionaries',
    'safe_json_loads',
    'safe_json_dumps',
    'generate_unique_id',
    'is_business_hours',
    'format_number_compact',
    'ConfigValidator'
]


if __name__ == "__main__":
    # Test utilities
    print("Testing utilities...")
    
    # Test text processing
    text = "This is a sample text with some UPPERCASE and punctuation!"
    print(f"Normalized: {normalize_text(text)}")
    print(f"Hash: {calculate_text_hash(text)}")
    print(f"Keywords: {extract_keywords(text)}")
    print(f"Readability: {calculate_readability_score(text)}")
    
    # Test date handling
    test_date = "2024-01-15T10:30:00Z"
    parsed = parse_date_flexible(test_date)
    print(f"Parsed date: {parsed}")
    
    # Test week boundaries
    week_start, week_end = get_week_boundaries()
    print(f"This week: {week_start} to {week_end}")
    
    # Test validation
    print(f"Valid email: {validate_email('test@example.com')}")
    print(f"Valid URL: {validate_url('https://example.com')}")
    
    print("All tests completed!")
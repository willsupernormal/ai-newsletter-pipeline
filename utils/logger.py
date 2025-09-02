"""
Centralized logging configuration
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
import structlog


def setup_logger(log_level: str = "INFO", log_file: Optional[str] = None) -> None:
    """Setup structured logging for the application"""
    
    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create logs directory if it doesn't exist
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="ISO"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Setup standard library logging
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[]
    )
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    
    # Console formatter with colors
    console_formatter = ColoredFormatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(console_formatter)
    
    # File handler if specified
    file_handler = None
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(numeric_level)
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
        )
        file_handler.setFormatter(file_formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.handlers.clear()  # Remove existing handlers
    root_logger.addHandler(console_handler)
    
    if file_handler:
        root_logger.addHandler(file_handler)
    
    # Set specific logger levels
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    logging.getLogger("asyncpg").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("apify_client").setLevel(logging.WARNING)
    
    # Log startup message
    logger = logging.getLogger("pipeline.startup")
    logger.info(f"Logging initialized with level {log_level}")
    if log_file:
        logger.info(f"Log file: {log_file}")


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output"""
    
    # Color codes
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'       # Reset
    }
    
    def format(self, record):
        # Add color to log level
        if record.levelname in self.COLORS:
            record.levelname = (
                f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
            )
        
        # Format the message
        formatted = super().format(record)
        
        return formatted


class PipelineLogger:
    """Enhanced logger with pipeline-specific methods"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.start_time = None
    
    def start_operation(self, operation: str, **context):
        """Log the start of an operation with context"""
        self.start_time = datetime.now()
        self.logger.info(f"Starting {operation}", extra=context)
    
    def complete_operation(self, operation: str, **context):
        """Log completion of an operation with duration"""
        if self.start_time:
            duration = (datetime.now() - self.start_time).total_seconds()
            context['duration_seconds'] = duration
        
        self.logger.info(f"Completed {operation}", extra=context)
        self.start_time = None
    
    def fail_operation(self, operation: str, error: Exception, **context):
        """Log failure of an operation"""
        if self.start_time:
            duration = (datetime.now() - self.start_time).total_seconds()
            context['duration_seconds'] = duration
        
        context['error_type'] = type(error).__name__
        context['error_message'] = str(error)
        
        self.logger.error(f"Failed {operation}", extra=context, exc_info=True)
        self.start_time = None
    
    def progress(self, operation: str, current: int, total: int, **context):
        """Log progress of long-running operations"""
        percentage = (current / total * 100) if total > 0 else 0
        context.update({
            'current': current,
            'total': total,
            'percentage': f"{percentage:.1f}%"
        })
        
        self.logger.info(f"Progress {operation}: {current}/{total} ({percentage:.1f}%)", extra=context)
    
    def metric(self, metric_name: str, value: float, unit: str = "", **context):
        """Log performance metrics"""
        context.update({
            'metric_name': metric_name,
            'metric_value': value,
            'metric_unit': unit
        })
        
        self.logger.info(f"Metric {metric_name}: {value}{unit}", extra=context)


def get_pipeline_logger(name: str) -> PipelineLogger:
    """Get a pipeline logger instance"""
    return PipelineLogger(name)


def log_function_call(func_name: str, args: tuple = (), kwargs: dict = None):
    """Decorator to log function calls"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(f"pipeline.{func.__module__}.{func.__name__}")
            
            try:
                logger.debug(f"Calling {func_name}")
                result = func(*args, **kwargs)
                logger.debug(f"Completed {func_name}")
                return result
            except Exception as e:
                logger.error(f"Failed {func_name}: {e}")
                raise
        
        return wrapper
    return decorator


def log_async_function_call(func_name: str):
    """Decorator to log async function calls"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            logger = logging.getLogger(f"pipeline.{func.__module__}.{func.__name__}")
            
            try:
                logger.debug(f"Starting async {func_name}")
                result = await func(*args, **kwargs)
                logger.debug(f"Completed async {func_name}")
                return result
            except Exception as e:
                logger.error(f"Failed async {func_name}: {e}")
                raise
        
        return wrapper
    return decorator


def setup_request_logging():
    """Setup HTTP request logging"""
    import aiohttp.client_logger
    
    # Configure aiohttp client logging
    client_logger = logging.getLogger("aiohttp.client")
    client_logger.setLevel(logging.INFO)
    
    # Add custom handler for requests
    request_handler = RequestLoggingHandler()
    client_logger.addHandler(request_handler)


class RequestLoggingHandler(logging.Handler):
    """Custom handler for HTTP request logging"""
    
    def emit(self, record):
        if hasattr(record, 'url') and hasattr(record, 'method'):
            logger = logging.getLogger("pipeline.requests")
            logger.info(f"{record.method} {record.url} - {getattr(record, 'status', 'N/A')}")


# Performance monitoring
class PerformanceMonitor:
    """Monitor and log performance metrics"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = get_pipeline_logger(f"pipeline.performance.{name}")
        self.metrics = {}
    
    def start_timer(self, operation: str):
        """Start timing an operation"""
        self.metrics[operation] = datetime.now()
    
    def end_timer(self, operation: str):
        """End timing and log duration"""
        if operation in self.metrics:
            duration = (datetime.now() - self.metrics[operation]).total_seconds()
            self.logger.metric(f"{operation}_duration", duration, "seconds")
            del self.metrics[operation]
            return duration
        return 0
    
    def log_memory_usage(self):
        """Log current memory usage"""
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            self.logger.metric("memory_usage", memory_mb, "MB")
        except ImportError:
            pass
    
    def log_throughput(self, operation: str, count: int, duration: float):
        """Log throughput metrics"""
        if duration > 0:
            throughput = count / duration
            self.logger.metric(f"{operation}_throughput", throughput, "items/second")


# Export commonly used functions
__all__ = [
    'setup_logger',
    'get_pipeline_logger',
    'PipelineLogger',
    'PerformanceMonitor',
    'log_function_call',
    'log_async_function_call'
]


if __name__ == "__main__":
    # Test logging setup
    setup_logger("DEBUG")
    
    logger = get_pipeline_logger("test")
    logger.start_operation("test_operation", component="test")
    
    import time
    time.sleep(1)
    
    logger.complete_operation("test_operation", items_processed=100)
    logger.metric("test_metric", 42.5, "units")
    
    # Test performance monitor
    monitor = PerformanceMonitor("test")
    monitor.start_timer("test_timer")
    time.sleep(0.5)
    duration = monitor.end_timer("test_timer")
    monitor.log_throughput("test_processing", 10, duration)
"""
FastAPI webhook server for Slack interactive messages
Receives button clicks and routes to handler
"""

import logging
from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.responses import JSONResponse
import json
from urllib.parse import parse_qs

from config.settings import Settings
from services.slack_webhook_handler import SlackWebhookHandler
from utils.logger import setup_logger

# Setup logging
setup_logger('INFO')
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Digest Webhook Server",
    description="Handles Slack interactive message callbacks",
    version="1.0.0"
)

# Initialize settings and handler
settings = Settings()
webhook_handler = SlackWebhookHandler(settings)


@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {
        "status": "healthy",
        "service": "AI Digest Webhook Server",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": "2025-10-26T15:00:00Z"
    }


@app.post("/slack/interactions")
async def slack_interactions(request: Request):
    """
    Handle Slack interactive message callbacks
    
    Slack sends button clicks as form-encoded data with a 'payload' field
    containing JSON data about the interaction.
    """
    try:
        # Get headers for signature verification
        timestamp = request.headers.get('X-Slack-Request-Timestamp', '')
        signature = request.headers.get('X-Slack-Signature', '')
        
        # Get raw body for signature verification
        body = await request.body()
        body_str = body.decode('utf-8')
        
        # Verify Slack signature
        if not webhook_handler.verify_slack_signature(timestamp, body_str, signature):
            logger.warning("Invalid Slack signature")
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Parse form data
        form_data = parse_qs(body_str)
        
        # Extract payload
        if 'payload' not in form_data:
            logger.error("No payload in request")
            raise HTTPException(status_code=400, detail="No payload found")
        
        payload_str = form_data['payload'][0]
        payload = json.loads(payload_str)
        
        # Log interaction
        action_type = payload.get('type', 'unknown')
        user = payload.get('user', {}).get('username', 'unknown')
        logger.info(f"Received {action_type} from {user}")
        
        # Handle interaction
        response_data = await webhook_handler.handle_interaction(payload)
        
        # Return response to Slack
        return JSONResponse(content=response_data)
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON payload: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
        
    except Exception as e:
        logger.error(f"Error handling Slack interaction: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/slack/events")
async def slack_events(request: Request):
    """
    Handle Slack Events API callbacks
    
    This endpoint handles Slack's URL verification challenge
    and can be extended for other event types.
    """
    try:
        data = await request.json()
        
        # Handle URL verification challenge
        if data.get('type') == 'url_verification':
            logger.info("Responding to Slack URL verification challenge")
            return JSONResponse(content={"challenge": data.get('challenge')})
        
        # Handle other event types (future expansion)
        event_type = data.get('event', {}).get('type')
        logger.info(f"Received Slack event: {event_type}")
        
        return JSONResponse(content={"status": "ok"})
        
    except Exception as e:
        logger.error(f"Error handling Slack event: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )


if __name__ == "__main__":
    import uvicorn
    
    # Run server
    port = int(settings.WEBHOOK_PORT) if hasattr(settings, 'WEBHOOK_PORT') else 8000
    
    logger.info(f"Starting webhook server on port {port}")
    
    uvicorn.run(
        "api.webhook_server:app",
        host="0.0.0.0",
        port=port,
        reload=True,  # Auto-reload on code changes (disable in production)
        log_level="info"
    )

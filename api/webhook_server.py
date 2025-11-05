"""
FastAPI webhook server for Slack interactive messages
Receives button clicks and routes to handler
"""

import logging
import asyncio
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


@app.api_route("/slack/test", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def slack_test(request: Request):
    """
    Test endpoint that accepts ANY method and logs everything
    Use this to see what Slack is actually sending
    """
    body = await request.body()
    body_str = body.decode('utf-8') if body else "NO BODY"
    
    logger.info("=" * 80)
    logger.info(f"TEST ENDPOINT HIT: {request.method} /slack/test")
    logger.info(f"Headers: {dict(request.headers)}")
    logger.info(f"Body: {body_str}")
    logger.info("=" * 80)
    
    # Try to parse as JSON and respond to challenge
    try:
        data = json.loads(body_str)
        if data.get('type') == 'url_verification':
            return JSONResponse(content={"challenge": data.get('challenge')})
    except:
        pass
    
    return JSONResponse(content={
        "status": "received",
        "method": request.method,
        "body_length": len(body_str)
    })


@app.api_route("/slack/simple", methods=["GET", "POST"])
async def slack_simple(request: Request):
    """
    Simplest possible endpoint - no auth, no parsing, just respond
    """
    body = await request.body()
    body_str = body.decode('utf-8') if body else ""
    
    logger.info(f"SIMPLE ENDPOINT: {request.method} - Body length: {len(body_str)}")
    
    # Always respond with challenge if present
    try:
        data = json.loads(body_str)
        if 'challenge' in data:
            logger.info(f"Returning challenge: {data['challenge']}")
            return {"challenge": data['challenge']}
    except:
        pass
    
    return {"ok": True}


@app.api_route("/slack/minimal", methods=["GET", "POST"])
async def slack_minimal(request: Request):
    """
    Absolute minimal endpoint - just return OK
    """
    logger.info(f"MINIMAL ENDPOINT HIT: {request.method}")
    return {"ok": True}


@app.post("/slack/challenge")
async def slack_challenge(request: Request):
    """
    Dedicated challenge endpoint - only handles url_verification
    """
    try:
        data = await request.json()
        logger.info(f"CHALLENGE ENDPOINT: Received type={data.get('type')}")
        
        if data.get('type') == 'url_verification':
            challenge = data.get('challenge')
            logger.info(f"Responding with challenge: {challenge}")
            return JSONResponse(
                content={"challenge": challenge},
                headers={"Content-Type": "application/json"}
            )
        
        return {"ok": True}
    except Exception as e:
        logger.error(f"Challenge endpoint error: {e}")
        return {"error": str(e)}


@app.post("/slack/interactions")
async def slack_interactions(request: Request):
    """
    Handle Slack interactive message callbacks
    
    Slack sends button clicks as form-encoded data with a 'payload' field
    containing JSON data about the interaction.
    """
    try:
        # LOG EVERYTHING FOR DEBUGGING
        logger.info("=" * 80)
        logger.info("RECEIVED REQUEST TO /slack/interactions")
        logger.info(f"Headers: {dict(request.headers)}")
        
        # Get headers for signature verification
        timestamp = request.headers.get('X-Slack-Request-Timestamp', '')
        signature = request.headers.get('X-Slack-Signature', '')
        
        # Get raw body
        body = await request.body()
        body_str = body.decode('utf-8')
        
        logger.info(f"Body (first 500 chars): {body_str[:500]}")
        logger.info(f"Content-Type: {request.headers.get('content-type')}")
        
        # Try to parse as JSON first (for URL verification)
        try:
            payload = json.loads(body_str)
            
            # Handle URL verification challenge from Slack
            # NOTE: We respond to the challenge BEFORE verifying signature
            # because Slack needs the challenge response to complete setup
            if payload.get('type') == 'url_verification':
                logger.info("Responding to Slack URL verification challenge")
                challenge = payload.get('challenge')
                if challenge:
                    logger.info(f"Returning challenge: {challenge[:20]}...")
                    return JSONResponse(content={"challenge": challenge})
                else:
                    logger.error("No challenge in url_verification payload")
                    raise HTTPException(status_code=400, detail="No challenge provided")
        except json.JSONDecodeError:
            # Not JSON, must be form-encoded interaction
            pass
        
        # Verify Slack signature for regular interactions
        if not webhook_handler.verify_slack_signature(timestamp, body_str, signature):
            logger.warning("Invalid Slack signature")
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Parse form data for button interactions
        form_data = parse_qs(body_str)
        
        # Extract payload
        if 'payload' not in form_data:
            logger.error("No payload in request")
            raise HTTPException(status_code=400, detail="No payload found")
        
        payload_str = form_data['payload'][0]
        payload = json.loads(payload_str)
        
        # Log interaction
        action_type = payload.get('type', 'unknown')
        user_obj = payload.get('user', {})
        user_name = user_obj.get('username', 'unknown') if isinstance(user_obj, dict) else 'unknown'
        user_id = user_obj.get('id', '') if isinstance(user_obj, dict) else ''
        logger.info(f"Received {action_type} from {user_name}")
        
        # Handle modal submissions differently
        if action_type == 'view_submission':
            # Check which modal was submitted
            callback_id = payload.get('view', {}).get('callback_id')
            response_url = payload.get('response_url')

            if callback_id == 'idea_modal':
                # Idea modal submission
                asyncio.create_task(
                    webhook_handler._process_add_idea_async(
                        payload,
                        user_id,
                        user_name,
                        response_url
                    )
                )
            else:
                # Pipeline modal submission (existing flow)
                asyncio.create_task(
                    webhook_handler._process_add_to_pipeline_async(
                        payload,
                        user_id,
                        user_name,
                        response_url
                    )
                )
            # Close modal immediately
            return JSONResponse(content={"response_action": "clear"})
        else:
            # Handle regular button interactions
            response_data = await webhook_handler.handle_interaction(payload)
            return JSONResponse(content=response_data)
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON payload: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
        
    except Exception as e:
        logger.error(f"Error handling Slack interaction: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/slack/commands")
async def slack_commands(request: Request):
    """
    Handle Slack slash commands (e.g., /add-idea)

    Slack sends slash commands as form-encoded data
    """
    try:
        logger.info("=" * 80)
        logger.info("RECEIVED SLASH COMMAND")
        logger.info(f"Headers: {dict(request.headers)}")

        # Get headers for signature verification
        timestamp = request.headers.get('X-Slack-Request-Timestamp', '')
        signature = request.headers.get('X-Slack-Signature', '')

        # Get raw body
        body = await request.body()
        body_str = body.decode('utf-8')

        logger.info(f"Body: {body_str[:500]}")

        # Verify Slack signature
        if not webhook_handler.verify_slack_signature(timestamp, body_str, signature):
            logger.warning("Invalid Slack signature on slash command")
            raise HTTPException(status_code=401, detail="Invalid signature")

        # Parse form data
        form_data = parse_qs(body_str)

        # Extract command details
        command = form_data.get('command', [''])[0]
        text = form_data.get('text', [''])[0]
        trigger_id = form_data.get('trigger_id', [''])[0]
        user_id = form_data.get('user_id', [''])[0]
        user_name = form_data.get('user_name', [''])[0]

        logger.info(f"Slash command: {command} from {user_name}, text: '{text}'")

        # Route to appropriate handler
        if command == '/add-idea':
            # Open modal for capturing idea
            webhook_handler._open_idea_modal(trigger_id, text)
            return Response(status_code=200)  # Acknowledge immediately
        else:
            return JSONResponse(content={
                "text": f"Unknown command: {command}",
                "response_type": "ephemeral"
            })

    except Exception as e:
        logger.error(f"Error handling slash command: {e}", exc_info=True)
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

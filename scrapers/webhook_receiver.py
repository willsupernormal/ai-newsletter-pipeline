"""
Simple webhook receiver for Gmail forwarding
No IMAP needed - just forward newsletters to a webhook
"""

from flask import Flask, request, jsonify
from datetime import datetime
import json
import logging

app = Flask(__name__)
logger = logging.getLogger(__name__)

@app.route('/webhook/newsletter', methods=['POST'])
def receive_newsletter():
    """
    Receive forwarded newsletter from Gmail
    Set up Gmail filter to forward newsletters to:
    https://your-domain.com/webhook/newsletter
    
    Or use a service like:
    - Zapier (Gmail -> Webhook)
    - Make.com (Gmail -> HTTP Request)
    - IFTTT (Gmail -> Webhooks)
    """
    try:
        data = request.json
        
        # Extract email content
        newsletter = {
            'title': data.get('subject', 'Untitled Newsletter'),
            'content_excerpt': data.get('body', ''),
            'source_type': 'gmail_newsletter',
            'source_name': data.get('from', 'Unknown Sender'),
            'url': data.get('link', ''),
            'published_at': datetime.now().isoformat(),
            'tags': ['newsletter', 'email']
        }
        
        # Save to database or process immediately
        # You can call your pipeline here
        
        logger.info(f"Received newsletter: {newsletter['title']}")
        return jsonify({'status': 'success'}), 200
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(port=5000)
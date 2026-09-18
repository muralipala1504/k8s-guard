"""
k8s-guard Slack Alerts
Sends notifications to Slack for auto-heal events
"""

import os
import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def send_slack_alert(action, resource, name, status, details=""):
    """Send a Slack alert for an auto-heal event"""
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        logger.info("ℹ️ Slack webhook not configured. Alerts disabled.")
        return
    
    payload = {
        "text": f"🛡️ *k8s-guard Alert*",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Action:* `{action}`\n*Resource:* `{resource}`\n*Name:* `{name}`\n*Status:* `{status}`\n*Time:* `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "🔐 *k8s-guard* - Kubernetes Auto-Heal Agent"
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post(webhook_url, json=payload, timeout=5)
        if response.status_code == 200:
            logger.info(f"✅ Slack alert sent for {resource} {name}")
        else:
            logger.error(f"❌ Slack alert failed: {response.status_code}")
    except Exception as e:
        logger.error(f"❌ Slack alert error: {e}")

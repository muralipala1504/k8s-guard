"""
k8s-guard History Module
Stores auto-heal actions with 7-day limit (free tier)
"""

import json
import os
from datetime import datetime, timedelta

HISTORY_FILE = "/tmp/k8s-guard_history.json"

def load_history():
    """Load history from file"""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def trim_history(history, days=7):
    """Remove entries older than days"""
    cutoff = datetime.now() - timedelta(days=days)
    trimmed = []
    for entry in history:
        try:
            entry_time = datetime.fromisoformat(entry['timestamp'])
            if entry_time > cutoff:
                trimmed.append(entry)
        except (KeyError, ValueError):
            trimmed.append(entry)
    return trimmed

def save_action(action_type, resource, resource_name, status, details=""):
    """Save an action to history"""
    history = load_history()
    entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action_type,
        "resource": resource,
        "name": resource_name,
        "status": status,
        "details": details
    }
    history.append(entry)
    
    # Trim to 7 days (free tier)
    history = trim_history(history, 7)
    
    # Keep max 1000 entries
    if len(history) > 1000:
        history = history[-1000:]
    
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

def get_history(limit=50):
    """Get recent history entries"""
    history = load_history()
    return history[-limit:]

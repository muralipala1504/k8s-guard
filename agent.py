#!/usr/bin/env python3
"""
k8s-guard Agent - Continuous Monitoring
Runs auto-heal in the background every 30 seconds
"""

import sys
import os
import time
import logging
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.k8s_guard.k8s_client import K8sClient
from src.k8s_guard.history import save_action
from src.k8s_guard.slack import send_slack_alert

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    logger.info("🚀 k8s-guard Agent started")
    logger.info("⏱️  Monitoring interval: 30 seconds")
    
    try:
        k8s = K8sClient()
    except Exception as e:
        logger.error(f"❌ Failed to initialize: {e}")
        sys.exit(1)
    
    while True:
        try:
            logger.info("🔄 Running auto-heal cycle...")
            
            # Heal pods
            pod_actions = k8s.auto_heal_pods()
            if pod_actions:
                logger.info(f"✅ Healed {len(pod_actions)} pods")
            
            # Heal nodes
            node_actions = k8s.auto_heal_nodes()
            if node_actions:
                logger.info(f"✅ Healed {len(node_actions)} nodes")
            
            # Scale deployments
            scale_actions = k8s.auto_scale_deployments()
            if scale_actions:
                logger.info(f"✅ Scaled {len(scale_actions)} deployments")
            
            time.sleep(30)
            
        except KeyboardInterrupt:
            logger.info("🛑 Agent stopped by user")
            break
        except Exception as e:
            logger.error(f"❌ Error in cycle: {e}")
            time.sleep(30)

if __name__ == "__main__":
    main()

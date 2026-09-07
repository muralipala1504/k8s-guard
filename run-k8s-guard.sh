#!/bin/bash
export PYTHONPATH=/home/ruser/projects/k8s-guard
export KUBECONFIG=/home/ruser/.kube/config
export SLACK_WEBHOOK_URL=${SLACK_WEBHOOK_URL:-""}
cd /home/ruser/projects/k8s-guard
source venv/bin/activate

# Start the agent in the background
python agent.py &

# Start the dashboard in the foreground
python dashboard/app.py

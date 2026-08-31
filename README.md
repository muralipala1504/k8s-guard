# 🚀 k8s-guard

**Autonomous Kubernetes Agent** - Auto-heal, Monitor, and Optimize your K8s clusters.

## Features

- ✅ **Auto-heal** - Automatically restarts failed pods
- ✅ **Web Dashboard** - Real-time monitoring with Gradio UI
- ✅ **Action History** - 7 days free, unlimited with Pro
- ✅ **Slack Alerts** - Get notified of critical events (Pro)
- ✅ **Auto-scaling** - Scale deployments based on metrics (Pro)
- ✅ **Node Management** - Cordon and drain unhealthy nodes (Pro)
- ✅ **Cost Optimization** - Resource recommendations (Pro)

## Quick Start

```bash
# Clone and install
git clone https://github.com/muralipala1504/k8s-guard.git
cd k8s-guard

# Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -e .

# Start the agent
k8s-guard start --ui --port=7860
License
Free: 7-day action history, basic auto-heal

Pro: Unlimited history, Slack alerts, auto-scaling, node management

Architecture
┌─────────────────────────────────────────┐
│          k8s-guard Agent               │
│  ┌─────────────────────────────────┐   │
│  │  Pod Watcher                    │   │
│  │  - Detects failed pods         │   │
│  │  - Triggers auto-heal          │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │  Action History (SQLite)       │   │
│  │  - 7 days free                │   │
│  │  - Unlimited Pro              │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │  Web UI (Gradio)               │   │
│  │  - Dashboard                   │   │
│  │  - History view               │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
Commands
k8s-guard start           # Start agent with UI
k8s-guard start --no-ui   # Run without UI
k8s-guard status          # Show status
k8s-guard version         # Show version

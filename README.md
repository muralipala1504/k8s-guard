# 🛡️ k8s-guard

**Kubernetes Auto-Heal Agent** — Monitors and auto-heals Kubernetes clusters.

---

## 🚀 Features

| Feature | Description |
|---------|-------------|
| **Pod Auto-Heal** | Restarts failed pods (CrashLoopBackOff, ImagePullBackOff, etc.) |
| **Node Auto-Heal** | Detects and uncordons SchedulingDisabled nodes |
| **Deployment Scaling** | Auto-scales failing deployments |
| **Dashboard** | Web UI showing cluster status and action history |
| **Free Tier** | 7-day action history |
| **Pro Tier** | Unlimited history + Slack alerts + Multi-cluster |
| **Auto-Kubeconfig** | ✅ Automatically configures Kubernetes access |

---

## ⚡ Quick Start

**✨ No manual configuration needed** — the installer automatically sets up kubectl and Kubernetes access.

### Prerequisites

- Kubernetes cluster (minikube, kind, or cloud)
- `kubectl` configured
- Python 3.9+

### One-Line Install

```bash
curl -sSL https://raw.githubusercontent.com/muralipala1504/k8s-guard/main/scripts/install.sh | bash
Manual Install
git clone https://github.com/muralipala1504/k8s-guard.git
cd k8s-guard
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python dashboard/app.py
📊 Dashboard
Access the dashboard at http://localhost:7860

## 💬 Slack Alerts (Pro)

Configure Slack alerts for real-time notifications:

```bash
sudo tee -a /etc/systemd/system/k8s-guard.service << 'EOF'
Environment="SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
EOF

sudo systemctl daemon-reload
sudo systemctl restart k8s-guard

Alert Example

🛡️ k8s-guard Alert
Action: delete
Resource: pod
Name: fail-pod
Status: success
Time: 2026-09-07 06:29:21



Nodes: Status of all nodes

Pods: Running/Error pods with restart counts

Recent Actions: History of auto-heal events

🔧 Configuration
Environment Variables
Variable	Description	Default
KUBECONFIG	Path to kubeconfig	~/.kube/config
LOG_LEVEL	Logging level	INFO
📄 License
MIT License

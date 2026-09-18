# 🛡️ k8s-guard

**Kubernetes Auto-Heal Agent** — Monitors and auto-heals Kubernetes clusters. Ships with a built-in web dashboard.

> **Autonomous. Free. Open Source.**

---

## 🎯 What It Does

Watches your Kubernetes cluster 24/7 and automatically fixes common failures:

- 🔄 **Pods that crash** → restart them
- ⚠️ **Pods stuck in ImagePullBackOff** → clean them up
- 🚫 **Nodes marked SchedulingDisabled** → uncordon them
- 📉 **Deployments failing** → auto-scale them

No more waking up at 3 AM for a pod that could heal itself.

---

## 🚀 Features

| Feature | Description |
|---------|-------------|
| **Pod Auto-Heal** | Restarts failed pods (CrashLoopBackOff, ImagePullBackOff, Error) |
| **Node Auto-Heal** | Detects and uncordons SchedulingDisabled nodes |
| **Deployment Scaling** | Auto-scales failing deployments |
| **Web Dashboard** | Real-time cluster status + action history |
| **Slack Alerts** | Get notified of every auto-heal event |
| **Action History** | 7-day log of all agent actions |
| **Auto-Kubeconfig** | ✅ Automatically configures Kubernetes access |
| **MIT Licensed** | Free for any use |

---

## ⚡ Quick Start

### Prerequisites

- Kubernetes cluster (minikube, kind, or cloud)
- `kubectl` configured
- Python 3.9+

### One-Line Install

```bash
curl -sSL https://raw.githubusercontent.com/muralipala1504/k8s-guard/main/scripts/install.sh | bash
```

### Manual Install

```bash
git clone https://github.com/muralipala1504/k8s-guard.git
cd k8s-guard
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 📊 Dashboard

Access the web dashboard at **http://localhost:7860**:

- **Nodes** — Live status of all cluster nodes
- **Pods** — Running/Error pods with restart counts
- **Recent Actions** — History of all auto-heal events
- **Manual Controls** — Trigger actions on demand

---

## 💬 Slack Alerts

Get real-time notifications when k8s-guard auto-heals something.

### Setup

1. Create a Slack webhook at https://api.slack.com/apps
2. Add the webhook to the service:

```bash
sudo tee -a /etc/systemd/system/k8s-guard.service << 'EOF'
Environment="SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
EOF

sudo systemctl daemon-reload
sudo systemctl restart k8s-guard
```

### Alert Example

```
🛡️ k8s-guard Alert
Action: delete
Resource: pod
Name: fail-pod
Status: success
Time: 2026-09-18 06:29:21

🔐 k8s-guard - Kubernetes Auto-Heal Agent
```

---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `KUBECONFIG` | Path to kubeconfig | `~/.kube/config` |
| `SLACK_WEBHOOK_URL` | Slack webhook for alerts | (empty — alerts disabled) |
| `LOG_LEVEL` | Logging level | `INFO` |

### Systemd Service

```bash
# Check status
sudo systemctl status k8s-guard

# View logs
sudo journalctl -u k8s-guard -f

# Restart
sudo systemctl restart k8s-guard
```

---

## 📚 Documentation

- **[README.md](README.md)** — Project overview (this file)
- **[docs/INSTALL.md](docs/INSTALL.md)** — Detailed installation guide
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** — Technical design

---

## 🛠️ How It Works

```
┌─────────────────────────────────────────────────────────┐
│  k8s-guard Agent (runs every 30s)                       │
│                                                         │
│  1. Connect to Kubernetes API                           │
│  2. Scan all Pods, Nodes, Deployments                   │
│  3. Detect failures (CrashLoop, ImagePull, etc.)        │
│  4. Auto-heal: restart, delete, uncordon, scale         │
│  5. Log action + send Slack alert                       │
│  6. Repeat                                              │
└─────────────────────────────────────────────────────────┘
                        ↓
              Kubernetes Cluster
              (minikube / kind / cloud)
```

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing`)
5. Open a Pull Request

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/muralipala1504/k8s-guard/issues)
- **Discussions**: [GitHub Discussions](https://github.com/muralipala1504/k8s-guard/discussions)

---

**Part of the Linux Admin Suite** — [github.com/muralipala1504](https://github.com/muralipala1504)

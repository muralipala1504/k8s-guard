# Installation Guide

## Prerequisites

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Kubernetes | 1.20+ | 1.25+ |
| kubectl | 1.20+ | Latest |
| Python | 3.9+ | 3.11+ |
| CPU | 2 cores | 4 cores |
| RAM | 2 GB | 4 GB |

## Installation

### One-Line Install

```bash
curl -sSL https://raw.githubusercontent.com/muralipala1504/k8s-guard/main/scripts/install.sh | bash
Manual Instal
git clone https://github.com/muralipala1504/k8s-guard.git
cd k8s-guard
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python dashboard/app.py
# Check if dashboard is running
curl http://localhost:7860

# Check logs
tail -f /var/log/k8s-guard.log

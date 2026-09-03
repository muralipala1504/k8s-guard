# Architecture

## Overview

k8s-guard is a Python-based agent that monitors Kubernetes clusters and automatically heals failures.

## Components

| Component | Description |
|-----------|-------------|
| **Kubernetes Client** | Connects to the Kubernetes API |
| **Pod Monitor** | Checks pod status and restarts failed pods |
| **Node Monitor** | Detects unhealthy nodes |
| **Deployment Scaler** | Auto-scales failing deployments |
| **Dashboard** | Web UI for monitoring and actions |

## Data Flow
Kubernetes API → k8s-guard Agent → Auto-Heal Actions → Dashboard

## Auto-Heal Logic

| Condition | Action |
|-----------|--------|
| Pod in `CrashLoopBackOff` | Delete pod (restart) |
| Pod in `ImagePullBackOff` | Delete pod (retry pull) |
| Node `SchedulingDisabled` | Un-cordon node |
| Deployment >50% failing | Scale down replicas |

## License

- **Free**: 7-day history
- **Pro**: Unlimited history + Slack alerts + Multi-cluster

import warnings
warnings.filterwarnings("ignore")
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import gradio as gr
import docker
import subprocess
import json
import time
from datetime import datetime

from src.k8s_guard.k8s_client import K8sClient
from src.k8s_guard.history import get_history
import logging
logging.basicConfig(level=logging.INFO)

# Initialize Kubernetes client
k8s = K8sClient()

# Store action history globally
action_history = []

# Auto-Heal for Kubernetes
def k8s_auto_heal():
    global action_history
    try:
        actions = k8s.auto_heal_pods()
        if actions:
            action_history.extend(actions)
        return actions
    except Exception as e:
        return [{"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "pod": "error", "action": str(e)}]

# Get Kubernetes nodes
def get_k8s_nodes():
    try:
        nodes = k8s.get_nodes()
        return nodes
    except:
        return [{"name": "minikube", "status": "Ready"}]

# Get Kubernetes pods
def get_k8s_pods():
    try:
        pods = k8s.get_pods()
        result = []
        for pod in pods:
            status = k8s.get_pod_status(pod)
            result.append(status)
        return result
    except:
        return []

# Refresh Dashboard
def refresh():
    global action_history
    
    heal_actions = k8s_auto_heal()
    nodes = get_k8s_nodes()
    pods = get_k8s_pods()
    
    node_text = "## 🖥️ Nodes\n\n"
    for n in nodes:
        icon = "🟢" if n["status"] == "Ready" else "🔴"
        node_text += f"{icon} **{n['name']}**: {n['status']}\n"
    
    pod_text = "## 📦 Pods\n\n"
    for p in pods:
        status = p["status"]
        reason = p.get("reason", "")
        icon = "🟢" if status == "Running" else ("🟡" if status == "Pending" else "🔴")
        pod_text += f"{icon} **{p['name']}**: {status} (restarts: {p['restarts']})"
        if reason:
            pod_text += f" - {reason}"
        pod_text += "\n"
    
    # Action history from JSON file
    history = get_history(10)
    history_text = "## 📜 Recent Actions\n\n"
    if history:
        for action in history:
            history_text += f"**{action['timestamp']}** — {action['action']} {action['resource']} {action['name']} — {action['status']}\n"
    else:
        history_text += "No actions recorded yet.\n"
    
    return node_text, pod_text, history_text

def manual_restart_pod(name):
    try:
        k8s.delete_pod("default", name)
        return f"✅ Deleted pod {name} (will be recreated if part of a deployment)"
    except Exception as e:
        return f"❌ Failed: {e}"

# Build the UI
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🛡️ k8s-guard")
    gr.Markdown("Auto-heal · Monitor · Optimize")
    
    with gr.Row():
        refresh_btn = gr.Button("🔄 Refresh")
        license_status = gr.Markdown("**License**: Free")
    
    with gr.Row():
        with gr.Column(scale=1):
            nodes_output = gr.Markdown("Loading...")
        with gr.Column(scale=2):
            pods_output = gr.Markdown("Loading...")
    
    with gr.Row():
        history_output = gr.Markdown("Loading...")
    
    with gr.Row():
        pod_name = gr.Textbox(label="Pod Name", placeholder="e.g., test-pod")
        restart_btn = gr.Button("🔄 Delete Pod (Auto-Heal Test)")
        restart_result = gr.Textbox(label="Result", interactive=False)
    
    refresh_btn.click(refresh, outputs=[nodes_output, pods_output, history_output])
    restart_btn.click(manual_restart_pod, inputs=[pod_name], outputs=[restart_result])
    demo.load(refresh, outputs=[nodes_output, pods_output, history_output])

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)

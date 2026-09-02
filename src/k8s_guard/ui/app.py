import gradio as gr
from datetime import datetime
from ..core.database import Database
from ..k8s.client import K8sClient
from ..k8s.node_manager import NodeManager

def create_ui(db: Database, k8s: K8sClient, node_manager: NodeManager = None):
    
    def get_stats_data():
        stats = db.get_stats()
        actions = db.get_actions(limit=10)
        node_status = node_manager.get_node_status() if node_manager else []
        
        nodes_text = ""
        if node_status:
            for node in node_status:
                icon = "✅" if node['status'] == 'Ready' else "❌"
                cordon = "🔒 Cordoned" if not node['schedulable'] else "🔓 Schedulable"
                nodes_text += f"{icon} {node['name']} | {node['status']} | {cordon}\n"
        else:
            nodes_text = "No nodes found"
        
        actions_text = ""
        if actions:
            for a in actions:
                icon = "✅" if a['status'] == 'success' else "❌"
                actions_text += f"{icon} {a['timestamp'][:19]} | {a['action_type']} | {a['resource_name']}\n"
        else:
            actions_text = "No actions yet"
        
        return {
            "total_actions": stats['total_actions'],
            "nodes_count": len(node_status),
            "actions_count": len(actions),
            "nodes_text": nodes_text,
            "actions_text": actions_text,
            "license": "🔓 Pro" if stats['is_pro'] else "🆓 Free",
            "time": datetime.now().strftime('%H:%M:%S')
        }
    
    with gr.Blocks(title="k8s-guard", theme=gr.themes.Soft()) as app:
        
        # Header
        with gr.Row():
            with gr.Column():
                gr.Markdown("# 🚀 k8s-guard")
                gr.Markdown("*Autonomous Kubernetes Agent — Auto-heal, Monitor & Optimize*")
        
        # Stats - 3 columns
        with gr.Row():
            with gr.Column():
                gr.Markdown("### 📊 Total Actions")
                total_actions = gr.Number(value=0, label="", interactive=False)
            with gr.Column():
                gr.Markdown("### 🖥️ Nodes")
                nodes_count = gr.Number(value=0, label="", interactive=False)
            with gr.Column():
                gr.Markdown("### 📋 Recent")
                actions_count = gr.Number(value=0, label="", interactive=False)
        
        # Main content - 2 columns
        with gr.Row():
            with gr.Column():
                gr.Markdown("### 🖥️ Node Status")
                nodes_output = gr.Textbox(value="", label="", lines=5, interactive=False)
            with gr.Column():
                gr.Markdown("### 📋 Action History")
                actions_output = gr.Textbox(value="", label="", lines=5, interactive=False)
        
        # Footer - 2 columns
        with gr.Row():
            with gr.Column():
                license_status = gr.Textbox(value="", label="🔑 License", interactive=False)
            with gr.Column():
                timestamp = gr.Textbox(value="", label="⏱️ Updated", interactive=False)
        
        # Refresh button
        refresh_btn = gr.Button("🔄 Refresh Dashboard", variant="primary")
        
        def update_dashboard():
            data = get_stats_data()
            return [
                data["total_actions"],
                data["nodes_count"],
                data["actions_count"],
                data["nodes_text"],
                data["actions_text"],
                data["license"],
                data["time"]
            ]
        
        refresh_btn.click(
            update_dashboard,
            outputs=[total_actions, nodes_count, actions_count, nodes_output, actions_output, license_status, timestamp]
        )
        
        app.load(update_dashboard, outputs=[total_actions, nodes_count, actions_count, nodes_output, actions_output, license_status, timestamp])
    
    return app

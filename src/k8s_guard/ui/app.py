import gradio as gr
from datetime import datetime
from ..core.database import Database
from ..k8s.client import K8sClient
from ..k8s.node_manager import NodeManager

def create_ui(db: Database, k8s: K8sClient, node_manager: NodeManager = None):
    
    with gr.Blocks(title="k8s-guard", theme=gr.themes.Soft()) as app:
        
        gr.Markdown("# 🚀 k8s-guard")
        gr.Markdown("Auto-heal · Monitor · Optimize")
        
        with gr.Row():
            with gr.Column():
                total_actions = gr.Number(label="Total Actions", value=0, interactive=False)
            with gr.Column():
                nodes_count = gr.Number(label="Nodes", value=0, interactive=False)
            with gr.Column():
                actions_count = gr.Number(label="Recent Actions", value=0, interactive=False)
        
        with gr.Row():
            with gr.Column():
                nodes_output = gr.Textbox(label="Node Status", lines=4, interactive=False)
            with gr.Column():
                actions_output = gr.Textbox(label="Action History", lines=4, interactive=False)
        
        with gr.Row():
            license_status = gr.Textbox(label="License", value="Free", interactive=False)
            timestamp = gr.Textbox(label="Last Updated", value="", interactive=False)
        
        refresh_btn = gr.Button("Refresh")
        
        def update():
            stats = db.get_stats()
            actions = db.get_actions(limit=10)
            node_status = node_manager.get_node_status() if node_manager else []
            
            nodes_text = ""
            for node in node_status:
                nodes_text += f"{node['name']} | {node['status']}\n"
            
            actions_text = ""
            for a in actions:
                actions_text += f"{a['timestamp'][:19]} | {a['action_type']} | {a['resource_name']}\n"
            
            return [
                stats['total_actions'],
                len(node_status),
                len(actions),
                nodes_text or "No nodes",
                actions_text or "No actions",
                "Pro" if stats['is_pro'] else "Free",
                datetime.now().strftime('%H:%M:%S')
            ]
        
        refresh_btn.click(
            update,
            outputs=[total_actions, nodes_count, actions_count, nodes_output, actions_output, license_status, timestamp]
        )
        
        app.load(update, outputs=[total_actions, nodes_count, actions_count, nodes_output, actions_output, license_status, timestamp])
    
    return app

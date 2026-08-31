import gradio as gr
from datetime import datetime
from ..core.database import Database
from ..k8s.client import K8sClient

def create_ui(db: Database, k8s: K8sClient):
    def get_dashboard():
        stats = db.get_stats()
        actions = db.get_actions(limit=10)
        
        # DEBUG - print to terminal
        print(f"DEBUG: Found {len(actions)} actions")
        
        html = f"<h2>DEBUG: Found {len(actions)} actions</h2>"
        
        if actions:
            for a in actions:
                html += f"<p>{a['action_type']}: {a['resource_name']}</p>"
        else:
            html += "<p>No actions</p>"
        
        return html
    
    with gr.Blocks() as app:
        gr.Markdown("# k8s-guard")
        output = gr.HTML(get_dashboard)
        btn = gr.Button("Refresh")
        btn.click(get_dashboard, outputs=output)
    
    return app

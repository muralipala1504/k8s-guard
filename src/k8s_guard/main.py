#!/usr/bin/env python3
import sys
import click
import threading
import time
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from .core.config import Config
from .core.database import Database
from .k8s.client import K8sClient
from .k8s.watcher import PodWatcher
from .ui.app import create_ui

console = Console()

@click.group()
def cli():
    """k8s-guard - Autonomous Kubernetes Agent"""
    pass

@cli.command()
@click.option('--namespace', default='', help='Namespace to watch')
@click.option('--ui/--no-ui', default=True, help='Start web UI')
@click.option('--port', default=7860, help='Web UI port')
@click.option('--in-cluster', is_flag=True, help='Run inside Kubernetes')
def start(namespace, ui, port, in_cluster):
    """Start k8s-guard agent"""
    console.print(Panel.fit("[bold blue]🚀 k8s-guard[/bold blue]", border_style="blue"))
    
    config = Config()
    config.in_cluster = in_cluster
    config.namespace = namespace
    
    console.print(f"[green]✓[/green] Config loaded (Pro: {config.is_pro})")
    
    db = Database(config.db_path, config.is_pro)
    console.print(f"[green]✓[/green] Database: {config.db_path}")
    
    k8s = K8sClient(config.kubeconfig, config.in_cluster)
    
    def on_pod_failure(pod):
        console.print(f"[red]⚠ Pod failure:[/red] {pod['name']} - {pod['reason']}")
        if k8s.delete_pod(pod['name'], pod['namespace']):
            db.add_action('restart', 'pod', pod['name'], pod['namespace'], 
                         'success', f'Restarted: {pod["reason"]}')
            console.print(f"[green]✓[/green] Pod {pod['name']} restarted")
        else:
            db.add_action('restart', 'pod', pod['name'], pod['namespace'], 
                         'failed', f'Failed: {pod["reason"]}')
    
    watcher = PodWatcher(k8s, on_pod_failure)
    
    # Start watcher in background thread
    def run_watcher():
        watcher.watch_forever(namespace, config.check_interval)
    
    watcher_thread = threading.Thread(target=run_watcher, daemon=True)
    watcher_thread.start()
    console.print("[yellow]✓[/yellow] Watcher running in background")
    
    if ui:
        console.print("[yellow]🔮 Starting UI...[/yellow]")
        app = create_ui(db, k8s)
        app.launch(server_name='0.0.0.0', server_port=port, share=False)
    else:
        console.print("[yellow]Agent running (no UI)[/yellow]")
        while True:
            time.sleep(1)

@cli.command()
def status():
    config = Config()
    db = Database(config.db_path, config.is_pro)
    stats = db.get_stats()
    
    table = Table(title="k8s-guard Status")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("License", "Pro" if config.is_pro else "Free")
    table.add_row("Storage", stats['storage_limit'])
    table.add_row("Total Actions", str(stats['total_actions']))
    console.print(table)
    
    actions = db.get_actions(limit=5)
    if actions:
        console.print("\n[bold]Recent Actions:[/bold]")
        for a in actions:
            console.print(f"  {a['timestamp'][:19]} - {a['action_type']}: {a['resource_name']}")

@cli.command()
def version():
    console.print("[bold blue]k8s-guard[/bold blue] v0.1.0")

if __name__ == '__main__':
    cli()

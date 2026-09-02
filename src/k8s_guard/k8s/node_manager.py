"""
Node Manager - Monitor and manage Kubernetes nodes
"""

from kubernetes.client.rest import ApiException
import time

class NodeManager:
    def __init__(self, k8s_client, db=None, on_node_issue=None):
        self.client = k8s_client
        self.db = db
        self.on_node_issue = on_node_issue
    
    def check_nodes(self):
        try:
            nodes = self.client.core_v1.list_node()
            unhealthy_nodes = []
            
            for node in nodes.items:
                node_name = node.metadata.name
                
                for condition in node.status.conditions:
                    # Only alert on REAL issues:
                    # 1. Ready = False (node not ready)
                    if condition.type == "Ready" and condition.status == "False":
                        unhealthy_nodes.append({
                            'name': node_name,
                            'condition': 'NotReady',
                            'status': 'False',
                            'reason': condition.reason or 'Node not ready',
                            'message': condition.message or ''
                        })
                    # 2. MemoryPressure = True (node running out of memory)
                    elif condition.type == "MemoryPressure" and condition.status == "True":
                        unhealthy_nodes.append({
                            'name': node_name,
                            'condition': 'MemoryPressure',
                            'status': 'True',
                            'reason': condition.reason or 'Memory pressure',
                            'message': condition.message or ''
                        })
                    # 3. DiskPressure = True (node running out of disk)
                    elif condition.type == "DiskPressure" and condition.status == "True":
                        unhealthy_nodes.append({
                            'name': node_name,
                            'condition': 'DiskPressure',
                            'status': 'True',
                            'reason': condition.reason or 'Disk pressure',
                            'message': condition.message or ''
                        })
                    # 4. PIDPressure = True (node running out of PIDs)
                    elif condition.type == "PIDPressure" and condition.status == "True":
                        unhealthy_nodes.append({
                            'name': node_name,
                            'condition': 'PIDPressure',
                            'status': 'True',
                            'reason': condition.reason or 'PID pressure',
                            'message': condition.message or ''
                        })
                
                # Check if node is cordoned
                if node.spec.unschedulable:
                    unhealthy_nodes.append({
                        'name': node_name,
                        'condition': 'Cordoned',
                        'status': 'True',
                        'reason': 'Manually cordoned',
                        'message': 'Node is cordoned'
                    })
            
            if unhealthy_nodes and self.on_node_issue:
                for node in unhealthy_nodes:
                    self.on_node_issue(node)
            
            return unhealthy_nodes
            
        except Exception as e:
            print(f"[ERROR] Failed to check nodes: {e}")
            return []
    
    def cordon_node(self, node_name):
        try:
            patch = {"spec": {"unschedulable": True}}
            self.client.core_v1.patch_node(node_name, patch)
            print(f"[INFO] Node {node_name} cordoned")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to cordon node {node_name}: {e}")
            return False
    
    def get_node_status(self):
        try:
            nodes = self.client.core_v1.list_node()
            status = []
            for node in nodes.items:
                ready = False
                for condition in node.status.conditions:
                    if condition.type == "Ready":
                        ready = condition.status == "True"
                status.append({
                    'name': node.metadata.name,
                    'status': 'Ready' if ready else 'NotReady',
                    'schedulable': not node.spec.unschedulable
                })
            return status
        except Exception as e:
            print(f"[ERROR] Failed to get node status: {e}")
            return []
    
    def monitor_forever(self, interval=30):
        print(f"[INFO] Starting node monitor (interval={interval}s)")
        while True:
            try:
                unhealthy = self.check_nodes()
                if unhealthy:
                    print(f"[WARN] Found {len(unhealthy)} node issues")
                time.sleep(interval)
            except KeyboardInterrupt:
                print("\n[INFO] Stopping node monitor")
                break
            except Exception as e:
                print(f"[ERROR] Node monitor error: {e}")
                time.sleep(interval * 2)

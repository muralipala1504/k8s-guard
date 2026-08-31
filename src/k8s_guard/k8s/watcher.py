import time
from typing import List, Dict
from kubernetes.client.rest import ApiException
from .client import K8sClient

class PodWatcher:
    """Watch pods for failures and trigger healing"""
    
    def __init__(self, k8s_client: K8sClient, on_failure_callback=None):
        self.client = k8s_client
        self.on_failure = on_failure_callback
        self.known_pods = {}
    
    def check_pods(self, namespace: str = ''):
        """Check all pods for failures"""
        pods = self.client.get_pods(namespace)
        
        if not pods:
            return []
        
        unhealthy_pods = []
        
        for pod in pods.items:
            pod_name = pod.metadata.name
            pod_namespace = pod.metadata.namespace
            status = pod.status
            phase = status.phase
            
            if phase in ['Failed', 'Unknown']:
                unhealthy_pods.append({
                    'name': pod_name,
                    'namespace': pod_namespace,
                    'phase': phase,
                    'reason': status.reason if status.reason else 'Unknown'
                })
            
            if status.container_statuses:
                for container in status.container_statuses:
                    if container.state.waiting and container.state.waiting.reason in [
                        'CrashLoopBackOff', 'ImagePullBackOff', 'ErrImagePull'
                    ]:
                        unhealthy_pods.append({
                            'name': pod_name,
                            'namespace': pod_namespace,
                            'phase': phase,
                            'reason': container.state.waiting.reason,
                            'container': container.name
                        })
        
        for pod in unhealthy_pods:
            if self.on_failure:
                self.on_failure(pod)
        
        return unhealthy_pods
    
    def watch_forever(self, namespace: str = '', interval: int = 10):
        """Continuously watch pods"""
        print(f"[INFO] Starting pod watcher (interval={interval}s)")
        
        while True:
            try:
                unhealthy = self.check_pods(namespace)
                if unhealthy:
                    print(f"[INFO] Found {len(unhealthy)} unhealthy pods")
                time.sleep(interval)
            except KeyboardInterrupt:
                print("\n[INFO] Stopping watcher")
                break
            except Exception as e:
                print(f"[ERROR] Watcher error: {e}")
                time.sleep(interval * 2)

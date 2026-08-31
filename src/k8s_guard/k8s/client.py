from kubernetes import client, config
from kubernetes.client.rest import ApiException
import os

class K8sClient:
    """Kubernetes API client wrapper"""
    
    def __init__(self, kubeconfig: str = None, in_cluster: bool = False):
        self.kubeconfig = kubeconfig
        self.in_cluster = in_cluster
        
        try:
            if in_cluster:
                config.load_incluster_config()
            elif kubeconfig and os.path.exists(kubeconfig):
                config.load_kube_config(config_file=kubeconfig)
            else:
                config.load_kube_config()
            
            self.core_v1 = client.CoreV1Api()
            self.apps_v1 = client.AppsV1Api()
            self.autoscaling_v1 = client.AutoscalingV1Api()
            
            # Test connection
            self.core_v1.get_api_resources()
            print("[✓] Connected to Kubernetes cluster")
            
        except Exception as e:
            print(f"[✗] Failed to connect to Kubernetes: {e}")
            raise
    
    def get_pods(self, namespace: str = ''):
        """Get pods in namespace (or all namespaces)"""
        try:
            if namespace:
                return self.core_v1.list_namespaced_pod(namespace)
            else:
                return self.core_v1.list_pod_for_all_namespaces()
        except ApiException as e:
            print(f"[ERROR] Failed to get pods: {e}")
            return None
    
    def get_pod_status(self, name: str, namespace: str = 'default'):
        """Get specific pod status"""
        try:
            return self.core_v1.read_namespaced_pod_status(name, namespace)
        except ApiException:
            return None
    
    def delete_pod(self, name: str, namespace: str = 'default'):
        """Delete a pod (forces restart if in deployment)"""
        try:
            self.core_v1.delete_namespaced_pod(name, namespace)
            return True
        except ApiException as e:
            print(f"[ERROR] Failed to delete pod {name}: {e}")
            return False

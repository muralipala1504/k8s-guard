"""
Kubernetes API Client for k8s-guard
Monitors pods, nodes, and deployments
"""

import os
import time
import logging
from datetime import datetime
from kubernetes import client, config

logger = logging.getLogger(__name__)

class K8sClient:
    def __init__(self):
        """Initialize Kubernetes client"""
        try:
            config.load_incluster_config()
            logger.info("✅ Loaded in-cluster Kubernetes config")
        except:
            try:
                config.load_kube_config()
                logger.info("✅ Loaded kubeconfig from ~/.kube/config")
            except Exception as e:
                logger.error(f"❌ Failed to load Kubernetes config: {e}")
                raise
        
        self.core_v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()
        self.batch_v1 = client.BatchV1Api()
    
    def get_pods(self, namespace="default"):
        """Get all pods in a namespace"""
        try:
            pods = self.core_v1.list_namespaced_pod(namespace)
            return pods.items
        except Exception as e:
            logger.error(f"❌ Failed to get pods: {e}")
            return []
    
    def get_pod_status(self, pod):
        """Extract pod status"""
        status = pod.status.phase
        conditions = pod.status.conditions or []
        reason = ""
        container_statuses = pod.status.container_statuses or []
        
        # Check for failure conditions
        if container_statuses:
            for c in container_statuses:
                if c.state.waiting and c.state.waiting.reason:
                    reason = c.state.waiting.reason
                if c.state.terminated and c.state.terminated.reason:
                    reason = c.state.terminated.reason
        
        restart_count = 0
        if container_statuses:
            restart_count = sum(c.restart_count for c in container_statuses)
        
        return {
            "name": pod.metadata.name,
            "namespace": pod.metadata.namespace,
            "status": status,
            "reason": reason,
            "restarts": restart_count,
            "node": pod.spec.node_name or "unknown"
        }
    
    def get_nodes(self):
        """Get all nodes"""
        try:
            nodes = self.core_v1.list_node()
            result = []
            for node in nodes.items:
                status = "Ready" if any(c.type == "Ready" and c.status == "True" for c in node.status.conditions) else "NotReady"
                result.append({
                    "name": node.metadata.name,
                    "status": status,
                    "kubelet_version": node.status.node_info.kubelet_version,
                    "os": node.status.node_info.operating_system,
                    "architecture": node.status.node_info.architecture
                })
            return result
        except Exception as e:
            logger.error(f"❌ Failed to get nodes: {e}")
            return []
    
    def get_deployments(self, namespace="default"):
        """Get all deployments"""
        try:
            deployments = self.apps_v1.list_namespaced_deployment(namespace)
            return deployments.items
        except Exception as e:
            logger.error(f"❌ Failed to get deployments: {e}")
            return []
    
    def restart_deployment(self, namespace, name):
        """Restart a deployment by scaling it down and up"""
        try:
            self.apps_v1.patch_namespaced_deployment_scale(
                name=name,
                namespace=namespace,
                body={"spec": {"replicas": 0}}
            )
            logger.info(f"🔄 Scaled down deployment {name} to 0")
            time.sleep(2)
            self.apps_v1.patch_namespaced_deployment_scale(
                name=name,
                namespace=namespace,
                body={"spec": {"replicas": 1}}
            )
            logger.info(f"🔄 Scaled up deployment {name} to 1")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to restart deployment {name}: {e}")
            return False
    
    def delete_pod(self, namespace, name):
        """Delete a pod (triggers auto-restart if part of a deployment)"""
        try:
            self.core_v1.delete_namespaced_pod(name=name, namespace=namespace)
            logger.info(f"🗑️ Deleted pod {name} in namespace {namespace}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to delete pod {name}: {e}")
            return False
    
    def get_namespaces(self):
        """Get all namespaces"""
        try:
            namespaces = self.core_v1.list_namespace()
            return [ns.metadata.name for ns in namespaces.items]
        except Exception as e:
            logger.error(f"❌ Failed to get namespaces: {e}")
            return []
    
    def auto_heal_pods(self, namespace="default"):
        """Auto-heal failed pods"""
        pods = self.get_pods(namespace)
        actions = []
        failure_conditions = ["CrashLoopBackOff", "ImagePullBackOff", "Error", "Failed", "OOMKilled"]
        
        for pod in pods:
            status = self.get_pod_status(pod)
            
            # Check if pod is in a failure state
            needs_heal = False
            heal_reason = ""
            
            if status["status"] in ["Failed", "Unknown"]:
                needs_heal = True
                heal_reason = status["status"]
            
            if status["reason"] in failure_conditions:
                needs_heal = True
                heal_reason = status["reason"]
            
            if status["restarts"] > 5:
                needs_heal = True
                heal_reason = f"High restarts: {status['restarts']}"
            
            if needs_heal:
                logger.warning(f"⚠️ Pod {status['name']} needs healing: {heal_reason}")
                self.delete_pod(namespace, status["name"])
                actions.append({
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "pod": status["name"],
                    "action": "deleted",
                    "reason": heal_reason
                })
        
        return actions

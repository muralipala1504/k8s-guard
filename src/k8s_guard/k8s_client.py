"""
Kubernetes API Client for k8s-guard
Monitors pods, nodes, and deployments
"""

import os
import time
import logging
from datetime import datetime
from kubernetes import client, config

# Import history module
from .history import save_action

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
        reason = ""
        container_statuses = pod.status.container_statuses or []
        restart_count = 0
        
        if container_statuses:
            for c in container_statuses:
                if c.state.waiting and c.state.waiting.reason:
                    reason = c.state.waiting.reason
                if c.state.terminated and c.state.terminated.reason:
                    reason = c.state.terminated.reason
            restart_count = sum(c.restart_count for c in container_statuses)
        
        return {
            "name": pod.metadata.name,
            "namespace": pod.metadata.namespace,
            "status": status,
            "reason": reason,
            "restarts": restart_count,
            "node": pod.spec.node_name or "unknown",
            "labels": pod.metadata.labels or {}
        }
    
    def get_nodes(self):
        """Get all nodes with full status"""
        try:
            nodes = self.core_v1.list_node()
            result = []
            for node in nodes.items:
                status_parts = []
                for c in node.status.conditions:
                    if c.type == "Ready" and c.status == "True":
                        status_parts.append("Ready")
                if node.spec.unschedulable:
                    status_parts.append("SchedulingDisabled")
                if not status_parts:
                    status_parts.append("Unknown")
                
                result.append({
                    "name": node.metadata.name,
                    "status": ",".join(status_parts),
                    "ready": "Ready" in status_parts,
                    "schedulable": not node.spec.unschedulable,
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
    
    def scale_deployment(self, namespace, name, replicas):
        """Scale a deployment to the specified number of replicas"""
        try:
            self.apps_v1.patch_namespaced_deployment_scale(
                name=name,
                namespace=namespace,
                body={"spec": {"replicas": replicas}}
            )
            logger.info(f"✅ Scaled deployment {name} to {replicas} replicas")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to scale deployment {name}: {e}")
            return False
    
    def delete_pod(self, namespace, name):
        """Delete a pod (triggers auto-restart if part of a deployment)"""
        try:
            self.core_v1.delete_namespaced_pod(name=name, namespace=namespace)
            logger.info(f"🗑️ Deleted pod {name} in namespace {namespace}")
            save_action("delete", "pod", name, "success", "Pod deleted by user")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to delete pod {name}: {e}")
            return False
    
    def auto_heal_pods(self, namespace="default"):
        """Auto-heal failed pods"""
        pods = self.get_pods(namespace)
        actions = []
        failure_conditions = ["CrashLoopBackOff", "ImagePullBackOff", "Error", "Failed", "OOMKilled"]
        
        for pod in pods:
            status = self.get_pod_status(pod)
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
                save_action("delete", "pod", status["name"], "success", heal_reason)
                actions.append({
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "pod": status["name"],
                    "action": "deleted",
                    "reason": heal_reason
                })
        
        return actions
    
    def auto_heal_nodes(self):
        """Auto-heal unhealthy nodes"""
        nodes = self.get_nodes()
        actions = []
        for node in nodes:
            if "NotReady" in node["status"]:
                logger.warning(f"⚠️ Node {node['name']} is NotReady")
                actions.append({
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "node": node["name"],
                    "action": "not_ready",
                    "status": node["status"]
                })
            elif "SchedulingDisabled" in node["status"]:
                logger.warning(f"⚠️ Node {node['name']} is SchedulingDisabled")
                try:
                    import subprocess
                    subprocess.run(["kubectl", "uncordon", node["name"]], check=True)
                    logger.info(f"✅ Uncordoned node {node['name']}")
                    save_action("uncordon", "node", node["name"], "success", "SchedulingDisabled")
                    actions.append({
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "node": node["name"],
                        "action": "uncordoned",
                        "status": node["status"]
                    })
                except Exception as e:
                    logger.error(f"❌ Failed to uncordon {node['name']}: {e}")
        return actions
    
    def auto_scale_deployments(self, namespace="default"):
        """Auto-scale deployments based on pod status"""
        deployments = self.get_deployments(namespace)
        actions = []
        
        for deployment in deployments:
            name = deployment.metadata.name
            replicas = deployment.spec.replicas or 1
            labels = deployment.spec.selector.match_labels
            
            pods = self.get_pods(namespace)
            failing_pods = 0
            total_pods = 0
            
            for pod in pods:
                pod_labels = pod.metadata.labels or {}
                match = True
                for key, value in labels.items():
                    if pod_labels.get(key) != value:
                        match = False
                        break
                
                if match:
                    total_pods += 1
                    status = self.get_pod_status(pod)
                    if status["status"] != "Running" or status["restarts"] > 1:
                        failing_pods += 1
            
            if total_pods > 0 and failing_pods / total_pods > 0.5 and replicas > 1:
                new_replicas = max(1, replicas - 1)
                self.scale_deployment(namespace, name, new_replicas)
                save_action("scale", "deployment", name, "success", f"{replicas}->{new_replicas}")
                actions.append({
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "deployment": name,
                    "action": "scaled_down",
                    "from": replicas,
                    "to": new_replicas
                })
            elif total_pods == 0:
                self.scale_deployment(namespace, name, 1)
                save_action("scale", "deployment", name, "success", "0->1")
                actions.append({
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "deployment": name,
                    "action": "scaled_up",
                    "from": replicas,
                    "to": 1
                })
        
        return actions

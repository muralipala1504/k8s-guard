import os
from pathlib import Path
from dotenv import load_dotenv

class Config:
    """Configuration management for k8s-guard"""
    
    def __init__(self):
        load_dotenv()
        
        # Database
        self.db_path = os.getenv('K8S_GUARD_DB', 
                                 str(Path.home() / '.k8s-guard' / 'history.db'))
        self.history_days_free = 7  # Free tier keeps 7 days
        self.history_days_pro = 0   # 0 = unlimited
        
        # License
        self.license_key = os.getenv('K8S_GUARD_LICENSE', '')
        self.is_pro = self._check_license()
        
        # Slack
        self.slack_webhook = os.getenv('SLACK_WEBHOOK_URL', '')
        
        # Kubernetes
        self.kubeconfig = os.getenv('KUBECONFIG', 
                                    str(Path.home() / '.kube' / 'config'))
        self.in_cluster = os.getenv('K8S_GUARD_IN_CLUSTER', 'false').lower() == 'true'
        
        # Agent settings
        self.check_interval = int(os.getenv('K8S_GUARD_CHECK_INTERVAL', '10'))
        self.namespace = os.getenv('K8S_GUARD_NAMESPACE', '')
    
    def _check_license(self) -> bool:
        """Validate license key - Free tier by default"""
        if not self.license_key:
            return False
        return self.license_key.startswith('PRO-')

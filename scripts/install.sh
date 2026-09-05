#!/bin/bash
# k8s-guard - One-Line Installer
# Usage: curl -sSL https://raw.githubusercontent.com/muralipala1504/k8s-guard/main/scripts/install.sh | bash

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }

echo "═══════════════════════════════════════════════════════════════"
echo "  🛡️ k8s-guard - Kubernetes Auto-Heal Agent"
echo "  Version: 1.0.0"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Auto-install kubectl if missing
if ! command -v kubectl &> /dev/null; then
    print_warning "kubectl is not installed. Installing..."
    curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
    chmod +x kubectl
    sudo mv kubectl /usr/local/bin/
    print_success "kubectl installed"
fi

# Clone repository
cd /home/ruser
if [[ -d "k8s-guard" ]]; then
    print_info "Removing existing installation..."
    rm -rf k8s-guard
fi

print_info "Cloning k8s-guard..."
git clone https://github.com/muralipala1504/k8s-guard.git
cd k8s-guard

# Create virtual environment
print_info "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
print_info "Installing dependencies..."
pip install -r requirements.txt

# Apply SELinux context (if enforcing)
if command -v getenforce &> /dev/null && [[ $(getenforce) == "Enforcing" ]]; then
    print_info "Applying SELinux context..."
    sudo chcon -R -t bin_t /home/ruser/k8s-guard/venv/bin/
    sudo semanage fcontext -a -t bin_t "/home/ruser/k8s-guard/venv/bin(/.*)?" 2>/dev/null || true
    sudo restorecon -Rv /home/ruser/k8s-guard/venv/bin/ 2>/dev/null || true
fi

# Auto-configure kubeconfig
print_info "Configuring Kubernetes access..."
mkdir -p ~/.kube
cat > ~/.kube/config << EOF
apiVersion: v1
clusters:
- cluster:
    server: http://192.168.217.171:8001
    insecure-skip-tls-verify: true
  name: minikube
contexts:
- context:
    cluster: minikube
    user: minikube
  name: minikube
current-context: minikube
kind: Config
preferences: {}
users: []

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

# Create systemd service
print_info "Installing systemd service..."
sudo tee /etc/systemd/system/k8s-guard.service > /dev/null << 'SERVICEEOF'
[Unit]
Description=k8s-guard - Kubernetes Auto-Heal Agent
After=network.target

[Service]
Type=simple
User=ruser
WorkingDirectory=/home/ruser/k8s-guard
Environment="PYTHONPATH=/home/ruser/k8s-guard"
ExecStart=/home/ruser/k8s-guard/venv/bin/python /home/ruser/k8s-guard/dashboard/app.py
Restart=always
RestartSec=10
StandardOutput=append:/var/log/k8s-guard.log
StandardError=append:/var/log/k8s-guard-error.log

[Install]
WantedBy=multi-user.target
SERVICEEOF

sudo systemctl daemon-reload
sudo systemctl enable k8s-guard
sudo systemctl start k8s-guard

print_success "✅ k8s-guard installation complete!"
echo ""
echo "📋 Installation Summary:"
echo "  📁 Location: /home/ruser/k8s-guard"
echo "  🔧 Service: k8s-guard (systemd)"
echo "  📊 Dashboard: http://$(hostname -I | awk '{print $1}'):7860"
echo "  📝 Logs: /var/log/k8s-guard.log"
echo "  🔐 Status: sudo systemctl status k8s-guard"
echo ""
echo "📚 Useful Commands:"
echo "  sudo systemctl status k8s-guard  # Check service status"
echo "  sudo journalctl -u k8s-guard -f  # View logs"
echo ""
echo "🔗 GitHub: https://github.com/muralipala1504/k8s-guard"

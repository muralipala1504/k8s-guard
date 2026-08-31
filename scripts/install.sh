#!/bin/bash
# k8s-guard one-line installer

set -e

echo "🚀 Installing k8s-guard..."

cd ~

if [ ! -d "projects/k8s-guard" ]; then
    mkdir -p projects
    cd projects
    git clone https://github.com/muralipala1504/k8s-guard.git
    cd k8s-guard
else
    cd projects/k8s-guard
    git pull
fi

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -e .

cp .env.example .env

echo "✅ k8s-guard installed successfully!"
echo ""
echo "To start:"
echo "  cd ~/projects/k8s-guard"
echo "  source venv/bin/activate"
echo "  k8s-guard start"

#!/bin/bash
export PYTHONPATH=/home/ruser/projects/k8s-guard
cd /home/ruser/projects/k8s-guard
source venv/bin/activate
exec python dashboard/app.py

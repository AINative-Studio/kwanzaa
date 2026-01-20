#!/usr/bin/env python3
"""
Upload training files to RunPod and start training
Uses RunPod GraphQL API
"""

import os
import sys
import time
import json
import base64
import requests
from pathlib import Path

POD_ID = "m8iue5exvrpa51"
API_KEY = "your-runpod-api-key-here"
API_URL = "https://api.runpod.io/graphql"

def run_command_on_pod(command):
    """Run a command on the pod via GraphQL"""
    query = """
    mutation {
      podRunShellCommand(input: {
        podId: "%s"
        command: "%s"
      }) {
        id
        output
      }
    }
    """ % (POD_ID, command.replace('"', '\\"'))

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    response = requests.post(API_URL, json={"query": query}, headers=headers)
    return response.json()

def main():
    print("[INFO] Starting training setup on pod", POD_ID)

    # Install git and clone repo
    print("[INFO] Installing git...")
    result = run_command_on_pod("apt-get update && apt-get install -y git")
    print(result)

    # For now, let's create the files directly
    print("[INFO] Creating training files on pod...")

    # Upload training config
    with open("backend/training/config/training.yaml") as f:
        config_content = f.read()

    # Create files via echo commands (simple approach)
    commands = [
        "mkdir -p /workspace/backend/training/config",
        "mkdir -p /workspace/data/training",
        f"cat > /workspace/backend/training/config/training.yaml << 'EOF'\n{config_content}\nEOF",
    ]

    for cmd in commands:
        print(f"[INFO] Running: {cmd[:50]}...")
        result = run_command_on_pod(cmd)
        print(result)

    print("[SUCCESS] Setup complete!")

if __name__ == "__main__":
    main()

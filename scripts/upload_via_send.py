#!/usr/bin/env python3
"""Upload training files using runpodctl send"""
import os
import subprocess
import sys

POD_ID = "m8iue5exvrpa51"
RUNPODCTL = "/Users/aideveloper/.local/bin/runpodctl"

print("[INFO] Getting send code...")
# The send command creates a code that you use to receive on the other end
# Start the send process
proc = subprocess.Popen(
    [RUNPODCTL, "send", "/tmp/kwanzaa-training.tar.gz"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

stdout, stderr = proc.communicate()
print("STDOUT:", stdout)
print("STDERR:", stderr)

# Extract the code from output
for line in stdout.split("\n"):
    if "code" in line.lower() or "enter" in line.lower():
        print(f"[INFO] {line}")

print("""
[INFO] Now on the pod's terminal, run:
runpodctl receive

Then enter the code shown above.
""")

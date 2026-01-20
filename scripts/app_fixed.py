#!/usr/bin/env python3
"""
Gradio app that runs training and shows progress
"""
import gradio as gr
import subprocess
import threading
import time

training_log = []
training_status = "Not Started"

def run_training():
    global training_log, training_status
    training_status = "Running"
    training_log = ["Starting training...\n"]

    process = subprocess.Popen(
        ["python3", "train.py"],  # Use python3 explicitly
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    for line in iter(process.stdout.readline, ''):
        if line:
            training_log.append(line)
            # Keep only last 1000 lines
            if len(training_log) > 1000:
                training_log = training_log[-1000:]

    process.wait()

    if process.returncode == 0:
        training_status = "Completed"
        training_log.append("\n✅ Training completed successfully!\n")
        training_log.append("\nAdapter saved to HuggingFace Hub:\n")
        training_log.append("https://huggingface.co/ainativestudio/kwanzaa-adapter-v1\n")
    else:
        training_status = "Failed"
        training_log.append(f"\n❌ Training failed with code {process.returncode}\n")

def start_training():
    thread = threading.Thread(target=run_training, daemon=True)
    thread.start()
    time.sleep(2)
    return get_logs()

def get_logs():
    return f"Status: {training_status}\n\n{''.join(training_log)}"

with gr.Blocks(title="Kwanzaa Adapter Training") as demo:
    gr.Markdown("# Kwanzaa Adapter Training")
    gr.Markdown("Train Llama-3.2-1B with LoRA adapters for Kwanzaa knowledge")
    gr.Markdown("**GPU:** A10G-large (22GB VRAM)")
    gr.Markdown("**Training Time:** ~10-15 minutes")

    with gr.Row():
        start_btn = gr.Button("🚀 Start Training", variant="primary", size="lg")
        refresh_btn = gr.Button("🔄 Refresh Logs")

    status_text = gr.Markdown("**Status:** Not Started")

    logs_box = gr.Textbox(
        label="Training Logs",
        lines=30,
        max_lines=50,
        interactive=False
    )

    start_btn.click(fn=start_training, outputs=logs_box)
    refresh_btn.click(fn=get_logs, outputs=logs_box)

    # Auto-refresh every 5 seconds
    demo.load(fn=get_logs, outputs=logs_box, every=5)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)

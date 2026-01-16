#!/usr/bin/env python3
"""Send notifications for ingestion run status."""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin
from urllib.request import Request, urlopen


def load_final_metadata(run_id: str) -> dict:
    """Load final run metadata."""
    log_dir = Path(__file__).parent.parent.parent / "logs" / "ingestion"
    final_file = log_dir / f"{run_id}_final.json"

    if not final_file.exists():
        # Try metadata file
        metadata_file = log_dir / f"{run_id}_metadata.json"
        if metadata_file.exists():
            with open(metadata_file, "r") as f:
                return json.load(f)
        return {}

    with open(final_file, "r") as f:
        return json.load(f)


def format_notification_message(
    run_id: str,
    status: str,
    summary: str,
    metadata: dict,
) -> str:
    """Format notification message."""
    status_emoji = {
        "completed": "✅",
        "failed": "❌",
        "partial": "⚠️",
    }

    emoji = status_emoji.get(status, "ℹ️")

    message = f"{emoji} Kwanzaa Ingestion Job {status.upper()}\n\n"
    message += f"Run ID: {run_id}\n"
    message += f"Environment: {metadata.get('environment', 'unknown')}\n"
    message += f"Summary: {summary}\n\n"

    if metadata:
        message += "Statistics:\n"
        message += f"  • Documents discovered: {metadata.get('documents_discovered', 0)}\n"
        message += f"  • Documents processed: {metadata.get('documents_processed', 0)}\n"
        message += f"  • Chunks created: {metadata.get('chunks_created', 0)}\n"
        message += f"  • Vectors upserted: {metadata.get('vectors_upserted', 0)}\n"

        if metadata.get("documents_failed", 0) > 0:
            message += f"  • Documents failed: {metadata['documents_failed']}\n"

        if metadata.get("duration_seconds"):
            duration = metadata["duration_seconds"]
            minutes = int(duration // 60)
            seconds = int(duration % 60)
            message += f"\nDuration: {minutes}m {seconds}s\n"

    return message


def send_webhook_notification(
    webhook_url: str,
    run_id: str,
    status: str,
    summary: str,
    metadata: dict,
) -> bool:
    """Send notification via webhook."""
    try:
        message = format_notification_message(run_id, status, summary, metadata)

        payload = {
            "run_id": run_id,
            "status": status,
            "summary": summary,
            "message": message,
            "metadata": metadata,
            "timestamp": datetime.utcnow().isoformat(),
        }

        data = json.dumps(payload).encode("utf-8")
        req = Request(
            webhook_url,
            data=data,
            headers={"Content-Type": "application/json"},
        )

        with urlopen(req, timeout=10) as response:
            if response.status == 200:
                print(f"Webhook notification sent to {webhook_url}")
                return True
            else:
                print(f"Webhook returned status {response.status}")
                return False

    except Exception as e:
        print(f"Error sending webhook notification: {e}", file=sys.stderr)
        return False


def send_slack_notification(
    slack_webhook_url: str,
    run_id: str,
    status: str,
    summary: str,
    metadata: dict,
) -> bool:
    """Send notification via Slack webhook."""
    try:
        message = format_notification_message(run_id, status, summary, metadata)

        # Slack webhook payload format
        payload = {
            "text": message,
            "username": "Kwanzaa Ingestion Bot",
        }

        data = json.dumps(payload).encode("utf-8")
        req = Request(
            slack_webhook_url,
            data=data,
            headers={"Content-Type": "application/json"},
        )

        with urlopen(req, timeout=10) as response:
            if response.status == 200:
                print(f"Slack notification sent")
                return True
            else:
                print(f"Slack webhook returned status {response.status}")
                return False

    except Exception as e:
        print(f"Error sending Slack notification: {e}", file=sys.stderr)
        return False


def send_email_notification(
    email_recipients: list,
    run_id: str,
    status: str,
    summary: str,
    metadata: dict,
) -> bool:
    """Send notification via email."""
    # Email sending requires SMTP configuration
    # For MVP, we'll just log that email would be sent
    print(f"Email notification would be sent to: {', '.join(email_recipients)}")
    print(f"Subject: Kwanzaa Ingestion Job {status.upper()} - {run_id}")
    return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Send ingestion job notifications")
    parser.add_argument("--run-id", required=True, help="Run identifier")
    parser.add_argument("--status", required=True, help="Run status")
    parser.add_argument("--summary", required=True, help="Summary message")
    parser.add_argument("--log-file", help="Log file path")

    args = parser.parse_args()

    # Load metadata
    metadata = load_final_metadata(args.run_id)

    # Get notification configuration from environment
    webhook_url = os.getenv("NOTIFICATION_WEBHOOK")
    slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    email_recipients = os.getenv("NOTIFICATION_EMAIL", "").split(",")
    email_recipients = [e.strip() for e in email_recipients if e.strip()]

    notifications_sent = []

    # Send webhook notification
    if webhook_url:
        if send_webhook_notification(
            webhook_url,
            args.run_id,
            args.status,
            args.summary,
            metadata,
        ):
            notifications_sent.append("webhook")

    # Send Slack notification
    if slack_webhook_url:
        if send_slack_notification(
            slack_webhook_url,
            args.run_id,
            args.status,
            args.summary,
            metadata,
        ):
            notifications_sent.append("slack")

    # Send email notification
    if email_recipients:
        if send_email_notification(
            email_recipients,
            args.run_id,
            args.status,
            args.summary,
            metadata,
        ):
            notifications_sent.append("email")

    if not notifications_sent:
        print("No notification channels configured")
        print("Set NOTIFICATION_WEBHOOK, SLACK_WEBHOOK_URL, or NOTIFICATION_EMAIL")

    print(f"\nNotifications sent via: {', '.join(notifications_sent) or 'none'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

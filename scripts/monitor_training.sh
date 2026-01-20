#!/bin/bash

export HF_TOKEN="your-huggingface-token-here"
SPACE_ID="ainativestudio/kwanzaa-training"

echo "=================================================="
echo "Monitoring HuggingFace Space: $SPACE_ID"
echo "Checking every 5 minutes..."
echo "=================================================="
echo ""

while true; do
    TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
    echo "[$TIMESTAMP] Checking status..."

    STATUS=$(curl -s -H "Authorization: Bearer $HF_TOKEN" \
        "https://huggingface.co/api/spaces/$SPACE_ID" | \
        python3 -c "import sys, json; data=json.load(sys.stdin); print(data['runtime']['stage'])" 2>/dev/null)

    if [ -z "$STATUS" ]; then
        echo "  Status: Unable to fetch (API error)"
    else
        echo "  Status: $STATUS"

        if [ "$STATUS" = "RUNNING" ]; then
            echo "  ✓ Space is RUNNING!"
            echo "  → Open: https://huggingface.co/spaces/$SPACE_ID"
            echo "  → Click 'Start Training' button when you see the interface"
            break
        elif [ "$STATUS" = "RUNTIME_ERROR" ]; then
            echo "  ✗ Space has an error - checking logs..."
            break
        elif [ "$STATUS" = "RUNNING_BUILDING" ] || [ "$STATUS" = "RUNNING_APP_STARTING" ]; then
            echo "  ⏳ Still building/starting..."
        else
            echo "  → Current stage: $STATUS"
        fi
    fi

    echo "  Next check in 5 minutes..."
    echo ""
    sleep 300  # 5 minutes
done

echo ""
echo "=================================================="
echo "Monitoring stopped. Check the Space manually:"
echo "https://huggingface.co/spaces/$SPACE_ID"
echo "=================================================="

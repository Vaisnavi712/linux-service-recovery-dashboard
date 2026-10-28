#!/bin/bash

SERVICE="test-web.service"
LOG_FILE="/home/iot/service-recovery-project/logs/recovery.log"

echo "----------------------------------------" >> "$LOG_FILE"
echo "Time: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"

if systemctl is-active --quiet "$SERVICE"; then
    echo "Status: HEALTHY - $SERVICE is running" >> "$LOG_FILE"
    echo "$SERVICE is running normally."
else
    echo "Status: FAILURE - $SERVICE is stopped" >> "$LOG_FILE"
    echo "$SERVICE has stopped. Attempting restart..."

    if systemctl restart "$SERVICE" && sleep 2 &&
       systemctl is-active --quiet "$SERVICE"; then
        echo "Recovery: SUCCESS - Service restarted" >> "$LOG_FILE"
        echo "Recovery successful!"
    else
        echo "Recovery: FAILED - Service is still inactive" >> "$LOG_FILE"
        echo "Recovery failed. Check service logs."
    fi
fi

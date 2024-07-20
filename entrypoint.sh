#!/bin/sh

if [ "$RUN_MODE" = "producer" ]; then
    exec python3 main.py
elif [ "$RUN_MODE" = "consumer" ]; then
    echo "Delaying consumer startup to wait for producer..."
    sleep 30  # Adjust the delay as needed
    exec python3 consumer.py
else
    echo "Unknown RUN_MODE: $RUN_MODE"
    exit 1
fi
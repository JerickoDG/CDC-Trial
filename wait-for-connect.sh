#!/bin/bash

echo "Waiting for Kafka Connect to start..."
while ! curl -s http://localhost:8083/connectors > /dev/null; do
  echo "Kafka Connect not available yet - sleeping 10 seconds"
  sleep 10
done

echo "Kafka Connect is up! Proceeding with connector setup..."
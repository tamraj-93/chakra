#!/bin/bash

echo "Restarting frontend with API format compatibility fixes..."
cd /home/nilabh/Projects/chakra
./restart_frontend.sh

echo "Waiting for the frontend to restart..."
sleep 5

echo "Done! The chat box in the SLA template view should now be working properly."
echo "The frontend now handles both API response formats correctly."
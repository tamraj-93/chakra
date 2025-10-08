#!/bin/bash

echo "Restarting frontend after chat box fixes..."
cd /home/nilabh/Projects/chakra
./restart_frontend.sh

echo "Waiting for the frontend to restart..."
sleep 5

echo "Done! The chat box in the SLA template view should now be working properly."
echo "If you still encounter issues, you may need to clear your browser cache or do a hard refresh."
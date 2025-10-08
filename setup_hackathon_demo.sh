#!/bin/bash

# Demo script for the hackathon that creates example consultations with enhanced visualization

echo "╔═════════════════════════════════════════════════════════════════╗"
echo "║                 CHAKRA HACKATHON DEMO SETUP                     ║"
echo "║     Creating example consultations with structured data         ║"
echo "╚═════════════════════════════════════════════════════════════════╝"

# Create the demo examples
echo -e "\n[1/2] Creating Healthcare SLA demo with enhanced visualization..."
./examples/create_demo_visualization.sh

echo -e "\n[2/2] Creating Infrastructure SLA demo with advanced visualization..."
./examples/create_infrastructure_sla_demo.sh

echo -e "\n✅ Demo examples created successfully!"
echo -e "\nAccess the frontend application to see the enhanced visualization."
echo -e "Navigate to the consultations list to view the examples.\n"
echo -e "Demo Consultations Created:"
echo -e "  1. Healthcare Cloud SLA Demo - Enhanced Visualization"
echo -e "  2. Infrastructure SLA Demo - Advanced Visualization\n"
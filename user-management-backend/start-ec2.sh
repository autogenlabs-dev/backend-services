#!/bin/bash

# Simple EC2 Startup Script
echo "🚀 Starting User Management Backend on EC2..."

# Navigate to project directory
cd ~/backend-services/user-management-backend

# Make deployment script executable
chmod +x ec2-deploy.sh

# Run the deployment script
./ec2-deploy.sh

echo "✅ Deployment script executed!"

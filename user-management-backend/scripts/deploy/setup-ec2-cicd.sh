#!/bin/bash

# Quick Setup Script for EC2 Instance: 13.234.18.159
# Instance ID: i-0d9d2fd36b0527c07

echo "🚀 Setting up CI/CD for EC2 Instance: 13.234.18.159"

# EC2 Details
EC2_HOST="13.234.18.159"
EC2_USER="ubuntu"
EC2_DNS="ec2-13-234-18-159.ap-south-1.compute.amazonaws.com"

echo "📋 Your EC2 Instance Details:"
echo "  Public IP: $EC2_HOST"
echo "  DNS Name: $EC2_DNS"
echo "  SSH User: $EC2_USER"
echo "  Instance ID: i-0d9d2fd36b0527c07"

echo ""
echo "🔐 GitHub Secrets to Add:"
echo "Go to: https://github.com/autogenlabs-dev/backend-services/settings/secrets/actions"
echo ""
echo "1. EC2_HOST"
echo "   Value: $EC2_HOST"
echo ""
echo "2. EC2_USER"
echo "   Value: $EC2_USER"
echo ""
echo "3. EC2_SSH_PRIVATE_KEY"
echo "   Value: [Content of your autogenlabs.pem file]"
echo ""

echo "📁 To get your private key content:"
echo "cat autogenlabs.pem"
echo ""

echo "🧪 Test your SSH connection:"
echo "ssh -i autogenlabs.pem ubuntu@$EC2_HOST"
echo ""

echo "🔧 Initial EC2 Setup Commands:"
echo "1. Connect to your EC2:"
echo "   ssh -i autogenlabs.pem ubuntu@$EC2_HOST"
echo ""
echo "2. Run on EC2:"
echo "   sudo apt update && sudo apt upgrade -y"
echo "   sudo apt install -y python3-pip python3-venv nginx redis-server git curl"
echo ""
echo "3. Clone your repository:"
echo "   git clone https://github.com/autogenlabs-dev/backend-services.git"
echo ""
echo "4. Setup the application:"
echo "   cd backend-services/user-management-backend"
echo "   chmod +x ec2-deploy.sh"
echo "   ./ec2-deploy.sh"
echo ""

echo "🚀 After setup, test deployment with:"
echo "   export EC2_HOST=$EC2_HOST"
echo "   ./deploy-manager.sh status"
echo ""

echo "✅ Setup information ready!"
echo "📖 See CICD_SETUP.md for detailed instructions"

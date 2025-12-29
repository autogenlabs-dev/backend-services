#!/bin/bash
# EC2 Setup Script for User Management API
# Run this on your EC2 instance: i-0b65b244ab0990c4d

echo "🚀 Setting up EC2 instance for User Management API deployment..."

# Update system
sudo yum update -y

# Install Docker
sudo yum install docker -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ec2-user

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Create directories
mkdir -p /home/ec2-user/app
mkdir -p /home/ec2-user/data/mongodb
mkdir -p /home/ec2-user/data/redis

# Set permissions
sudo chown -R ec2-user:ec2-user /home/ec2-user/

echo "✅ EC2 setup complete!"
echo "📝 Next steps:"
echo "1. Configure GitHub secrets with your EC2 details"
echo "2. Push code to trigger deployment"
echo "3. Access your API at: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8000"

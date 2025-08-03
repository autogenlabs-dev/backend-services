#!/bin/bash
# Deploy User Management API to EC2
# Usage: ./deploy.sh

echo "🚀 Deploying User Management API to EC2..."

# Set your EC2 details
EC2_USER="ec2-user"
PEM_FILE="autogen (1).pem"

# Get EC2 public IP (you'll need to replace this with actual IP)
read -p "Enter your EC2 public IP address: " EC2_IP

echo "📋 Using EC2 IP: $EC2_IP"

# Set correct permissions for PEM file
chmod 400 "$PEM_FILE"

# Test connection
echo "🔗 Testing SSH connection..."
ssh -i "$PEM_FILE" -o ConnectTimeout=10 $EC2_USER@$EC2_IP "echo 'Connection successful!'"

if [ $? -eq 0 ]; then
    echo "✅ SSH connection successful!"
    
    # Copy files to EC2
    echo "📁 Copying files to EC2..."
    scp -i "$PEM_FILE" -r user-management-backend/ $EC2_USER@$EC2_IP:~/
    
    # Run deployment commands on EC2
    echo "🚀 Running deployment on EC2..."
    ssh -i "$PEM_FILE" $EC2_USER@$EC2_IP << 'EOF'
        cd ~/user-management-backend
        
        # Update system and install Docker
        sudo yum update -y
        sudo yum install docker -y
        sudo systemctl start docker
        sudo systemctl enable docker
        sudo usermod -a -G docker ec2-user
        
        # Install Docker Compose
        sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
        
        # Build and run containers
        docker build -t user-management-api:latest .
        docker-compose up -d
        
        echo "✅ Deployment complete!"
        echo "🌐 Your API is now running at: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8000"
        echo "📚 API Documentation: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8000/docs"
        
        # Show running containers
        docker ps
EOF
    
    echo "🎉 Deployment completed successfully!"
else
    echo "❌ SSH connection failed. Please check:"
    echo "1. EC2 instance is running"
    echo "2. Security group allows SSH (port 22)"
    echo "3. PEM file permissions are correct"
    echo "4. EC2 public IP is correct"
fi

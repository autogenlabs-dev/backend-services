#!/bin/bash

# Deployment Management Script
# Usage: ./deploy-manager.sh [setup|deploy|rollback|status|logs]

set -e

# Configuration
EC2_HOST="${EC2_HOST:-your-ec2-ip}"
EC2_USER="${EC2_USER:-ubuntu}"
PROJECT_PATH="~/backend-services/user-management-backend"
SERVICE_NAME="user-management-backend"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to check if EC2 is reachable
check_ec2_connection() {
    log_info "Checking EC2 connection..."
    if ssh -o ConnectTimeout=10 ${EC2_USER}@${EC2_HOST} "echo 'Connected successfully'"; then
        log_success "EC2 connection successful"
        return 0
    else
        log_error "Failed to connect to EC2. Please check your SSH configuration."
        return 1
    fi
}

# Setup function
setup_ec2() {
    log_info "Setting up EC2 environment..."
    
    if ! check_ec2_connection; then
        exit 1
    fi
    
    ssh ${EC2_USER}@${EC2_HOST} << 'EOF'
        # Update system
        sudo apt update && sudo apt upgrade -y
        
        # Install required packages
        sudo apt install -y python3-pip python3-venv nginx redis-server git curl
        
        # Clone repository if not exists
        if [ ! -d "backend-services" ]; then
            git clone https://github.com/autogenlabs-dev/backend-services.git
        fi
        
        cd backend-services/user-management-backend
        
        # Create virtual environment
        python3 -m venv venv
        source venv/bin/activate
        
        # Install dependencies
        pip install -r requirements.txt
        
        echo "✅ EC2 setup completed!"
EOF
    
    log_success "EC2 setup completed!"
}

# Deploy function
deploy() {
    log_info "Starting deployment..."
    
    if ! check_ec2_connection; then
        exit 1
    fi
    
    ssh ${EC2_USER}@${EC2_HOST} << EOF
        cd ${PROJECT_PATH}
        
        # Pull latest changes
        git pull origin main
        
        # Backup current environment
        if [ -f .env.production ]; then
            cp .env.production .env.production.backup.\$(date +%Y%m%d_%H%M%S)
        fi
        
        # Activate virtual environment
        source venv/bin/activate
        
        # Update dependencies
        pip install -r requirements.txt
        
        # Run migrations
        alembic upgrade head
        
        # Restart services
        sudo systemctl restart ${SERVICE_NAME}
        sudo systemctl restart nginx
        
        # Wait and check status
        sleep 5
        sudo systemctl status ${SERVICE_NAME} --no-pager
        
        echo "✅ Deployment completed!"
EOF
    
    log_success "Deployment completed!"
}

# Rollback function
rollback() {
    log_warning "Starting rollback..."
    
    if ! check_ec2_connection; then
        exit 1
    fi
    
    ssh ${EC2_USER}@${EC2_HOST} << EOF
        cd ${PROJECT_PATH}
        
        # Find latest backup
        BACKUP_FILE=\$(ls -t .env.production.backup.* 2>/dev/null | head -n1)
        
        if [ -n "\$BACKUP_FILE" ]; then
            echo "Restoring from: \$BACKUP_FILE"
            cp "\$BACKUP_FILE" .env.production
        fi
        
        # Reset to previous commit
        git reset --hard HEAD~1
        
        # Restart services
        sudo systemctl restart ${SERVICE_NAME}
        sudo systemctl restart nginx
        
        echo "⚠️  Rollback completed!"
EOF
    
    log_warning "Rollback completed!"
}

# Status function
status() {
    log_info "Checking service status..."
    
    if ! check_ec2_connection; then
        exit 1
    fi
    
    ssh ${EC2_USER}@${EC2_HOST} << EOF
        echo "=== Service Status ==="
        sudo systemctl status ${SERVICE_NAME} --no-pager
        
        echo ""
        echo "=== Nginx Status ==="
        sudo systemctl status nginx --no-pager
        
        echo ""
        echo "=== Redis Status ==="
        sudo systemctl status redis-server --no-pager
        
        echo ""
        echo "=== Port Status ==="
        ss -tlnp | grep -E ':80|:8000|:6379'
        
        echo ""
        echo "=== Disk Usage ==="
        df -h | grep -E '/|home'
        
        echo ""
        echo "=== Memory Usage ==="
        free -h
EOF
}

# Logs function
logs() {
    log_info "Showing application logs..."
    
    if ! check_ec2_connection; then
        exit 1
    fi
    
    ssh ${EC2_USER}@${EC2_HOST} "sudo journalctl -u ${SERVICE_NAME} -f --since '1 hour ago'"
}

# Health check function
health_check() {
    log_info "Performing health check..."
    
    # Check if service is reachable
    if curl -f -s "http://${EC2_HOST}/health" > /dev/null; then
        log_success "Health check passed - Application is responding"
    else
        log_error "Health check failed - Application may be down"
        return 1
    fi
}

# Main function
main() {
    case "${1:-}" in
        setup)
            setup_ec2
            ;;
        deploy)
            deploy
            health_check
            ;;
        rollback)
            rollback
            health_check
            ;;
        status)
            status
            ;;
        logs)
            logs
            ;;
        health)
            health_check
            ;;
        *)
            echo "Usage: $0 {setup|deploy|rollback|status|logs|health}"
            echo ""
            echo "Commands:"
            echo "  setup    - Initial EC2 environment setup"
            echo "  deploy   - Deploy latest changes"
            echo "  rollback - Rollback to previous version"
            echo "  status   - Check service status"
            echo "  logs     - View application logs"
            echo "  health   - Perform health check"
            echo ""
            echo "Environment variables:"
            echo "  EC2_HOST - Your EC2 public IP or domain"
            echo "  EC2_USER - SSH user (default: ubuntu)"
            exit 1
            ;;
    esac
}

main "$@"

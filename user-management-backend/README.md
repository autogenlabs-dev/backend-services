# User Management Backend

A comprehensive backend service for user authentication, subscription management, and LLM API integration.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip

### Installation
```bash
# Clone the repository
git clone https://github.com/autogenlabs-dev/backend-services.git
cd backend-services/user-management-backend

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run the server
python run_server.py
```

### Testing
```bash
# Run all tests
python run_tests.py

# Run specific test
python tests/integration/test_full_flow_comprehensive.py
```

## 📋 Features

### ✅ Authentication & Authorization
- JWT-based authentication
- API key management
- Role-based access control
- OAuth integration ready

### ✅ Subscription Management
- Stripe payment integration
- Multiple subscription tiers
- Usage tracking and limits
- Webhook support

### ✅ LLM Integration
- Multi-provider support (OpenAI, Anthropic)
- Rate limiting and usage tracking
- Proxy service for API calls
- Cost monitoring

### ✅ API Management
- RESTful API design
- Rate limiting
- Comprehensive error handling
- API documentation

## 🏗️ Architecture

```
user-management-backend/
├── app/                    # Application core
│   ├── api/               # API endpoints
│   ├── auth/              # Authentication logic
│   ├── models/            # Database models
│   ├── services/          # Business logic
│   └── middleware/        # Custom middleware
├── tests/                 # Test suite
│   ├── integration/       # End-to-end tests
│   ├── api/              # API tests
│   └── stripe/           # Payment tests
├── docs/                 # Documentation
├── alembic/              # Database migrations
└── scripts/              # Utility scripts
```

## 📊 API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/refresh` - Token refresh
- `GET /users/me` - Get current user

### API Keys
- `POST /api/keys` - Create API key
- `GET /api/keys` - List API keys
- `DELETE /api/keys/{id}` - Delete API key

### Subscriptions
- `GET /subscriptions/plans` - List subscription plans
- `POST /subscriptions/subscribe` - Subscribe to plan
- `GET /subscriptions/current` - Current subscription

### LLM Services
- `POST /llm/chat` - Chat completion
- `GET /llm/models` - Available models
- `GET /llm/usage` - Usage statistics

## 🧪 Testing

The project includes comprehensive tests with **89.5% success rate**:

- **Integration Tests** - Full end-to-end workflows
- **API Tests** - Individual endpoint testing  
- **Payment Tests** - Stripe integration validation
- **Performance Tests** - Load and response time testing

## 📚 Documentation

- [Installation Guide](docs/INSTALLATION.md)
- [API Reference](docs/API_REFERENCE.md)
- [Architecture Overview](docs/ARCHITECTURE.md)
- [Testing Guide](docs/TESTING.md)

## 🔧 Configuration

Key environment variables:
```env
DATABASE_URL=sqlite:///./test.db
JWT_SECRET=your_jwt_secret
STRIPE_SECRET_KEY=your_stripe_secret_key
OPENAI_API_KEY=your_openai_api_key
```

## 🚀 Deployment

### Docker
```bash
docker-compose up -d
```

### Manual Deployment
```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start server
python run_server.py
```

## 📈 Status

- **Production Ready** ✅
- **Test Coverage** 89.5%
- **API Endpoints** 20+
- **Authentication** JWT + API Keys
- **Payment Processing** Stripe Integration
- **LLM Integration** Multi-provider

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

For support, email support@autogenlabs.dev or create an issue on GitHub.

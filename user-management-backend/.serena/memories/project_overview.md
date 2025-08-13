# AutogenLabs User Management Backend - Project Overview

## Project Purpose
This is the backend service for AutogenLabs, a marketplace platform for AI-powered templates and components. The system provides:

- **User Authentication & Authorization** - Multi-role system (User/Developer/Admin)
- **Content Management** - Templates and components marketplace with approval workflow
- **Admin Dashboard** - Comprehensive management system for platform oversight
- **Payment Integration** - Razorpay integration for marketplace transactions
- **Developer Tools** - API for content creation and management

## Tech Stack

### Backend Framework
- **FastAPI** - Modern Python web framework for building APIs
- **Uvicorn** - ASGI server for running FastAPI applications
- **Python 3.8+** - Core programming language

### Database & ODM
- **MongoDB** - Primary database for all data storage
- **Beanie** - Python ODM (Object Document Mapper) for MongoDB
- **Motor** - Async MongoDB driver
- **PyMongo** - MongoDB driver for Python

### Authentication & Security
- **JWT (PyJWT)** - JSON Web Tokens for authentication
- **BCrypt** - Password hashing and verification
- **Passlib** - Password handling utilities

### Payment Processing
- **Razorpay** - Indian payment gateway integration
- **Stripe** - International payment processing

### Caching & Session Management
- **Redis** - Caching and session storage

### Development & Testing
- **Pydantic** - Data validation and settings management
- **Python-multipart** - File upload handling
- **HTTPX** - HTTP client for testing and external API calls

## Current Phase Status
- **Phase 1**: ✅ Enhanced Role-Based System (Complete)
- **Phase 2**: ✅ Admin Dashboard & Management System (Complete)
- **Phase 3**: 🔄 Enhanced Comment System (Next)

## Architecture Overview
- **Modular Structure** - Organized into models, services, middleware, and API modules
- **Role-Based Access Control** - Three-tier permission system
- **Content Approval Workflow** - Admin-moderated content publishing
- **Audit Logging** - Complete action tracking for compliance
- **Email Notifications** - Event-driven communication system
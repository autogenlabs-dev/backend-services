# AWS Secrets Setup Guide

## 🔐 GitHub Secrets to Add

Go to: https://github.com/autogenlabs-dev/backend-services/settings/secrets/actions

Click "New repository secret" and add these **5 secrets**:

### 1. EC2_HOST
```
13.234.18.159
```

### 2. EC2_USER
```
ubuntu
```

### 3. EC2_SSH_PRIVATE_KEY
```
[Content of your autogenlabs.pem file - copy everything including BEGIN and END lines]
```

### 4. AWS_ACCESS_KEY_ID
```
[Your AWS Access Key ID: AKIA...]
```

### 5. AWS_SECRET_ACCESS_KEY
```
[Your AWS Secret Access Key from AWS Console]
```

## 🔑 How to Get AWS Keys

1. **Go to AWS Console**: https://console.aws.amazon.com/
2. **Navigate to IAM**: Search for "IAM"
3. **Create a new user** (or use existing):
   - User name: `github-actions-user`
   - Attach policies: `EC2FullAccess`, `CloudWatchLogsFullAccess`
4. **Create Access Key**:
   - Go to "Security credentials" tab
   - Click "Create access key"
   - Choose "Application running outside AWS"
   - Copy the Access Key ID and Secret Access Key

## 🚀 Available Deployment Workflows

You now have **2 deployment options**:

### Option 1: Simple EC2 Deployment
- **File**: `user-management-backend/.github/workflows/deploy.yml`
- **Requires**: EC2_HOST, EC2_USER, EC2_SSH_PRIVATE_KEY
- **Triggers**: Push to main branch
- **Best for**: Simple deployments

### Option 2: AWS-Integrated EC2 Deployment  
- **File**: `.github/workflows/aws.yml`
- **Requires**: All 5 secrets above
- **Triggers**: Push to main branch with changes in `user-management-backend/`
- **Best for**: AWS-managed infrastructure

## 🧪 Testing Your Setup

After adding the secrets:

1. **Push any change** to main branch
2. **Go to GitHub Actions**: https://github.com/autogenlabs-dev/backend-services/actions
3. **Watch both workflows** run (if both are triggered)
4. **Test endpoints** after deployment:
   - Health: http://13.234.18.159/health
   - Main: http://13.234.18.159/
   - Docs: http://13.234.18.159/docs

## ⚠️ Important Security Notes

1. **Never commit AWS keys** to git repositories
2. **These keys have full EC2 access** to your AWS account
3. **Consider using IAM roles** for better security in production
4. **Rotate keys regularly** for security

## 🔧 Troubleshooting

If deployment fails:
- Check GitHub Actions logs for detailed errors
- Verify all 5 secrets are added correctly
- Ensure EC2 instance is running and accessible
- Check SSH key format (must include BEGIN/END lines)

## 🎯 Next Steps

1. ✅ Add all 5 GitHub secrets manually - **COMPLETED**
2. ✅ Make a small change and push to main - **TESTING NOW**
3. ✅ Watch GitHub Actions deploy automatically
4. ✅ Test your deployed application

## 📋 Your Specific Values (Add these to GitHub Secrets)

- **EC2_HOST**: `13.234.18.159`
- **EC2_USER**: `ubuntu`
- **AWS_ACCESS_KEY_ID**: `AKIA[REDACTED]` ← Add this manually to GitHub
- **AWS_SECRET_ACCESS_KEY**: `[REDACTED]` ← Add this manually to GitHub
- **EC2_SSH_PRIVATE_KEY**: Content of your `autogenlabs.pem` file

> ⚠️ **Security Note**: Actual credentials have been redacted for security. Use the values provided separately.

# GitHub Secrets Configuration

This document outlines all the GitHub secrets that need to be configured for the CI/CD pipeline to work properly.

## Required Secrets for CI (Testing)

These secrets are used during the CI pipeline for testing. If not set, the pipeline will use default test values.

### Application Secrets
- `SECRET_KEY` - JWT signing key (default: test-secret-key-for-ci)
- `REFRESH_SECRET_KEY` - JWT refresh token signing key (default: test-refresh-secret-key)
- `FIRST_SUPERUSER` - Admin email for testing (default: admin@example.com)
- `FIRST_SUPERUSER_PASSWORD` - Admin password for testing (default: adminpass)
- `PROJECT_NAME` - Application name (default: News Portal CI)

### Email Configuration (Optional)
- `SMTP_TLS` - SMTP TLS enabled (default: true)
- `SMTP_SSL` - SMTP SSL enabled (default: false)
- `SMTP_PORT` - SMTP port (default: 587)
- `SMTP_HOST` - SMTP server hostname
- `SMTP_USER` - SMTP username
- `SMTP_PASSWORD` - SMTP password
- `EMAILS_FROM_EMAIL` - From email address
- `EMAILS_FROM_NAME` - From name

### OAuth Configuration (Optional)
- `GOOGLE_CLIENT_ID` - Google OAuth client ID
- `GOOGLE_CLIENT_SECRET` - Google OAuth client secret
- `FACEBOOK_CLIENT_ID` - Facebook OAuth client ID
- `FACEBOOK_CLIENT_SECRET` - Facebook OAuth client secret
- `TWITTER_CLIENT_ID` - Twitter OAuth client ID
- `TWITTER_CLIENT_SECRET` - Twitter OAuth client secret
- `GITHUB_CLIENT_ID` - GitHub OAuth client ID
- `GITHUB_CLIENT_SECRET` - GitHub OAuth client secret

### Frontend Configuration
- `FRONTEND_URL` - Frontend application URL (default: http://localhost:3000)

## Required Secrets for CD (Deployment)

These secrets are required for the deployment pipeline to work. They must be set for the CD job to run.

### VPS Connection
- `VPS_HOST` - Your VPS IP address or domain name
- `VPS_USER` - SSH username for your VPS
- `VPS_SSH_KEY` - Private SSH key for connecting to your VPS
- `VPS_PORT` - SSH port (default: 22)

## How to Set Up Secrets

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret with its name and value

## Example Secret Values

### For Testing (CI)
```
SECRET_KEY=your-super-secret-jwt-key-here
FIRST_SUPERUSER=test@example.com
FIRST_SUPERUSER_PASSWORD=testpass123
PROJECT_NAME=News Portal
FRONTEND_URL=http://localhost:3000
```

### For Deployment (CD)
```
VPS_HOST=your-vps-ip-or-domain.com
VPS_USER=ubuntu
VPS_SSH_KEY=-----BEGIN OPENSSH PRIVATE KEY-----
...
-----END OPENSSH PRIVATE KEY-----
VPS_PORT=22
```

## Security Notes

- **Never commit secrets to code** - Always use GitHub secrets
- **Rotate secrets regularly** - Change keys periodically
- **Use strong, unique values** - Especially for SECRET_KEY
- **Limit secret access** - Only repository admins should manage secrets
- **Monitor secret usage** - Check GitHub's security tab for any exposed secrets

## Generating SSH Keys

To generate an SSH key pair for VPS access:

```bash
# Generate a new SSH key pair
ssh-keygen -t ed25519 -C "github-actions@yourdomain.com" -f ~/.ssh/github_actions

# Copy the public key to your VPS
ssh-copy-id -i ~/.ssh/github_actions.pub user@your-vps-ip

# The private key content goes into VPS_SSH_KEY secret
cat ~/.ssh/github_actions
```

## Testing Secrets

You can verify secrets are working by:

1. Running a test workflow manually
2. Checking the workflow logs for any missing secret warnings
3. Using the health check endpoint after deployment

## Troubleshooting

### Common Issues

1. **"Secret not found" errors**
   - Check that the secret name matches exactly (case-sensitive)
   - Ensure the secret is created in the correct repository
   - Verify the secret value doesn't have extra whitespace

2. **SSH connection failures**
   - Verify VPS_HOST, VPS_USER, and VPS_PORT are correct
   - Ensure the SSH key is properly formatted (no extra lines)
   - Check that the public key is added to `~/.ssh/authorized_keys` on the VPS

3. **Permission denied errors**
   - Ensure the SSH user has sudo privileges on the VPS
   - Check that Docker is installed and the user is in the docker group

4. **Deployment failures**
   - Check that the VPS has sufficient resources (CPU, memory, disk)
   - Verify Docker and docker-compose are installed
   - Ensure the deployment directory `/opt/news-portal` exists and is writable
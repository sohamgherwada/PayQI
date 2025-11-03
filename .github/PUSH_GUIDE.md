# GitHub Push Guide

Guide to push PayQI code to GitHub.

## Prerequisites

1. **GitHub Account** - Make sure you have a GitHub account
2. **Git Installed** - Check with `git --version`
3. **SSH Key or Personal Access Token** - For authentication

## Step 1: Initialize Git Repository (if not already done)

```bash
cd /workspace
git init
git branch -M main
```

## Step 2: Create .gitignore (Already Created)

The `.gitignore` file is already configured to exclude:
- Environment files (`.env`)
- Python cache files
- Virtual environments
- Build artifacts
- Secrets

## Step 3: Stage All Files

```bash
git add .
```

## Step 4: Create Initial Commit

```bash
git commit -m "Initial commit: PayQI payment gateway with XRP support

- FastAPI backend with JWT authentication
- XRP payment support with destination tags
- Ruby webhook service (Sinatra)
- Ruby CLI tool (Shopify style)
- Comprehensive test suites (pytest, RSpec)
- GitHub Actions CI/CD workflows
- Complete integration documentation
- Security best practices
- Docker setup for easy deployment"
```

## Step 5: Create GitHub Repository

1. Go to [GitHub.com](https://github.com)
2. Click the "+" icon ? "New repository"
3. Repository name: `payqi` (or your preferred name)
4. Description: "PayQI - Stripe for Crypto - Payment gateway for cryptocurrency payments"
5. Choose Public or Private
6. **Don't** initialize with README, .gitignore, or license (we already have these)
7. Click "Create repository"

## Step 6: Add Remote and Push

```bash
# Add your GitHub repository as remote
# Replace YOUR_USERNAME and YOUR_REPO with your actual values
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# Or if using SSH:
# git remote add origin git@github.com:YOUR_USERNAME/YOUR_REPO.git

# Push to GitHub
git push -u origin main
```

## Alternative: Using GitHub CLI

If you have GitHub CLI installed:

```bash
# Install GitHub CLI (if not installed)
# macOS: brew install gh
# Linux: See https://cli.github.com/manual/installation

# Authenticate
gh auth login

# Create repository and push
gh repo create payqi --public --source=. --remote=origin --push
```

## Step 7: Update Badge URLs

After pushing, update the badge URLs in `README.md`:

```markdown
[![Python Tests](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/python-tests.yml/badge.svg)](...)
```

Replace `YOUR_USERNAME` and `YOUR_REPO` with your actual values.

## Troubleshooting

### Authentication Issues

**If using HTTPS:**
- Use Personal Access Token instead of password
- Create token: GitHub ? Settings ? Developer settings ? Personal access tokens ? Tokens (classic)
- Use token as password when prompted

**If using SSH:**
```bash
# Generate SSH key (if not exists)
ssh-keygen -t ed25519 -C "your_email@example.com"

# Add to ssh-agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Add public key to GitHub
# Copy: cat ~/.ssh/id_ed25519.pub
# GitHub ? Settings ? SSH and GPG keys ? New SSH key
```

### Large Files

If you have large files:
```bash
# Install git-lfs
git lfs install
git lfs track "*.pdf"
git add .gitattributes
```

### Push Rejected

If push is rejected:
```bash
# Pull first (if repository already exists)
git pull origin main --allow-unrelated-histories

# Then push
git push -u origin main
```

## Next Steps After Push

1. **Enable GitHub Actions**
   - Go to repository Settings ? Actions ? General
   - Enable workflows

2. **Set Up Secrets** (if needed)
   - Settings ? Secrets and variables ? Actions
   - Add: `NOWPAYMENTS_API_KEY`, `XRP_WALLET_ADDRESS`, etc.

3. **Update README Badges**
   - Replace placeholder badge URLs with your repository URL

4. **Invite Collaborators**
   - Settings ? Collaborators ? Add people

## Verify Push

1. Visit your repository on GitHub
2. Check that all files are present
3. Verify GitHub Actions workflows are running
4. Check that badges show correct status

## Important Notes

- ?? **Never commit `.env` files** - They contain secrets
- ?? **Never commit API keys or passwords**
- ? All sensitive data should be in environment variables
- ? Use GitHub Secrets for CI/CD workflows

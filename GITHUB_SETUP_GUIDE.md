# 🚀 Push Your AI Data Analyst Platform to GitHub

## Step 1: Install Git

### Download and Install Git:
1. Go to [https://git-scm.com/download/windows](https://git-scm.com/download/windows)
2. Download Git for Windows
3. Run the installer with default settings
4. Restart your command prompt/PowerShell

### Verify Installation:
```bash
git --version
```

## Step 2: Create GitHub Account & Repository

### GitHub Account:
1. Go to [https://github.com](https://github.com)
2. Sign up for a free account if you don't have one
3. Verify your email address

### Create New Repository:
1. Click the "+" icon in the top right corner
2. Select "New repository"
3. Repository name: `ai-data-analyst-platform`
4. Description: "AI-powered data analysis platform with dashboard generation"
5. Set to **Public** (for free deployment on Render)
6. **DO NOT** initialize with README, .gitignore, or license
7. Click "Create repository"

## Step 3: Prepare Your Project

### Create .gitignore file:
Create a `.gitignore` file in your project root with this content:

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual Environment
venv/
env/
ENV/
venv_3_11/

# Environment Variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# React
build/
.DS_Store
.env.local
.env.development.local
.env.test.local
.env.production.local

# Database
*.db
*.sqlite3

# Logs
*.log
logs/

# Temporary files
*.tmp
*.temp
test_*.csv
test_*.xlsx

# Charts and Reports (optional - you might want to keep some examples)
charts/*.html
reports/*.xlsx

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
```

## Step 4: Initialize Git and Push to GitHub

### Open PowerShell in your project directory:
```bash
# Navigate to your project
cd "E:\Bonison\Project\ai-data-analyst-platform"

# Initialize Git repository
git init

# Configure Git (replace with your information)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Add all files to staging
git add .

# Create first commit
git commit -m "Initial commit: AI Data Analyst Platform with enhanced dashboards"

# Add GitHub repository as remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/ai-data-analyst-platform.git

# Push to GitHub
git push -u origin main
```

## Step 5: Verify Upload

1. Go to your GitHub repository page
2. You should see all your project files
3. Check that the structure looks correct

## Step 6: Deploy to Render

### After pushing to GitHub:
1. Go to [Render.com](https://render.com) and sign up
2. Connect your GitHub account
3. Create a new Web Service
4. Select your `ai-data-analyst-platform` repository
5. Configure the service:
   - **Name**: `ai-data-analyst-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `cd Backend && pip install -r requirements.txt`
   - **Start Command**: `cd Backend && python -m uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `ENVIRONMENT`: `production`
7. Deploy!

## Step 7: Deploy Frontend (Separate Service)

1. Create another Web Service in Render
2. Same repository, but configure for frontend:
   - **Name**: `ai-data-analyst-frontend`
   - **Environment**: `Node`
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Start Command**: `cd frontend && npm start`
3. Add environment variable:
   - `REACT_APP_API_URL`: URL of your backend service

## Common Issues and Solutions

### Issue: Git command not found
**Solution**: Make sure Git is installed and restart your terminal

### Issue: Authentication failed
**Solution**: 
- Use Personal Access Token instead of password
- Go to GitHub Settings > Developer settings > Personal access tokens
- Generate new token with repo permissions
- Use token as password when prompted

### Issue: Repository already exists
**Solution**: 
- Delete the repository on GitHub and create a new one
- Or use `git remote set-url origin https://github.com/YOUR_USERNAME/ai-data-analyst-platform.git`

### Issue: Large files rejected
**Solution**: 
- Check your .gitignore file
- Remove large files from git: `git rm --cached large_file.ext`
- Add to .gitignore and commit

## Quick Commands Reference

```bash
# Check status
git status

# Add specific files
git add filename.ext

# Add all files
git add .

# Commit changes
git commit -m "Your commit message"

# Push changes
git push

# Pull latest changes
git pull

# Create new branch
git checkout -b new-feature

# Switch branches
git checkout main
```

## Security Notes

1. **Never commit your .env file** - it contains your OpenAI API key
2. **Use environment variables** for sensitive data
3. **Keep your repository public** for free Render deployment
4. **Review files before committing** to avoid uploading sensitive data

## Next Steps After Deployment

1. Test your deployed application
2. Share the URLs with your users
3. Monitor usage and performance
4. Set up custom domain (optional)

## Support

If you encounter any issues:
1. Check the GitHub repository for common issues
2. Review Render logs for deployment problems
3. Ensure all environment variables are set correctly
4. Verify your .gitignore file is working properly

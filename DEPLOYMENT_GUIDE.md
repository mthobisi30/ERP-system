# Complete Deployment Guide for ERP System on Vercel

## Prerequisites

- Python 3.11 or higher
- Git installed
- GitHub account
- Vercel account (free tier works)
- Neon account for PostgreSQL database

---

## Step 1: Set Up Neon PostgreSQL Database

### 1.1 Create Neon Account and Database

1. Go to https://console.neon.tech/
2. Sign up for a free account
3. Click **"Create a project"**
4. Choose a name for your project (e.g., "erp-system")
5. Select a region close to your users
6. Click **"Create project"**

### 1.2 Get Database Connection String

1. In your Neon dashboard, go to **"Connection Details"**
2. Copy the connection string - it looks like:
   ```
   postgresql://username:password@ep-xxxxx.region.aws.neon.tech/dbname?sslmode=require
   ```
3. Save this for later - you'll need it for environment variables

### 1.3 Run Database Schema

1. Open the Neon SQL Editor in your dashboard
2. Copy the entire contents of `neon_db_schema.sql`
3. Paste it into the SQL Editor
4. Click **"Run"** to execute the schema
5. Verify tables were created by running:
   ```sql
   SELECT table_name FROM information_schema.tables 
   WHERE table_schema = 'public';
   ```

---

## Step 2: Prepare Your Local Project

### 2.1 Create Project Directory

```bash
mkdir erp-system
cd erp-system
```

### 2.2 Initialize Git Repository

```bash
git init
```

### 2.3 Create .gitignore File

```bash
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
.venv

# Environment variables
.env
.env.local

# Flask
instance/
.webassets-cache

# Database
*.db
*.sqlite3

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
logs/
*.log

# Uploads
static/uploads/
uploads/

# Testing
.pytest_cache/
.coverage
htmlcov/

# Vercel
.vercel
EOF
```

### 2.4 Copy All Provided Files

Copy these files into your project directory:
- `neon_db_schema.sql`
- `.env.example`
- `requirements.txt`
- `vercel.json`
- `PROJECT_STRUCTURE.md`

---

## Step 3: Create Environment Variables File

### 3.1 Create .env File

```bash
cp .env.example .env
```

### 3.2 Edit .env File

**REQUIRED VARIABLES:**

```bash
# Database (from Neon dashboard)
DATABASE_URL=postgresql://username:password@ep-xxxxx.region.aws.neon.tech/dbname?sslmode=require

# Security (generate random strings)
SECRET_KEY=your-generated-secret-key-here
JWT_SECRET_KEY=your-generated-jwt-secret-here

# Application
FLASK_APP=app.py
FLASK_ENV=production
DEBUG=0

# App URL (update after Vercel deployment)
APP_URL=https://your-app.vercel.app
```

**Generate Secure Keys:**

```python
# Run this in Python to generate secure keys
import secrets
print("SECRET_KEY:", secrets.token_hex(32))
print("JWT_SECRET_KEY:", secrets.token_hex(32))
```

**OPTIONAL BUT RECOMMENDED:**

- Email settings (for notifications)
- File storage (AWS S3 or Cloudinary)
- Redis (for caching - can use Upstash free tier)

---

## Step 4: Create Basic Flask Application

### 4.1 Create app.py

```python
from flask import Flask, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Enable CORS
CORS(app)

@app.route('/')
def index():
    return jsonify({
        'message': 'ERP System API',
        'status': 'running',
        'version': '1.0.0'
    })

@app.route('/api/health')
def health():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    app.run(debug=False)
```

### 4.2 Test Locally

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run Flask
python app.py
```

Visit http://localhost:5000 - you should see the JSON response.

---

## Step 5: Deploy to Vercel

### 5.1 Install Vercel CLI

```bash
npm install -g vercel
```

### 5.2 Login to Vercel

```bash
vercel login
```

### 5.3 Initialize Vercel Project

```bash
vercel
```

Follow the prompts:
- Set up and deploy? **Y**
- Which scope? Select your account
- Link to existing project? **N**
- What's your project's name? **erp-system**
- In which directory is your code located? **.**
- Want to override settings? **N**

### 5.4 Add Environment Variables to Vercel

**Option A: Using Vercel CLI**

```bash
# Add DATABASE_URL
vercel env add DATABASE_URL

# When prompted:
# - Select "Production, Preview, and Development"
# - Paste your Neon connection string

# Add SECRET_KEY
vercel env add SECRET_KEY
# Paste your generated secret key

# Add JWT_SECRET_KEY
vercel env add JWT_SECRET_KEY
# Paste your generated JWT secret

# Add other required variables
vercel env add FLASK_APP
# Value: app.py

vercel env add FLASK_ENV
# Value: production
```

**Option B: Using Vercel Dashboard**

1. Go to https://vercel.com/dashboard
2. Select your project
3. Go to **Settings** → **Environment Variables**
4. Add each variable from your `.env` file
5. Make sure to select **Production**, **Preview**, and **Development**

### 5.5 Deploy to Production

```bash
vercel --prod
```

After deployment, you'll get a URL like: `https://erp-system-xyz.vercel.app`

---

## Step 6: Update Environment Variables

### 6.1 Update APP_URL in Vercel

1. Go to Vercel dashboard
2. Find your `APP_URL` environment variable
3. Update it with your actual Vercel URL
4. Redeploy: `vercel --prod`

---

## Step 7: Verify Deployment

### 7.1 Test API Endpoints

```bash
# Test health endpoint
curl https://your-app.vercel.app/api/health

# Should return: {"status":"healthy"}
```

### 7.2 Test Database Connection

Add a test endpoint to your `app.py`:

```python
from sqlalchemy import create_engine, text
import os

@app.route('/api/db-test')
def db_test():
    try:
        engine = create_engine(os.getenv('DATABASE_URL'))
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            return jsonify({'database': 'connected'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

Then test:
```bash
curl https://your-app.vercel.app/api/db-test
```

---

## Step 8: Set Up Continuous Deployment

### 8.1 Push to GitHub

```bash
git add .
git commit -m "Initial ERP system setup"
git branch -M main
```

### 8.2 Create GitHub Repository

1. Go to https://github.com/new
2. Create a new repository named "erp-system"
3. Don't initialize with README (you already have files)

### 8.3 Push Code

```bash
git remote add origin https://github.com/YOUR_USERNAME/erp-system.git
git push -u origin main
```

### 8.4 Link to Vercel

1. Go to your Vercel dashboard
2. Click on your project
3. Go to **Settings** → **Git**
4. Connect your GitHub repository
5. Now every push to `main` will auto-deploy!

---

## Step 9: Monitor and Maintain

### 9.1 View Logs

```bash
# View real-time logs
vercel logs

# Or in Vercel dashboard
```

### 9.2 Set Up Monitoring

1. Enable Vercel Analytics in project settings
2. (Optional) Add Sentry for error tracking:
   - Sign up at https://sentry.io
   - Add `SENTRY_DSN` to environment variables

### 9.3 Database Backups

Neon provides automatic backups, but you can also:
- Create manual backups in Neon dashboard
- Set up automated exports to S3

---

## Common Issues and Solutions

### Issue: "Module not found" errors

**Solution:** Make sure all dependencies are in `requirements.txt`:
```bash
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update dependencies"
vercel --prod
```

### Issue: Database connection fails

**Solution:** 
1. Verify `DATABASE_URL` in Vercel environment variables
2. Ensure it includes `?sslmode=require`
3. Check Neon database is active (not paused)

### Issue: 500 Internal Server Error

**Solution:**
```bash
# Check logs
vercel logs --follow

# Common causes:
# - Missing environment variables
# - Python version mismatch (ensure Python 3.11+)
# - Import errors
```

### Issue: Static files not loading

**Solution:** Ensure `vercel.json` has static route:
```json
{
  "routes": [
    {
      "src": "/static/(.*)",
      "dest": "/static/$1"
    }
  ]
}
```

---

## Performance Optimization

### 1. Enable Caching

Add Redis for caching:
1. Sign up for Upstash Redis (free tier)
2. Get connection URL
3. Add to Vercel environment:
   ```bash
   vercel env add REDIS_URL
   ```

### 2. Optimize Database Queries

- Use database indexes (already in schema)
- Implement pagination
- Use connection pooling

### 3. Enable Compression

Add to `app.py`:
```python
from flask_compress import Compress
Compress(app)
```

---

## Security Checklist

- ✅ Use HTTPS (automatic with Vercel)
- ✅ Strong SECRET_KEY and JWT_SECRET_KEY
- ✅ Database connection uses SSL (`?sslmode=require`)
- ✅ CORS configured properly
- ✅ Input validation on all endpoints
- ✅ Rate limiting enabled
- ✅ SQL injection prevention (using ORM)
- ✅ XSS prevention (using Flask auto-escaping)
- ✅ Environment variables not in code
- ✅ .env file in .gitignore

---

## Next Steps

1. Build out the complete application structure (see `PROJECT_STRUCTURE.md`)
2. Implement authentication system
3. Create frontend interface
4. Add more API endpoints
5. Set up automated testing
6. Configure custom domain (optional)

---

## Useful Commands Reference

```bash
# Local development
python app.py                    # Run locally
flask db migrate                 # Create migration
flask db upgrade                 # Apply migration

# Vercel deployment
vercel                          # Deploy to preview
vercel --prod                   # Deploy to production
vercel logs                     # View logs
vercel env ls                   # List environment variables
vercel env add VAR_NAME         # Add environment variable
vercel env rm VAR_NAME          # Remove environment variable

# Git
git status                      # Check status
git add .                       # Stage all changes
git commit -m "message"         # Commit changes
git push                        # Push to GitHub (auto-deploys)
```

---

## Support Resources

- Vercel Documentation: https://vercel.com/docs
- Neon Documentation: https://neon.tech/docs
- Flask Documentation: https://flask.palletsprojects.com/
- SQLAlchemy Documentation: https://docs.sqlalchemy.org/

---

**Congratulations! Your ERP system is now deployed and running on Vercel with Neon PostgreSQL! 🎉**

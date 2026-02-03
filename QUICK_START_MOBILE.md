# 🚀 QUICK START GUIDE - GitHub Mobile Edition

## For Mobile Users: Complete Setup in 10 Minutes

### Step 1: Create Files on GitHub Mobile (5 minutes)

1. **Create a new repository** on GitHub named `erp-system`
2. **Create these files one by one** using "Create new file" button:

#### Required Files (Create in order):

**1. Create: `.env`**
```
DATABASE_URL=your-neon-database-url-here
SECRET_KEY=generate-a-random-key
JWT_SECRET_KEY=generate-another-random-key
FLASK_APP=app.py
FLASK_ENV=production
```

**2. Create: `requirements.txt`**
- Copy contents from the requirements.txt file provided

**3. Create: `vercel.json`**
- Copy contents from the vercel.json file provided

**4. Create: `app.py`**
- Copy contents from the app.py file provided

**5. Create folders by adding placeholder files:**
```
config/__init__.py
app/__init__.py
app/models/__init__.py
app/routes/__init__.py
```

Then copy all other files to their respective folders.

### Step 2: Set Up Neon Database (2 minutes)

1. Open https://console.neon.tech on your mobile browser
2. Sign up / Log in
3. Create new project
4. Copy the connection string
5. Paste into `.env` file under `DATABASE_URL`

### Step 3: Run Database Schema

1. In Neon dashboard, click "SQL Editor"
2. Copy entire contents of `neon_db_schema.sql`
3. Paste and click "Run"

### Step 4: Deploy to Vercel (3 minutes)

1. Open https://vercel.com on mobile browser
2. Click "Add New" → "Project"
3. Import your GitHub repository
4. Add environment variables:
   - Click "Environment Variables"
   - Add: `DATABASE_URL`, `SECRET_KEY`, `JWT_SECRET_KEY`
5. Click "Deploy"

### Step 5: Test Your API

Once deployed, test:
```
https://your-app.vercel.app/api/health
```

## 🎯 Quick Commands Reference

### Generate Secret Keys

Use any online UUID generator or run on your computer:
```python
import secrets
print(secrets.token_hex(32))
```

### Test Endpoints

Use Postman mobile app or HTTP client:

**Login:**
```
POST /api/auth/login
Body: {"email": "user@example.com", "password": "password"}
```

**Get Projects:**
```
GET /api/projects
Header: Authorization: Bearer <token>
```

## 📱 Mobile-Friendly Development Tips

1. **Use GitHub Mobile App** for quick file edits
2. **Use Vercel Mobile App** for deployment monitoring
3. **Use Postman Mobile** for API testing
4. **Use Neon Mobile Dashboard** for database monitoring

## 🆘 Troubleshooting

**Database Connection Fails:**
- Check DATABASE_URL in Vercel environment variables
- Ensure URL includes `?sslmode=require`
- Verify Neon database is active

**Import Errors:**
- Check all `__init__.py` files exist
- Verify file structure matches PROJECT_STRUCTURE.md
- Redeploy on Vercel

**Token Errors:**
- Ensure JWT_SECRET_KEY is set
- Check token expiration in login response
- Try logging in again

## 📞 Getting Help

- Check DEPLOYMENT_GUIDE.md for detailed instructions
- Review API_DOCUMENTATION.md for API usage
- Check PROJECT_STRUCTURE.md for file organization

## ✅ Success Checklist

- [ ] GitHub repository created
- [ ] All files uploaded
- [ ] Neon database created
- [ ] Schema executed
- [ ] Vercel deployment successful
- [ ] Environment variables set
- [ ] Health endpoint responding
- [ ] Can create test user
- [ ] Can login successfully
- [ ] API returning data

---

**You're all set! Start building your ERP system! 🎉**

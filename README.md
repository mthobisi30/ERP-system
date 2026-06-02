# 🏢 Rephina Software ERP

A full-featured Enterprise Resource Planning (ERP) system built with Python Flask and PostgreSQL (Rephina Software ERP).

## 📋 Features

### Core Modules

- 🔐 **Authentication & User Management** - Secure login, role-based access control
- 📊 **Dashboard & Analytics** - Real-time KPIs, customizable widgets
- 📅 **Scheduler & Calendar** - Task scheduling, event management
- ✅ **Task Management** - Kanban boards, assignments, priorities
- 🎯 **Project Management** - Project tracking, milestones, budgets
- 👥 **Customer Relationship Management (CRM)** - Leads, opportunities, customer database
- 💼 **Sales Management** - Quotations, sales orders, pipeline tracking
- ⏱️ **Time Tracking** - Billable hours per project, timesheets
- 🧾 **Services & Rate Card** - Service catalog and billing rates
- 💰 **Accounting & Finance** - General ledger, invoicing (ZAR + 15% VAT), payments, expenses
- 👨‍💼 **HR & Performance** - Employee records, performance reviews, attendance
- 🎫 **Customer Service** - Ticket management, support tracking
- 📈 **Reports & Analytics** - Custom reports, data export, visualizations
- 📄 **Document Management** - File uploads, categorization
- 🔔 **Notifications** - In-app, email, SMS notifications
- 📝 **Activity Logs** - Audit trails, system logs

## 🚀 Tech Stack

**Backend:**
- Python 3.11+
- Flask 3.0
- SQLAlchemy 2.0 (ORM)
- PostgreSQL (Neon)
- JWT Authentication
- Flask-RESTful

**Deployment:**
- Vercel (Serverless)
- Neon PostgreSQL (Database)
- AWS S3 / Cloudinary (File Storage)
- Redis (Optional - Caching)

## 📁 Project Structure

```
erp-system/
├── app.py                  # Main application
├── vercel.json            # Vercel configuration
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
├── config/               # App configuration
├── app/
│   ├── models/          # Database models
│   ├── routes/          # API endpoints
│   ├── services/        # Business logic
│   ├── schemas/         # Data validation
│   └── utils/           # Helper functions
├── static/              # Static files
├── templates/           # HTML templates
└── migrations/          # Database migrations
```

## 🛠️ Quick Start

### Prerequisites

- Python 3.11+
- Git
- Neon account (free at https://neon.tech)
- Vercel account (free at https://vercel.com)

### 1. Clone or Download

```bash
git clone <your-repo-url>
cd erp-system
```

### 2. Set Up Database

1. Create a Neon PostgreSQL database at https://console.neon.tech/
2. Copy your database connection string (you'll set it as `DATABASE_URL` below)

> The schema is managed by **Alembic migrations** (`migrations/`), not a hand-maintained
> SQL file. You'll create the tables with `alembic upgrade head` in step 5.

### 3. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your values
nano .env  # or use your favorite editor
```

**Required variables:**
- `DATABASE_URL` - Your Neon connection string
- `SECRET_KEY` - Generate with: `python -c "import secrets; print(secrets.token_hex(32))"`
- `JWT_SECRET_KEY` - Generate with: `python -c "import secrets; print(secrets.token_hex(32))"`

### 4. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 5. Create the Schema & Seed

```bash
# Create all tables from the migrations
alembic upgrade head

# Seed default roles, an admin user, and company settings
python scripts/seed_database.py
```

### 6. Run Locally

```bash
python index.py
```

Visit http://localhost:5000

### 6. Deploy to Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
vercel --prod
```

**Don't forget to add environment variables in Vercel dashboard!**

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed instructions.

## 📚 Documentation

- [Deployment Guide](DEPLOYMENT_GUIDE.md) - Complete deployment instructions
- [Project Structure](PROJECT_STRUCTURE.md) - Detailed project organization
- Database Schema - Managed via Alembic migrations in `migrations/`

## 🔒 Security Features

- ✅ JWT Authentication
- ✅ Password hashing (bcrypt)
- ✅ Role-based access control
- ✅ CORS protection
- ✅ SQL injection prevention (ORM)
- ✅ XSS prevention
- ✅ Rate limiting
- ✅ Audit logging
- ✅ SSL/TLS encryption

## 🗄️ Database Schema Highlights

**70+ Tables Including:**
- Users & Authentication
- Projects & Tasks
- Customers & Leads
- Products & Inventory
- Sales & Purchases
- Accounting & Finance
- HR & Attendance
- Tickets & Support
- Logs & Analytics

## 📊 API Endpoints (Preview)

```
Authentication:
POST   /api/auth/register
POST   /api/auth/login
POST   /api/auth/logout
GET    /api/auth/me

Projects:
GET    /api/projects
POST   /api/projects
GET    /api/projects/:id
PUT    /api/projects/:id
DELETE /api/projects/:id

Tasks:
GET    /api/tasks
POST   /api/tasks
GET    /api/tasks/:id
PUT    /api/tasks/:id
DELETE /api/tasks/:id

... (30+ more endpoint groups)
```

## 🎨 Frontend Options

You can build the frontend using:

1. **Server-side rendered** (Included)
   - Jinja2 templates
   - HTMX for reactivity
   - Alpine.js for interactions

2. **Single Page Application** (Separate project)
   - React + Vite
   - Vue + Nuxt
   - Angular

3. **Mobile App**
   - React Native
   - Flutter

The API is framework-agnostic and works with any frontend!

## 🔧 Development

### Running Tests

The suite runs against a real Postgres database (the models use native `UUID`/`JSONB`).

```bash
# Easiest — spins up a throwaway Postgres, runs pytest, tears it down. No setup.
./scripts/run_tests.sh
./scripts/run_tests.sh -v tests/test_billing_spine.py   # args pass through to pytest

# Or against a database you provide (suite is skipped if this is unset):
TEST_DATABASE_URL=postgresql://user:pass@host/dbname pytest
```

CI runs the full suite on Postgres on every push — see [.github/workflows/tests.yml](.github/workflows/tests.yml).

### Database Migrations (Alembic)

```bash
alembic upgrade head                            # apply all migrations (creates the schema)
alembic revision --autogenerate -m "message"    # generate a migration from model changes
alembic downgrade -1                            # roll back one migration
```

### Code Quality

```bash
# Format code
black .

# Lint
flake8 .

# Type checking
mypy .
```

## 📈 Roadmap

- [ ] WebSocket support for real-time updates
- [ ] Mobile app (React Native)
- [ ] Advanced analytics dashboard
- [ ] AI-powered insights
- [ ] Multi-currency support
- [ ] Multi-language support
- [ ] Automated testing suite
- [ ] Integration with third-party services
  - [ ] Stripe payments
  - [ ] SendGrid emails
  - [ ] Twilio SMS
  - [ ] Slack notifications
  - [ ] Google Calendar sync

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 Environment Variables

See `.env.example` for all available environment variables.

**Essential:**
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - Flask secret key
- `JWT_SECRET_KEY` - JWT signing key

**Optional:**
- `REDIS_URL` - Redis for caching
- `AWS_*` - S3 file storage
- `SENDGRID_API_KEY` - Email sending
- `SENTRY_DSN` - Error tracking

## 🐛 Troubleshooting

### Database Connection Issues

```bash
# Test database connection
python -c "from sqlalchemy import create_engine; import os; engine = create_engine(os.getenv('DATABASE_URL')); print('Connected!' if engine else 'Failed')"
```

### Vercel Deployment Issues

```bash
# View logs
vercel logs --follow

# Check environment variables
vercel env ls
```

### Local Development Issues

```bash
# Clear cache
find . -type d -name "__pycache__" -exec rm -rf {} +

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## 📞 Support

- Create an issue on GitHub
- Check [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- Review [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Flask framework
- SQLAlchemy ORM
- Neon PostgreSQL
- Vercel hosting
- All open-source contributors

---

**Built with ❤️ using Python and Flask**

**Ready to revolutionize your business operations! 🚀**

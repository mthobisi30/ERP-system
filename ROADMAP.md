# Rephina ERP — Powerhouse Roadmap

Goal: a tightly-interconnected platform that documents and trails the **entire SDLC**
plus every service Rephina offers — with **Projects, Clients, and the Developer (User)**
as the three sources of truth, human-meaningful IDs, and proper typed inputs everywhere.

## ✅ Done

- **Spine**: Lead → Opportunity / Quote → Project → Time → Invoice (T&M) / Retainer → Payment.
- **Delivery**: sprints, tasks, Kanban board, phases + deliverables, expenses → profitability.
- **Documents engine**: Invoice, Milestone/Phase Report, Endorsement, Migration Notice, BRD/Scope
  (Rephina letterhead, banking, auto `RSS-TYPE-YYYY-NNN` numbering).
- **Project configuration**: type, tech stack (chips), scope, estimates, repo/live URLs, README,
  contract fields — via a dedicated typed form.
- **Meaningful IDs**: auto `customer_code` (e.g. `MPIA`) and `project_code` (`MPIA-001`); UUIDs hidden in lists.
- **Reports**: utilisation, project profitability, pipeline, revenue.
- **Modules**: Blog, Enquiries, Users-admin, module on/off toggles.
- **Platform**: role-based auth, glass UX, toasts, 53-test suite, CI, Alembic migrations, Vercel deploy.

## 🔜 Next (the deeper "powerhouse" work)

### 1. Input-type overhaul (per module)
Replace the generic free-text create form with typed forms (selects, multi-selects, dates,
numbers, currency, relation pickers) for: Customers, Leads, Opportunities, Tickets, Expenses,
HR, Invoices. Autopopulate where possible (dates default to today, currency from settings,
client → contact, rates from rate card).

### 2. Everything linked to Project + Client
Add (and surface) `project_id` / `customer_id` on every relevant record and show them on the
project & client 360° views:
- Tickets → project + client (with SLA).
- Documents (file attachments) → project.
- Notifications / activity log → project + actor.
- Leads/Opportunities → show conversion trail to Project.

### 3. Client 360° page (mirror of the project workspace)
One page per client: contacts, projects, quotes, invoices, payments, balance, retainers,
enquiries, tickets, documents — the client as a source of truth.

### 4. SDLC trail & audit
Activity log on every create/update/status-change (who, what, when), shown as a timeline on
the project. Status workflows (lead→won→active→delivered→closed) with gates.

### 5. Roles & permissions matrix
Per-module, per-action permissions (view/create/edit/delete/approve) beyond
employee/manager/admin; a roles admin screen. Client-portal role (read-only, own data) for later.

### 6. Developer showcase
Public project case-study pages (from project + BRD + live URL + tech stack), a skills/services
catalogue, and a portfolio view — so the ERP itself demonstrates capability.

### 7. Hardening for scale
Redis for rate-limit + token-blocklist (serverless), file uploads to Cloudinary/S3 (READMEs,
attachments, signed docs), email delivery of generated PDFs, and search across entities.

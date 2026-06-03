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

### 1. Input-type overhaul (per module) — ✅ DONE
Relation pickers (customer/project dropdowns) + correct typed fields on the generic
create/edit forms; dedicated rich project form. (Autopopulate of more defaults: ongoing.)

### 2. Everything linked to Project + Client — ✅ DONE (tickets); ongoing for documents
Tickets carry project + client (with SLA); activity log scoped to both.

### 3. Client 360° page — ✅ DONE
`/customers/<id>`: projects, tickets, invoices+balance, quotes, retainers, activity.

### 4. SDLC trail & audit — ✅ DONE
ActivityLog scoped to project+client; timeline on the workspace and client 360.

### 6. Developer showcase — ✅ DONE
Public `/showcase` portfolio from projects flagged `showcase`; sanitised `/api/public/showcase`.

### 7. Hardening — partial
✅ rate-limit storage config hook; ✅ DB-backed token blocklist; ✅ global search;
✅ email generated invoice/quote PDFs to clients (graceful when SMTP unset).
🔜 Redis for serverless; file uploads to Cloudinary/S3 (README/attachments/signed docs).

### 5. Roles & permissions matrix — 🔜 remaining (deliberate)
The 3-tier role system (employee < manager < admin) is enforced and tested. A full
per-module/per-action matrix + roles admin screen is a larger, security-sensitive refactor
best scoped on its own rather than rushed. Client-portal (read-only, own data) sits behind this.

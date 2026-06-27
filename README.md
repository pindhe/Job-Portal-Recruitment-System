# AI Recruitment Platform — AI-Powered Recruitment & Job Portal

An enterprise-grade, AI-powered recruitment and job portal built with **Django (Python)**.
It supports companies, recruiters, universities, NGOs, government organizations and job
seekers — with role-based dashboards, an AI service layer, a versioned REST API for mobile
apps, payments, notifications and a modern, responsive UI (Tailwind CSS, dark mode, RTL/LTR ready).

---

## ✨ Features

### Roles (RBAC)
Super Admin · Admin · Employer · Recruiter · HR Manager · Candidate · Support Agent · Accountant · Moderator · Guest

### Public Website
Modern landing page (animated hero, stats, categories, featured jobs, AI showcase, top
companies, testimonials, CTA), job search & filters, company directory, blog / career advice,
pricing, FAQs, contact, newsletter, dark-mode toggle, global search.

### Candidate Dashboard
Overview with profile-completion ring, resume builder (skills, experience, education,
certificates, languages, projects), PDF-ready resume preview, applied jobs, saved jobs,
AI recommendations, notifications.

### Employer Dashboard
Company profile, job posting / editing, applicant management with **AI ranking**, hiring
pipeline chart, application status workflow, billing & invoices.

### Recruiter Dashboard
Assigned jobs, candidate pipeline (doughnut chart), recent candidates, AI match scores.

### Super Admin Dashboard
Platform analytics (users, companies, jobs, applications, revenue), growth charts,
users-by-role chart, pending job approvals, user & job management.

### AI Service Layer (`apps/aifeatures/services.py`)
Deterministic, dependency-free heuristics with a clean interface (swap for an LLM later):
- AI candidate ↔ job **match score**
- Resume **ATS checker** (structure + keyword coverage + suggestions)
- AI **cover letter** generator
- AI **job description** generator
- **Candidate ranking** for recruiters
- **Skill-gap analysis** + career advisor

### REST API (versioned, JWT)
- `POST /api/v1/auth/register/`, `POST /api/v1/auth/token/`, `/token/refresh/`, `GET/PATCH /api/v1/auth/me/`
- `GET /api/v1/jobs/`, `GET /api/v1/jobs/{slug}/`, `POST /api/v1/jobs/{slug}/apply/`, `GET /api/v1/jobs/{slug}/match_score/`
- `categories`, `companies`, `applications`, `saved-jobs`, `notifications`
- `POST /api/v1/ai/ats-check/`
- Swagger UI at **`/api/docs/`**, schema at `/api/schema/`

### Platform
Custom email-based User model, OTP email/phone verification, password reset, login history,
device management, audit-log middleware, soft delete, payments (Stripe/PayPal/Zaad/EVC/Sahal/
Premier placeholders), subscriptions & invoices, unified notifications (in-app + email + WhatsApp/SMS hooks).

---

## 🧱 Tech Stack
- **Backend:** Python 3.11+, Django 5, Django REST Framework, SimpleJWT, MVC + service/repository-style layers, MySQL-ready (SQLite default)
- **Frontend:** Tailwind CSS, Alpine.js, Chart.js, AOS animations, Lucide icons, dark/light mode, responsive, PWA-friendly
- **API:** Versioned REST, JWT, throttling, drf-spectacular (OpenAPI/Swagger)

---

## 🚀 Quick Start (Windows / PowerShell)

```powershell
# 1. Create & activate a virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) configure environment
Copy-Item .env.example .env   # edit as needed

# 4. Run migrations
python manage.py migrate

# 5. Seed demo data (creates users, companies, jobs, applications, CMS content)
python manage.py seed_demo

# 6. Start the server
python manage.py runserver
```

On macOS/Linux use `source venv/bin/activate` instead of the Activate.ps1 line.

Then open **http://127.0.0.1:8000**.

---

## 🔑 Demo Accounts (after `seed_demo`)

| Role        | Email                          | Password       |
|-------------|--------------------------------|----------------|
| Super Admin | `admin@jobportal.local`        | `Admin@12345`  |
| Employer    | `employer1@jobportal.local`    | `Employer@123` |
| Recruiter   | `recruiter@jobportal.local`    | `Recruiter@123`|
| Candidate   | `candidate1@jobportal.local`   | `Candidate@123`|

Django admin: **http://127.0.0.1:8000/admin/**

---

## 🗂 Project Structure

```
config/                 # settings, root urls, wsgi/asgi
apps/
  core/                 # base models, soft delete, audit log, RBAC, middleware
  accounts/             # custom User, auth, OTP, devices, login history
  companies/            # Company, Branch, Department, CompanyMember
  jobs/                 # Job, JobCategory, JobApplication, SavedJob, events
  candidates/           # CandidateProfile + resume building blocks
  aifeatures/           # AI service layer + tools (ATS, cover letter, advisor)
  cms/                  # public site, blog, pages, FAQs, testimonials, contact
  payments/             # Plan, Subscription, Invoice, Coupon
  notifications/        # in-app + multi-channel notification service
  dashboard/            # role-based dashboards (candidate/employer/recruiter/admin)
  api/                  # versioned DRF API (v1) + JWT + Swagger
templates/              # Tailwind templates (base, partials, per-app)
static/                 # CSS assets
```

---

## ⚙️ Configuration

All settings are environment-driven (see `.env.example`):
- **Database:** SQLite by default; set `DB_ENGINE=django.db.backends.mysql` (+ `DB_*`) for MySQL.
- **Email:** console backend in dev; set `EMAIL_HOST` etc. for SMTP.
- **Cache:** local-memory by default; set `REDIS_URL` for Redis.
- **Integrations:** `STRIPE_*`, `WHATSAPP_*`, `OPENAI_API_KEY` placeholders for production wiring.

Theme colors (configurable in `config/settings.py` `THEME`):
Primary `#0F4C81` · Secondary `#14B8A6` · Accent `#F59E0B` · Success `#10B981` · Danger `#EF4444`.

---

## 🔌 Mobile / Flutter
The `/api/v1/` surface is JWT-authenticated and CORS-enabled, ready for Flutter / Android /
iOS clients. Device registration and push-token fields exist on the `Device` model for push
notifications.

---

## 📝 Notes
- The AI layer ships as deterministic heuristics so the platform runs with **zero external
  API keys**. It is isolated behind a service interface so you can drop in an LLM provider.
- Payment gateways and WhatsApp/SMS are stubbed at the integration boundary; flows and data
  models are complete and ready for real credentials.

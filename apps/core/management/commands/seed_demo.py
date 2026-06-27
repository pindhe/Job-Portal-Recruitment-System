"""Seed the database with realistic demo data.

Usage::

    python manage.py seed_demo
"""
import random
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.candidates.models import CandidateProfile, Education, Experience, Skill
from apps.cms.models import FAQ, BlogPost, Partner, Testimonial
from apps.companies.models import Company, CompanyMember
from apps.jobs.models import Job, JobApplication, JobCategory
from apps.payments.models import Plan

User = get_user_model()

CATEGORIES = [
    ("Software Development", "code"),
    ("Design & Creative", "palette"),
    ("Marketing & Sales", "megaphone"),
    ("Finance & Accounting", "calculator"),
    ("Human Resources", "users"),
    ("Healthcare", "heart-pulse"),
    ("Education", "graduation-cap"),
    ("Engineering", "wrench"),
    ("Customer Support", "headphones"),
    ("Data & Analytics", "bar-chart-3"),
]

COMPANIES = [
    ("TechNova Solutions", "company", "Technology", "Building the future of cloud software."),
    ("BrightPath University", "university", "Education", "Empowering the next generation of leaders."),
    ("GreenFuture NGO", "ngo", "Non-Profit", "Sustainability for a better tomorrow."),
    ("Ministry of Digital Economy", "government", "Government", "Driving national digital transformation."),
    ("PrimeHire Recruiters", "recruiter", "Staffing", "Connecting top talent with great companies."),
    ("FinEdge Capital", "company", "Finance", "Smart financial solutions for modern businesses."),
]

JOB_TITLES = [
    ("Senior Backend Engineer", "full_time", "senior", "Python, Django, PostgreSQL, REST, AWS"),
    ("Frontend Developer", "full_time", "mid", "JavaScript, React, Tailwind, HTML, CSS"),
    ("Product Designer", "full_time", "mid", "Figma, UI, UX, Prototyping, Design Systems"),
    ("Data Analyst", "full_time", "junior", "SQL, Python, Excel, Power BI, Statistics"),
    ("Marketing Manager", "full_time", "senior", "SEO, Content, Social Media, Analytics"),
    ("HR Specialist", "part_time", "mid", "Recruiting, Onboarding, Payroll, Communication"),
    ("DevOps Engineer", "remote", "senior", "Docker, Kubernetes, CI/CD, AWS, Linux"),
    ("Customer Success Lead", "full_time", "mid", "CRM, Communication, Support, SaaS"),
    ("UX Research Intern", "internship", "entry", "Research, Interviews, Surveys, Figma"),
    ("Mobile Developer (Flutter)", "contract", "mid", "Flutter, Dart, REST, Firebase"),
]

FIRST = ["Amina", "Yusuf", "Sara", "Omar", "Leyla", "Hassan", "Maryam", "Ali", "Fatima", "Ibrahim"]
LAST = ["Ahmed", "Mohamed", "Hassan", "Abdi", "Farah", "Yusuf", "Ismail", "Osman", "Warsame", "Jama"]


class Command(BaseCommand):
    help = "Seed the database with demo data"

    def handle(self, *args, **options):
        self.stdout.write("Seeding demo data...")

        # --- Superuser ---
        if not User.objects.filter(email="admin@jobportal.local").exists():
            User.objects.create_superuser("admin@jobportal.local", "Admin@12345", first_name="Super", last_name="Admin")
            self.stdout.write(self.style.SUCCESS("  Created super admin: admin@jobportal.local / Admin@12345"))

        # --- Plans ---
        plans = [
            dict(name="Starter", slug="starter", price=0, job_post_limit=2, resume_views_limit=20, order=1,
                 description="Perfect for getting started.", features=["Email support"]),
            dict(name="Professional", slug="professional", price=49, job_post_limit=15, featured_job_limit=3,
                 resume_views_limit=200, has_ai_tools=True, has_analytics=True, is_popular=True, order=2,
                 description="For growing teams.", features=["Priority support", "AI candidate matching"]),
            dict(name="Enterprise", slug="enterprise", price=199, job_post_limit=100, featured_job_limit=25,
                 resume_views_limit=2000, has_ai_tools=True, has_analytics=True, order=3,
                 description="For large organizations.", features=["Dedicated manager", "Custom integrations", "SLA"]),
        ]
        for p in plans:
            Plan.objects.get_or_create(slug=p["slug"], defaults=p)

        # --- Categories ---
        categories = []
        for name, icon in CATEGORIES:
            cat, _ = JobCategory.objects.get_or_create(name=name, defaults={"icon": icon})
            categories.append(cat)

        # --- Employers + Companies ---
        companies = []
        for i, (name, org_type, industry, tagline) in enumerate(COMPANIES):
            email = f"employer{i+1}@jobportal.local"
            owner, created = User.objects.get_or_create(
                email=email,
                defaults={"role": "employer", "first_name": name.split()[0], "last_name": "Admin", "email_verified": True},
            )
            if created:
                owner.set_password("Employer@123")
                owner.save()
            company, _ = Company.objects.get_or_create(
                name=name,
                defaults={
                    "owner": owner, "org_type": org_type, "industry": industry, "tagline": tagline,
                    "about": f"{name} is a leader in {industry}. {tagline}", "location": "Mogadishu, Somalia",
                    "is_verified": True, "is_featured": i < 3, "size": "51-200",
                },
            )
            CompanyMember.objects.get_or_create(company=company, user=owner, defaults={"member_role": "owner"})
            companies.append(company)

        # --- Recruiter ---
        recruiter, created = User.objects.get_or_create(
            email="recruiter@jobportal.local",
            defaults={"role": "recruiter", "first_name": "Rita", "last_name": "Recruiter", "email_verified": True},
        )
        if created:
            recruiter.set_password("Recruiter@123")
            recruiter.save()
        CompanyMember.objects.get_or_create(company=companies[0], user=recruiter, defaults={"member_role": "recruiter"})

        # --- Jobs ---
        jobs = []
        for i, (title, jtype, level, skills) in enumerate(JOB_TITLES):
            company = companies[i % len(companies)]
            job, _ = Job.objects.get_or_create(
                title=title, company=company,
                defaults={
                    "posted_by": company.owner,
                    "assigned_recruiter": recruiter if i % 3 == 0 else None,
                    "category": random.choice(categories),
                    "job_type": jtype, "experience_level": level,
                    "work_mode": random.choice(["onsite", "remote", "hybrid"]),
                    "description": f"We are looking for a talented {title} to join {company.name}. "
                                   "You'll work on impactful projects with a world-class team.",
                    "responsibilities": "- Build and ship features\n- Collaborate with the team\n- Improve quality",
                    "requirements": f"- Experience as a {title}\n- Strong skills in {skills}\n- Great communication",
                    "benefits": "- Competitive salary\n- Remote friendly\n- Health insurance\n- Learning budget",
                    "skills": skills,
                    "location": random.choice(["Mogadishu", "Hargeisa", "Remote", "Nairobi"]),
                    "salary_min": random.choice([800, 1200, 1500, 2000]),
                    "salary_max": random.choice([2500, 3500, 5000, 7000]),
                    "vacancies": random.randint(1, 5),
                    "status": "published", "published_at": timezone.now() - timedelta(days=i),
                    "is_featured": i < 4, "is_urgent": i % 4 == 0,
                    "deadline": timezone.now().date() + timedelta(days=30),
                },
            )
            jobs.append(job)

        # --- Candidates ---
        candidates = []
        for i in range(12):
            email = f"candidate{i+1}@jobportal.local"
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "role": "candidate", "first_name": random.choice(FIRST),
                    "last_name": random.choice(LAST), "email_verified": True,
                },
            )
            if created:
                user.set_password("Candidate@123")
                user.save()
            profile, _ = CandidateProfile.objects.get_or_create(user=user)
            title, _, level, skills = random.choice(JOB_TITLES)
            profile.headline = title
            profile.current_title = title
            profile.summary = f"Passionate {title} with hands-on experience delivering quality work."
            profile.location = random.choice(["Mogadishu", "Hargeisa", "Nairobi"])
            profile.experience_years = random.randint(1, 8)
            profile.save()
            if not profile.skills.exists():
                for s in skills.split(",")[:4]:
                    Skill.objects.create(profile=profile, name=s.strip(), level=random.randint(60, 95))
                Experience.objects.create(profile=profile, company="Previous Co", title=title,
                                          description="Delivered key projects.", start_date=timezone.now().date() - timedelta(days=900))
                Education.objects.create(profile=profile, institution="BrightPath University",
                                         degree="BSc Computer Science", start_year=2016, end_year=2020)
            candidates.append(user)

        # --- Applications ---
        from apps.aifeatures.services import compute_match_score

        for job in jobs:
            for cand in random.sample(candidates, k=random.randint(2, 6)):
                app, created = JobApplication.objects.get_or_create(
                    job=job, candidate=cand,
                    defaults={
                        "cover_letter": "I'm excited to apply for this role.",
                        "status": random.choice(["applied", "reviewing", "shortlisted", "interview"]),
                    },
                )
                if created:
                    profile = getattr(cand, "candidate_profile", None)
                    if profile:
                        app.ai_match_score = compute_match_score(profile, job)
                        app.save(update_fields=["ai_match_score"])

        # --- CMS content ---
        faqs = [
            ("Is it free to create an account?", "Yes! Job seekers can create an account and apply to jobs completely free."),
            ("How does AI matching work?", "Our AI analyzes your profile, skills and experience to score how well you match each job."),
            ("Can I post jobs as an employer?", "Absolutely. Sign up as an employer, create your company profile and start posting."),
            ("Which payment methods are supported?", "Stripe, PayPal, Zaad, EVC Plus, Sahal and Premier Wallet."),
        ]
        for i, (q, a) in enumerate(faqs):
            FAQ.objects.get_or_create(question=q, defaults={"answer": a, "order": i})

        testimonials = [
            ("Amina Hassan", "Software Engineer", "TechNova", "Found my dream job in two weeks. The AI matching is spot on!"),
            ("Omar Yusuf", "HR Manager", "FinEdge", "Hiring has never been easier. The candidate ranking saves us hours."),
            ("Sara Ali", "Designer", "BrightPath", "The resume builder and ATS checker helped me land more interviews."),
        ]
        for name, role, company, quote in testimonials:
            Testimonial.objects.get_or_create(name=name, defaults={"role": role, "company": company, "quote": quote, "rating": 5})

        for name in ["TechNova", "BrightPath", "GreenFuture", "FinEdge", "PrimeHire"]:
            Partner.objects.get_or_create(name=name)

        posts = [
            ("10 Resume Tips That Actually Work", "Learn how to craft a resume that beats the ATS and lands interviews."),
            ("How to Ace Your Next Interview", "Preparation strategies and common questions to expect."),
            ("Remote Work: Finding the Right Fit", "What to look for when applying to remote-first companies."),
        ]
        admin_user = User.objects.filter(role="super_admin").first()
        for title, excerpt in posts:
            BlogPost.objects.get_or_create(
                title=title,
                defaults={"author": admin_user, "excerpt": excerpt,
                          "content": excerpt + "\n\n" + "This is sample article content for the demo platform. " * 12},
            )

        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully!"))
        self.stdout.write("")
        self.stdout.write("Login credentials:")
        self.stdout.write("  Super Admin : admin@jobportal.local / Admin@12345")
        self.stdout.write("  Employer    : employer1@jobportal.local / Employer@123")
        self.stdout.write("  Recruiter   : recruiter@jobportal.local / Recruiter@123")
        self.stdout.write("  Candidate   : candidate1@jobportal.local / Candidate@123")

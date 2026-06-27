"""AI service layer.

These are deterministic, dependency-free heuristics that emulate the AI
features (matching, ATS scoring, generation). They expose a clean interface so
they can later be swapped for an LLM provider (OpenAI / local model) without
touching callers. The provider is selected via ``settings.OPENAI_API_KEY``.
"""
from __future__ import annotations

import re
from collections import Counter

STOPWORDS = {
    "the", "and", "for", "with", "you", "are", "our", "your", "will", "have",
    "this", "that", "from", "they", "their", "has", "was", "but", "not", "all",
    "can", "who", "out", "use", "job", "work", "role", "team", "a", "an", "to",
    "of", "in", "on", "is", "as", "at", "or", "be", "we", "it",
}


def _tokenize(text: str) -> list[str]:
    return [t for t in re.findall(r"[a-zA-Z][a-zA-Z+#.]{1,}", (text or "").lower()) if t not in STOPWORDS]


def _keywords(text: str, top: int = 40) -> set[str]:
    counts = Counter(_tokenize(text))
    return {word for word, _ in counts.most_common(top)}


def compute_match_score(profile, job) -> int:
    """Score 0-100 of how well a candidate profile matches a job."""
    job_skills = {s.lower() for s in job.skill_list}
    profile_skills = {s.name.lower() for s in profile.skills.all()}

    score = 0.0

    # Skill overlap (50%)
    if job_skills:
        overlap = len(job_skills & profile_skills) / len(job_skills)
        score += overlap * 50
    else:
        score += 25

    # Keyword overlap between job text and profile text (25%)
    job_kw = _keywords(" ".join([job.title, job.description, job.requirements, job.skills]))
    profile_text = " ".join(
        [profile.headline, profile.summary, profile.current_title]
        + [e.title for e in profile.experience.all()]
        + [s.name for s in profile.skills.all()]
    )
    profile_kw = _keywords(profile_text)
    if job_kw:
        score += (len(job_kw & profile_kw) / len(job_kw)) * 25

    # Experience match (15%)
    if profile.experience_years >= job.min_experience_years:
        score += 15
    elif job.min_experience_years:
        score += max(0, 15 * profile.experience_years / job.min_experience_years)

    # Remote / availability fit (10%)
    if profile.open_to_remote or job.work_mode != "remote":
        score += 10

    return max(0, min(100, round(score)))


def ats_score(resume_text: str, job_description: str = "") -> dict:
    """Resume ATS check: structure + keyword coverage."""
    text = resume_text or ""
    lower = text.lower()
    words = _tokenize(text)
    word_count = len(words)

    sections = {
        "Contact info": bool(re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", text)) or bool(re.search(r"\+?\d[\d \-]{7,}", text)),
        "Experience": any(k in lower for k in ["experience", "worked", "employment", "responsib"]),
        "Education": any(k in lower for k in ["education", "degree", "university", "bachelor", "master"]),
        "Skills": "skill" in lower or "," in text,
        "Summary": any(k in lower for k in ["summary", "objective", "profile"]),
    }
    structure_score = sum(sections.values()) / len(sections) * 50

    keyword_score = 25
    matched_keywords: list[str] = []
    missing_keywords: list[str] = []
    if job_description:
        job_kw = _keywords(job_description)
        resume_kw = set(words)
        matched = job_kw & resume_kw
        missing = job_kw - resume_kw
        matched_keywords = sorted(matched)[:20]
        missing_keywords = sorted(missing)[:20]
        keyword_score = (len(matched) / len(job_kw) * 50) if job_kw else 25

    length_score = 25 if 200 <= word_count <= 900 else (15 if word_count else 0)

    total = round(structure_score + keyword_score + length_score)
    total = max(0, min(100, total))

    suggestions = []
    for name, present in sections.items():
        if not present:
            suggestions.append(f"Add a clear '{name}' section.")
    if word_count < 200:
        suggestions.append("Your resume looks short — aim for 400-800 words with quantified achievements.")
    if missing_keywords:
        suggestions.append("Include relevant keywords: " + ", ".join(missing_keywords[:8]) + ".")
    if not suggestions:
        suggestions.append("Great job! Your resume is well structured and keyword-rich.")

    return {
        "score": total,
        "sections": sections,
        "word_count": word_count,
        "matched_keywords": matched_keywords,
        "missing_keywords": missing_keywords,
        "suggestions": suggestions,
    }


def generate_cover_letter(candidate_name: str, job_title: str, company: str, skills: list[str]) -> str:
    skills_text = ", ".join(skills[:5]) if skills else "the required skills"
    return (
        f"Dear Hiring Manager,\n\n"
        f"I am writing to express my strong interest in the {job_title} position at {company}. "
        f"With a solid background and proven strengths in {skills_text}, I am confident I can make "
        f"a meaningful contribution to your team.\n\n"
        f"Throughout my career I have focused on delivering measurable results, collaborating across "
        f"teams, and continuously improving my craft. The opportunity at {company} excites me because "
        f"it aligns closely with my expertise and career goals.\n\n"
        f"I would welcome the chance to discuss how my experience can support {company}'s objectives. "
        f"Thank you for considering my application.\n\n"
        f"Sincerely,\n{candidate_name}"
    )


def generate_job_description(title: str, skills: list[str]) -> dict:
    skills_text = ", ".join(skills) if skills else "relevant tools and technologies"
    return {
        "description": (
            f"We are seeking a talented {title} to join our growing team. In this role you will own "
            f"key initiatives, collaborate with cross-functional stakeholders, and help drive impact "
            f"across the organisation."
        ),
        "responsibilities": (
            f"- Deliver high-quality work as a {title}.\n"
            f"- Collaborate with team members and stakeholders.\n"
            f"- Continuously improve processes and outcomes.\n"
            f"- Stay current with industry best practices."
        ),
        "requirements": (
            f"- Proven experience relevant to a {title} role.\n"
            f"- Strong skills in {skills_text}.\n"
            f"- Excellent communication and problem-solving abilities.\n"
            f"- Ability to work independently and within a team."
        ),
    }


def rank_candidates(job, applications) -> list:
    """Return applications sorted by AI match score (desc)."""
    scored = []
    for app in applications:
        profile = getattr(app.candidate, "candidate_profile", None)
        score = compute_match_score(profile, job) if profile else app.ai_match_score
        scored.append((score, app))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [app for _, app in scored]


def skill_gap_analysis(profile, job) -> dict:
    job_skills = {s.strip() for s in job.skill_list}
    have = {s.name for s in profile.skills.all()}
    have_lower = {s.lower() for s in have}
    missing = [s for s in job_skills if s.lower() not in have_lower]
    matched = [s for s in job_skills if s.lower() in have_lower]
    return {"matched": matched, "missing": missing, "have": sorted(have)}

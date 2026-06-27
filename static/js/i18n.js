/*
 * Lightweight client-side i18n for English (en) and Somali (so).
 * - No page reload: swaps text via [data-i18n] / [data-i18n-placeholder] attributes.
 * - Persists choice in localStorage and auto-detects on load.
 * - Exposes window.setLanguage(lang) and window.t(key).
 */
(function () {
  "use strict";

  const translations = {
    en: {
      // Navbar
      "nav.find_jobs": "Find Jobs",
      "nav.companies": "Companies",
      "nav.career": "Career Advice",
      "nav.pricing": "Pricing",
      "nav.signin": "Sign in",
      "nav.get_started": "Get Started",
      "nav.dashboard": "Dashboard",
      "nav.post_job": "Post a Job",
      "nav.search_placeholder": "Search jobs...",
      "nav.browse_category": "Browse by category",
      "nav.featured_jobs": "Featured Jobs",
      "nav.view_all_jobs": "View all jobs",
      "nav.notifications": "Notifications",
      "nav.view_all": "View all",
      "nav.no_notifications": "No notifications",
      "nav.settings": "Settings",
      "nav.signout": "Sign out",
      "nav.my_resume": "My Resume",
      "nav.applications": "Applications",
      "nav.remote": "Remote",
      "nav.full_time": "Full Time",
      "nav.internships": "Internships",
      "nav.contract": "Contract",
      // Hero
      "hero.badge": "AI-powered matching & resume tools",
      "hero.title": "Find your dream job or your next great hire",
      "hero.subtitle": "The enterprise recruitment platform for companies, recruiters, universities, NGOs and governments — powered by intelligent candidate matching.",
      "hero.job_placeholder": "Job title, keyword or company",
      "hero.location_placeholder": "Location",
      "hero.search_jobs": "Search Jobs",
      "hero.popular": "Popular:",
      "hero.developer": "Developer",
      "hero.designer": "Designer",
      // Stats
      "stats.jobs": "Active Jobs",
      "stats.companies": "Companies",
      "stats.candidates": "Candidates",
      "stats.applications": "Applications",
      // Sections
      "sections.popular_categories": "Popular Categories",
      "sections.explore_field": "Explore opportunities by field",
      "sections.featured_jobs": "Featured Jobs",
      "sections.handpicked": "Hand-picked opportunities for you",
      "sections.browse_all": "Browse all jobs →",
      "sections.view_all": "View all →",
      "sections.ai_powered": "Powered by AI",
      "sections.smarter": "Smarter hiring, smarter job search",
      "sections.ai_resume": "AI Resume & ATS Checker",
      "sections.ai_resume_desc": "Instant ATS score, keyword gaps, and optimization tips to get past recruiters.",
      "sections.ai_match": "AI Candidate Matching",
      "sections.ai_match_desc": "Smart match scores rank the best candidates for every role automatically.",
      "sections.ai_advisor": "AI Career Advisor",
      "sections.ai_advisor_desc": "Personalized job recommendations and skill-gap analysis for your growth.",
      "sections.top_companies": "Top Companies Hiring",
      "sections.loved": "Loved by professionals",
      "sections.cta_title": "Ready to take the next step?",
      "sections.cta_sub": "Join thousands of candidates and employers building the future of work.",
      "sections.create_account": "Create free account",
      "sections.browse_jobs": "Browse jobs",
      // Footer
      "footer.newsletter_title": "Get the latest jobs in your inbox",
      "footer.newsletter_sub": "Join our newsletter — no spam, unsubscribe anytime.",
      "footer.subscribe": "Subscribe",
      "footer.email_placeholder": "Enter your email",
      "footer.desc": "The AI-powered recruitment platform connecting world-class talent with companies, recruiters, universities, NGOs and governments.",
      "footer.for_candidates": "For Candidates",
      "footer.for_employers": "For Employers",
      "footer.company": "Company",
      "footer.categories": "Categories",
      "footer.browse_jobs": "Browse Jobs",
      "footer.remote_jobs": "Remote Jobs",
      "footer.resume_checker": "Resume Checker",
      "footer.career_advisor": "Career Advisor",
      "footer.create_profile": "Create Profile",
      "footer.post_job": "Post a Job",
      "footer.pricing": "Pricing",
      "footer.api_docs": "API Docs",
      "footer.about": "About Us",
      "footer.blog": "Blog",
      "footer.faqs": "FAQs",
      "footer.contact": "Contact",
      "footer.all_jobs": "All Jobs",
      "footer.rights": "All rights reserved.",
      "footer.privacy": "Privacy",
      "footer.terms": "Terms",
    },
    so: {
      // Navbar
      "nav.find_jobs": "Raadi Shaqo",
      "nav.companies": "Shirkadaha",
      "nav.career": "Talo Xirfadeed",
      "nav.pricing": "Qiimaha",
      "nav.signin": "Soo Gal",
      "nav.get_started": "Bilow",
      "nav.dashboard": "Dashboard-ka",
      "nav.post_job": "Dhig Shaqo",
      "nav.search_placeholder": "Raadi shaqooyin...",
      "nav.browse_category": "Ka raadi qaybaha",
      "nav.featured_jobs": "Shaqooyin La Doortay",
      "nav.view_all_jobs": "Eeg dhammaan shaqooyinka",
      "nav.notifications": "Ogeysiisyada",
      "nav.view_all": "Eeg dhammaan",
      "nav.no_notifications": "Ogeysiis ma jiro",
      "nav.settings": "Dejinta",
      "nav.signout": "Ka Bax",
      "nav.my_resume": "CV-gayga",
      "nav.applications": "Codsiyada",
      "nav.remote": "Fog (Remote)",
      "nav.full_time": "Waqti Buuxa",
      "nav.internships": "Tababar",
      "nav.contract": "Qandaraas",
      // Hero
      "hero.badge": "Is-barbar dhig AI iyo qalabka CV-ga",
      "hero.title": "Hel shaqada aad ku riyoonayso ama shaqaalahaaga xiga",
      "hero.subtitle": "Madal shaqaalaysiin oo casri ah oo loogu talagalay shirkadaha, shaqaalaysiiyayaasha, jaamacadaha, hay'adaha iyo dawladaha — oo ay ku shaqayso is-barbardhig caqli leh.",
      "hero.job_placeholder": "Cinwaanka shaqada, erey ama shirkad",
      "hero.location_placeholder": "Goobta",
      "hero.search_jobs": "Raadi Shaqooyin",
      "hero.popular": "Caan ah:",
      "hero.developer": "Horumariye",
      "hero.designer": "Naqshadeeye",
      // Stats
      "stats.jobs": "Shaqooyin Firfircoon",
      "stats.companies": "Shirkado",
      "stats.candidates": "Codsadayaal",
      "stats.applications": "Codsiyo",
      // Sections
      "sections.popular_categories": "Qaybaha Caanka ah",
      "sections.explore_field": "Sahmi fursadaha qaybeed",
      "sections.featured_jobs": "Shaqooyin La Doortay",
      "sections.handpicked": "Fursado gaar ahaan laguu doortay",
      "sections.browse_all": "Eeg dhammaan shaqooyinka →",
      "sections.view_all": "Eeg dhammaan →",
      "sections.ai_powered": "Waxaa hawl-gelisa AI",
      "sections.smarter": "Shaqaalaysiin caqli leh, raadin shaqo caqli leh",
      "sections.ai_resume": "Hubiyaha CV & ATS ee AI",
      "sections.ai_resume_desc": "Dhibco ATS degdeg ah, ereyo maqan, iyo talooyin hagaajin si aad ula gudubto shaqaalaysiiyayaasha.",
      "sections.ai_match": "Is-barbardhig Codsade ee AI",
      "sections.ai_match_desc": "Dhibcaha is-barbardhigga ayaa si toos ah u kala saara codsadayaasha ugu fiican shaqo kasta.",
      "sections.ai_advisor": "Lataliye Xirfadeed ee AI",
      "sections.ai_advisor_desc": "Talooyin shaqo oo gaar ah iyo falanqayn xirfadeed oo kobcintaada ah.",
      "sections.top_companies": "Shirkadaha ugu Sarreeya ee Shaqaalaynaya",
      "sections.loved": "Waxaa jecel xirfadlayaasha",
      "sections.cta_title": "Diyaar ma u tahay tallaabada xigta?",
      "sections.cta_sub": "Ku biir kumannaan codsadayaal iyo shaqaalaysiiyayaal ah oo dhisaya mustaqbalka shaqada.",
      "sections.create_account": "Samee akoon bilaash ah",
      "sections.browse_jobs": "Eeg shaqooyinka",
      // Footer
      "footer.newsletter_title": "Hel shaqooyinka ugu dambeeyay sanduuqaaga",
      "footer.newsletter_sub": "Ku biir warsidahayaga — spam ma jiro, goor kasta ka bixi kartaa.",
      "footer.subscribe": "Is-diiwaangeli",
      "footer.email_placeholder": "Geli iimaylkaaga",
      "footer.desc": "Madasha shaqaalaysiinta ee AI ku shaqaysa oo isku xirta hibada heer caalami ah iyo shirkadaha, shaqaalaysiiyayaasha, jaamacadaha, hay'adaha iyo dawladaha.",
      "footer.for_candidates": "Codsadayaasha",
      "footer.for_employers": "Shaqaalaysiiyayaasha",
      "footer.company": "Shirkadda",
      "footer.categories": "Qaybaha",
      "footer.browse_jobs": "Eeg Shaqooyinka",
      "footer.remote_jobs": "Shaqooyin Fog",
      "footer.resume_checker": "Hubiyaha CV",
      "footer.career_advisor": "Lataliye Xirfadeed",
      "footer.create_profile": "Samee Profile",
      "footer.post_job": "Dhig Shaqo",
      "footer.pricing": "Qiimaha",
      "footer.api_docs": "Dukumeentiga API",
      "footer.about": "Nagu Saabsan",
      "footer.blog": "Blog",
      "footer.faqs": "Su'aalaha",
      "footer.contact": "Nala Soo Xiriir",
      "footer.all_jobs": "Dhammaan Shaqooyinka",
      "footer.rights": "Dhammaan xuquuqdu way xf-an tahay.",
      "footer.privacy": "Asturnaanta",
      "footer.terms": "Shuruudaha",
    },
  };

  const STORAGE_KEY = "site_lang";

  function t(key, lang) {
    lang = lang || getLanguage();
    return (translations[lang] && translations[lang][key]) || (translations.en[key] || key);
  }

  function getLanguage() {
    return localStorage.getItem(STORAGE_KEY) || "en";
  }

  function applyTranslations(lang) {
    document.querySelectorAll("[data-i18n]").forEach(function (el) {
      const key = el.getAttribute("data-i18n");
      const val = translations[lang] && translations[lang][key];
      if (val !== undefined) el.textContent = val;
    });
    document.querySelectorAll("[data-i18n-placeholder]").forEach(function (el) {
      const key = el.getAttribute("data-i18n-placeholder");
      const val = translations[lang] && translations[lang][key];
      if (val !== undefined) el.setAttribute("placeholder", val);
    });
  }

  function updateToggleState(lang) {
    document.querySelectorAll("[data-lang-btn]").forEach(function (btn) {
      const active = btn.getAttribute("data-lang-btn") === lang;
      btn.classList.toggle("lang-active", active);
      btn.setAttribute("aria-pressed", active ? "true" : "false");
    });
  }

  function setLanguage(lang) {
    if (!translations[lang]) lang = "en";
    localStorage.setItem(STORAGE_KEY, lang);
    document.documentElement.setAttribute("lang", lang);

    // Smooth fade animation while swapping content.
    const root = document.body;
    root.classList.add("lang-switching");
    window.setTimeout(function () {
      applyTranslations(lang);
      updateToggleState(lang);
      if (window.lucide) window.lucide.createIcons();
      root.classList.remove("lang-switching");
    }, 120);
  }

  // Public API
  window.setLanguage = setLanguage;
  window.getLanguage = getLanguage;
  window.t = t;

  // Initialise on load (auto-detect last selection).
  function init() {
    const lang = getLanguage();
    document.documentElement.setAttribute("lang", lang);
    applyTranslations(lang);
    updateToggleState(lang);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();

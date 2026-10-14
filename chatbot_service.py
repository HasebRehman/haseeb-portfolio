import os
import re
import json
import time
import urllib.request
import urllib.error
from typing import Dict, Any, Tuple, List

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Auto-load .env file if it exists
def load_env():
    env_path = os.path.join(CURRENT_DIR, ".env")
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        os.environ.setdefault(k.strip(), v.strip())
        except Exception:
            pass

load_env()

# Configuration
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "").strip()
USER_QUERY_LIMIT = int(os.environ.get("USER_QUERY_LIMIT", "10"))

# Per-user query counter: { user_id: { "count": int, "reset_time": float } }
USER_USAGE: Dict[str, Dict[str, Any]] = {}
USAGE_WINDOW_SECONDS = 86400  # 24 hours

# Haseeb's Knowledge Base & Context
HASEEB_PROFILE = {
    "name": "Haseeb Rehman",
    "role": "Senior Full-Stack & SaaS Web Developer",
    "experience": "3+ years of professional experience, with 50+ successful projects delivered worldwide.",
    "education": "BSc in Computer Science from NUML, Lahore (CGPA 3.63)",
    "current_job": "Senior Web Developer at Digitsio",
    "location": "Lahore, Pakistan (available for remote contracts, full-time, and freelance worldwide)",
    "contacts": {
        "email": "haseebrehman3460@gmail.com",
        "whatsapp": "+92 326 8795099",
        "whatsapp_link": "https://wa.me/923268795099",
        "linkedin": "https://www.linkedin.com/in/haseebrehmanweb/",
        "github": "https://github.com/HasebRehman",
        "cv_download": "/public/CV-2/Haseeb_Rehman_CV.pdf"
    },
    "skills": {
        "frontend": ["React.js", "Next.js", "TypeScript", "JavaScript (ES6+)", "Tailwind CSS", "Bootstrap 5", "GSAP animations", "HTML5", "CSS3", "Responsive UI"],
        "backend": ["Node.js", "NestJS", "Express.js", "Python", "RESTful APIs", "Microservices", "JWT / Auth", "Socket.io"],
        "databases_cloud": ["PostgreSQL", "MongoDB", "MySQL", "Supabase", "Firebase", "Redis", "Vercel", "Docker"],
        "ai_automation": ["OpenAI & Gemini API Integrations", "Groq LLM Acceleration", "Custom AI Chatbots", "LangChain", "Automated Business Workflows"],
        "cms_ecommerce": ["WordPress", "Shopify", "Webflow", "WooCommerce"]
    },
    "services": [
        "Custom Full-Stack Web Development (React, Next.js, Node.js, TypeScript)",
        "SaaS Web Applications (End-to-end architecture, multi-tenant, billing & subscriptions)",
        "AI Chatbots & Intelligent Automation (Gemini, OpenAI, LLM workflows)",
        "API Development & 3rd-Party Integrations (Payment gateways, CRMs, webhooks)",
        "Internal Tools & Custom Admin Dashboards",
        "Website Performance Optimization, SEO & High Speed Audits"
    ],
    "featured_projects": [
        {"title": "Veylohr", "desc": "A full-stack scalable HR management SaaS platform", "link": "https://veylohr.com/", "category": "SaaS Platform"},
        {"title": "Lizzt", "desc": "A collaborative event app with real-time tracking", "link": "https://lizzt.app/", "category": "Web App"},
        {"title": "Pakhims", "desc": "Hospital management brand portal and medical marketing web app", "link": "https://pakhims.com/", "category": "Healthcare"},
        {"title": "VendoSphere", "desc": "A modern, high-speed online e-commerce storefront", "link": "https://ecommerce-one-tau-62.vercel.app/", "category": "E-Commerce"},
        {"title": "Illinois Dental", "desc": "A clean, modern medical practice web application", "link": "https://dental-website-lovat.vercel.app/", "category": "Healthcare"},
        {"title": "Opa Bar", "desc": "Dining experience and online reservation website", "link": "https://opa-sable-seven.vercel.app/", "category": "Hospitality"}
    ]
}

SYSTEM_PROMPT = f"""You are the official AI Portfolio Assistant for Haseeb Rehman.
Your ONLY role is to represent Haseeb Rehman and assist visitors with questions about his professional background, technical skills, services, projects, and how to contact or hire him.

Key Information about Haseeb Rehman:
- Name: {HASEEB_PROFILE['name']}
- Title: {HASEEB_PROFILE['role']}
- Experience: {HASEEB_PROFILE['experience']}
- Education: {HASEEB_PROFILE['education']}
- Current Position: {HASEEB_PROFILE['current_job']}
- Location: {HASEEB_PROFILE['location']}
- Key Skills:
  * Frontend: {', '.join(HASEEB_PROFILE['skills']['frontend'])}
  * Backend: {', '.join(HASEEB_PROFILE['skills']['backend'])}
  * Databases & Cloud: {', '.join(HASEEB_PROFILE['skills']['databases_cloud'])}
  * AI & Automation: {', '.join(HASEEB_PROFILE['skills']['ai_automation'])}
  * CMS: {', '.join(HASEEB_PROFILE['skills']['cms_ecommerce'])}
- Services OFFERED:
{chr(10).join(['  * ' + s for s in HASEEB_PROFILE['services']])}
- Services NOT OFFERED (IMPORTANT):
  * Graphic Design & Logo Design (NOT offered)
  * Digital Marketing, Social Media Marketing & Ads Campaigns (NOT offered)
  * Content Writing / Copywriting (NOT offered)
  * Video Editing (NOT offered)
  * Haseeb focuses exclusively on software engineering, web application development, SaaS platforms, and AI integrations. If asked about unsupported services, clearly and politely clarify this distinction.
- Featured Projects:
{chr(10).join(['  * ' + p['title'] + ' (' + p['category'] + '): ' + p['desc'] + ' [' + p['link'] + ']' for p in HASEEB_PROFILE['featured_projects']])}
- Contact Details:
  * Email: {HASEEB_PROFILE['contacts']['email']}
  * WhatsApp: {HASEEB_PROFILE['contacts']['whatsapp']} ({HASEEB_PROFILE['contacts']['whatsapp_link']})
  * LinkedIn: {HASEEB_PROFILE['contacts']['linkedin']}
  * GitHub: {HASEEB_PROFILE['contacts']['github']}
  * Resume / CV: {HASEEB_PROFILE['contacts']['cv_download']}

STRICT INSTRUCTIONS & RESPONSE RULES:
1. ONLY answer questions related to Haseeb Rehman, his portfolio, skills, projects, work, experience, services, and hiring/contacting him.
2. If asked about general unrelated topics (e.g. math problems, general coding homework, recipes, politics, weather, entertainment), politely decline and state:
   "I am Haseeb Rehman's dedicated portfolio assistant. I can only assist with questions regarding Haseeb's background, technical skills, web & SaaS projects, and services. Feel free to ask about his work or how to hire him!"
3. If asked about services he does NOT offer (such as graphic designing, digital marketing, etc.), clearly state that Haseeb does not offer them, and highlight his core strengths in Full-Stack Web Development, SaaS Platforms, and Custom AI Integrations.
4. COMPLETION GUARANTEE: ALWAYS finish every thought, bullet point, and sentence completely. NEVER leave a sentence half-finished or truncated. Keep answers concise (between 80 and 180 words) and nicely formatted in markdown.
5. Always be polite, professional, and invite the visitor to reach out directly to Haseeb on WhatsApp ({HASEEB_PROFILE['contacts']['whatsapp']}) or Email ({HASEEB_PROFILE['contacts']['email']}).
"""

# Scope guardrail patterns: keywords that indicate the query is on-topic
RELEVANT_PATTERNS = [
    r"\b(hi|hello|hey|greetings|hola|assalam|aoa)\b",
    r"\b(who\s+are\s+you|what\s+can\s+you\s+do|help|what\s+is\s+this)\b",
    r"\b(haseeb|rehman|portfolio|profile|developer|coder|programmer|engineer)\b",
    r"\b(about\s+(haseeb|you|him|yourself|developer|work)|who\s+is\s+haseeb|tell\s+me\s+about|bio|background|experience|education|degree|numl|cgpa|digitsio)\b",
    r"\b(skill|skills|stack|tech|technologies|react|next|node|typescript|python|nestjs|express|frontend|backend|fullstack|full-stack|full\s+stack|css|tailwind|bootstrap|html|database|postgres|mongodb|sql|ai|llm|api|apis)\b",
    r"\b(service|services|build|develop|create|offer|what\s+do\s+you\s+do|capabilities|provide|giving|do\s+you|can\s+you|does\s+he|is\s+he)\b",
    r"\b(graphic|design|designing|logo|marketing|seo|video|content)\b",
    r"\b(project|projects|work|showcase|app|apps|website|websites|web\s+app|saas|veylohr|lizzt|pakhims|vendosphere|dental|opa)\b",
    r"\b(contact|hire|hiring|email|phone|whatsapp|call|reach|message|touch|linkedin|github|cv|resume|download|location|rates?|cost|price|pricing|quote|freelance|contract|remote)\b"
]

OFF_TOPIC_PATTERNS = [
    r"\b(solve|equation|recipe|cook|baking|weather|forecast|translate|translation|poem|poetry|story|joke|riddle|sports|football|cricket|who\s+won|president|prime\s+minister|capital\s+of|movie|song|lyrics|banana|fruit|animal|cat|dog)\b",
    r"\b(write\s+(a\s+)?(code|script|program)\s+for\s+(bubble|quick|binary|fibonacci|dijkstra|matrix))\b",
    r"\b(math|calculus|algebra|physics|chemistry|history|biology|geography|philosophy)\b",
    r"\b(homework|assignment|essay\s+on|essay\s+about)\b"
]

def is_relevant_to_portfolio(user_query: str) -> bool:
    """Check if the user question is relevant to Haseeb and his portfolio."""
    if not user_query or not user_query.strip():
        return False
    
    clean_query = user_query.strip().lower()
    
    # Check off-topic indicators FIRST
    for pattern in OFF_TOPIC_PATTERNS:
        if re.search(pattern, clean_query):
            return False

    # Check if query matches any portfolio-related pattern
    for pattern in RELEVANT_PATTERNS:
        if re.search(pattern, clean_query):
            return True
            
    return False

def check_user_rate_limit(user_id: str) -> Tuple[bool, int, int]:
    """
    Check if the user has exceeded their free query quota.
    Returns: (is_allowed, current_count, limit)
    """
    now = time.time()
    usage = USER_USAGE.get(user_id)
    
    if not usage or (now - usage.get("reset_time", 0)) > USAGE_WINDOW_SECONDS:
        USER_USAGE[user_id] = {"count": 0, "reset_time": now}
        usage = USER_USAGE[user_id]
        
    current_count = usage["count"]
    if current_count >= USER_QUERY_LIMIT:
        return False, current_count, USER_QUERY_LIMIT
        
    return True, current_count, USER_QUERY_LIMIT

def record_user_usage(user_id: str):
    """Increment the user query count."""
    if user_id in USER_USAGE:
        USER_USAGE[user_id]["count"] += 1
    else:
        USER_USAGE[user_id] = {"count": 1, "reset_time": time.time()}

# ----------------- Smart Local Default Answers -----------------

def get_default_answer(user_query: str) -> str:
    """
    Smart, comprehensive fallback answers when AI is unavailable,
    quota is exhausted, or user has reached their query limit.
    Ensures ZERO error messages are ever shown to visitors.
    """
    q = user_query.lower()

    # 0. Services NOT Offered: Graphic design, marketing, etc.
    if re.search(r"\b(graphic|designing|logo|marketing|seo\s+campaign|social\s+media|video\s+edit)\b", q):
        return (
            "**Services Clarification ℹ️**\n\n"
            "Haseeb Rehman focuses strictly on **Full-Stack Web Development, SaaS Platform Engineering, and Custom AI Integrations**.\n\n"
            "He does **not** provide graphic designing, logo design, or digital marketing services. However, if you need a high-performance web application, SaaS platform, or custom API built, Haseeb delivers end-to-end development!\n\n"
            "• Explore his core capabilities on the [Services Page](/services).\n"
            "• Or contact Haseeb directly on [WhatsApp (+92 326 8795099)](https://wa.me/923268795099) to discuss your software project."
        )

    # 1. Contact & Hire & WhatsApp & Email
    if re.search(r"\b(contact|hire|email|whatsapp|phone|reach|call|touch|quote|rate|price|pricing|freelance)\b", q):
        return (
            "**Let's Connect with Haseeb Rehman! 🚀**\n\n"
            "Haseeb is currently available for freelance projects, SaaS consulting, and full-time remote contracts.\n\n"
            "• **WhatsApp:** [+92 326 8795099](https://wa.me/923268795099)\n"
            "• **Email:** [haseebrehman3460@gmail.com](mailto:haseebrehman3460@gmail.com)\n"
            "• **LinkedIn:** [linkedin.com/in/haseebrehmanweb](https://www.linkedin.com/in/haseebrehmanweb/)\n"
            "• **GitHub:** [github.com/HasebRehman](https://github.com/HasebRehman)\n\n"
            "Feel free to drop a message directly on WhatsApp for the quickest response!"
        )

    # 2. CV / Resume
    if re.search(r"\b(cv|resume)\b", q):
        return (
            "**Download Haseeb Rehman's CV 📄**\n\n"
            "You can download his updated curriculum vitae directly using the link below:\n\n"
            "👉 [Download Haseeb Rehman CV](/public/CV-2/Haseeb_Rehman_CV.pdf)\n\n"
            "It includes his complete professional work history at Digitsio, academic credentials from NUML, and technical project breakdown."
        )

    # 3. Projects & Work
    if re.search(r"\b(project|projects|work|showcase|built|apps|websites|veylohr|lizzt|pakhims|vendosphere|dental|opa)\b", q):
        return (
            "**Featured Projects by Haseeb Rehman 💼**\n\n"
            "Haseeb has delivered 50+ successful production platforms. Here are several standout highlights:\n\n"
            "1. **[Veylohr](https://veylohr.com/)** — Full-stack scalable HR management SaaS platform.\n"
            "2. **[Lizzt](https://lizzt.app/)** — Collaborative event and task app with live updates.\n"
            "3. **[Pakhims](https://pakhims.com/)** — Hospital management brand portal & healthcare web app.\n"
            "4. **[VendoSphere](https://ecommerce-one-tau-62.vercel.app/)** — High-performance modern e-commerce platform.\n"
            "5. **[Illinois Dental](https://dental-website-lovat.vercel.app/)** — Professional healthcare practice web application.\n"
            "6. **[Opa Bar](https://opa-sable-seven.vercel.app/)** — Dining experience and online reservations.\n\n"
            "Explore full details on the [Projects Page](/projects)!"
        )

    # 4. Skills & Tech Stack
    if re.search(r"\b(skill|skills|tech|stack|technologies|react|next|node|typescript|python|backend|frontend|languages|tools|database|mongo|postgres)\b", q):
        return (
            "**Haseeb Rehman's Technical Stack ⚡**\n\n"
            "• **Frontend:** React.js, Next.js, TypeScript, JavaScript (ES6+), Tailwind CSS, Bootstrap 5, GSAP Animations.\n"
            "• **Backend:** Node.js, NestJS, Express.js, Python, RESTful APIs, Microservices, Socket.io.\n"
            "• **Databases & Cloud:** PostgreSQL, MongoDB, Supabase, Firebase, Redis, Vercel, Docker.\n"
            "• **AI & Automation:** Gemini API, OpenAI, Groq LLM pipelines, AI Chatbots, automated workflow integrations.\n"
            "• **CMS & E-Commerce:** WordPress, Shopify, Webflow, WooCommerce.\n\n"
            "Haseeb focuses on clean code, responsive layouts, and lightning-fast web performance!"
        )

    # 5. Services
    if re.search(r"\b(service|services|offer|what\s+do\s+you\s+do|capabilities|what\s+can\s+you\s+build)\b", q):
        return (
            "**Services Offered by Haseeb Rehman 🛠️**\n\n"
            "1. **Full-Stack Web Development:** Modern, dynamic web applications built with Next.js, React, and Node.js.\n"
            "2. **SaaS Product Engineering:** End-to-end multi-tenant platforms with user auth, billing, and database architecture.\n"
            "3. **AI Chatbots & Intelligent Integration:** Integrating smart assistants and automated business workflows.\n"
            "4. **API Development & Integrations:** Secure REST APIs, payment gateways (Stripe, PayPal), and CRM syncing.\n"
            "5. **Performance Optimization:** Core Web Vitals enhancement, high-speed refactoring, and modern SEO.\n\n"
            "Visit the [Services Page](/services) or message Haseeb to discuss your requirements!"
        )

    # 6. About & Education & Experience
    if re.search(r"\b(about|bio|education|degree|numl|cgpa|digitsio|experience|who\s+is\s+haseeb|years)\b", q):
        return (
            "**About Haseeb Rehman 👨‍💻**\n\n"
            "• **Current Role:** Senior Web Developer at **Digitsio**.\n"
            "• **Education:** Bachelor of Science in Computer Science from **NUML Lahore** (CGPA: 3.63).\n"
            "• **Experience:** 3+ years crafting scalable web apps, SaaS products, and custom websites.\n"
            "• **Track Record:** 50+ production projects delivered for international clients across USA, Europe, and the Middle East.\n"
            "• **Location:** Lahore, Pakistan (Available for remote global contracts).\n\n"
            "Learn more on the [About Page](/about)!"
        )

    # 7. Pure Greetings
    if re.search(r"\b(hi|hello|hey|greetings|aoa|assalam)\b", q):
        return (
            "**Hello! 👋 Welcome to Haseeb Rehman's Portfolio!**\n\n"
            "I'm Haseeb's AI Assistant. Haseeb is a **Senior Full-Stack & SaaS Web Developer** with 3+ years of experience and over 50+ projects delivered worldwide.\n\n"
            "How can I help you today? You can ask about:\n"
            "• **Skills & Tech Stack**\n"
            "• **Featured Projects & Demos**\n"
            "• **Web & SaaS Services**\n"
            "• **How to Hire or Contact Haseeb**"
        )

    # Default general portfolio answer
    return (
        "**Haseeb Rehman — Senior Full-Stack & SaaS Web Developer**\n\n"
        "Haseeb specializes in building high-performance web applications, scalable SaaS systems, and custom AI integrations.\n\n"
        "Here are quick things you can ask me:\n"
        "• *'What are Haseeb's main skills?'*\n"
        "• *'Show me projects Haseeb has built'* \n"
        "• *'What services does Haseeb provide?'*\n"
        "• *'How can I get in touch with Haseeb?'*\n\n"
        "You can also reach Haseeb directly on [WhatsApp (+92 326 8795099)](https://wa.me/923268795099) or [Email](mailto:haseebrehman3460@gmail.com)!"
    )

# ----------------- AI Provider 1: Google Gemini -----------------

def call_gemini_api(user_query: str, history: List[Dict[str, str]] = None) -> str:
    """Call Google Gemini Flash API (Free Tier)."""
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise ValueError("GEMINI_API_KEY not configured")

    contents = []

    # Add conversation history if available (limit last 4 turns)
    if history:
        for item in history[-4:]:
            role = "user" if item.get("role") == "user" else "model"
            text = item.get("content", "").strip()
            if text:
                contents.append({"role": role, "parts": [{"text": text}]})

    # Add current query
    contents.append({
        "role": "user",
        "parts": [{"text": user_query}]
    })

    payload = {
        "systemInstruction": {
            "parts": [{"text": SYSTEM_PROMPT}]
        },
        "contents": contents,
        "generationConfig": {
            "temperature": 0.4,
            "maxOutputTokens": 1024,
            "topP": 0.8
        }
    }

    # Try models in order of performance
    models_to_try = ["gemini-2.5-flash", "gemini-flash-latest", "gemini-2.5-flash-lite"]
    last_err = None

    for model in models_to_try:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode("utf-8"))
                candidates = result.get("candidates", [])
                if candidates and "content" in candidates[0]:
                    parts = candidates[0]["content"].get("parts", [])
                    if parts and "text" in parts[0]:
                        return parts[0]["text"].strip()
        except Exception as e:
            last_err = e
            continue

    raise ValueError(f"Gemini failed across all models: {last_err}")

# ----------------- AI Provider 2: Groq Cloud -----------------

def call_groq_api(user_query: str, history: List[Dict[str, str]] = None) -> str:
    """Call Groq Cloud API (Free Tier)."""
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not api_key:
        raise ValueError("GROQ_API_KEY not configured")

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if history:
        for item in history[-4:]:
            role = item.get("role", "user")
            content = item.get("content", "").strip()
            if content and role in ("user", "assistant"):
                messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": user_query})

    models_to_try = ["openai/gpt-oss-120b", "openai/gpt-oss-20b", "qwen/qwen3.8-27b"]
    last_err = None

    for model in models_to_try:
        try:
            payload = {
                "model": model,
                "messages": messages,
                "temperature": 0.4,
                "max_tokens": 1024
            }

            url = "https://api.groq.com/openai/v1/chat/completions"
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}",
                    "User-Agent": "HaseebPortfolioBot/1.0 (Windows NT 10.0; Win64; x64)"
                },
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode("utf-8"))
                choices = result.get("choices", [])
                if choices and "message" in choices[0]:
                    return choices[0]["message"].get("content", "").strip()
        except Exception as e:
            last_err = e
            continue

    raise ValueError(f"Groq failed across all models: {last_err}")

# ----------------- Main Chatbot Pipeline -----------------

def process_chat(user_query: str, user_id: str, history: List[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    Main entry point for processing incoming chat messages.
    Step 1: Relevance Check (Portfolio Guardrail)
    Step 2: Per-User Rate Limit Check
    Step 3: Try AI Provider #1 (Google Gemini)
    Step 4: Failover to AI Provider #2 (Groq Cloud)
    Step 5: Fallback to Smart Local Knowledge Base (Default Answers)
    
    Guarantees that the visitor ALWAYS receives a complete answer and NEVER sees a raw error.
    """
    load_env()
    user_query = user_query.strip()
    
    if not user_query:
        return {
            "success": True,
            "answer": "Hello! How can I assist you with Haseeb Rehman's portfolio today?",
            "provider": "default"
        }

    # STEP 1: Strict Scope & Relevance Filter
    if not is_relevant_to_portfolio(user_query):
        return {
            "success": True,
            "answer": (
                "I am **Haseeb Rehman's dedicated Portfolio AI Assistant**. I can only assist with questions regarding "
                "Haseeb's background, technical skills, projects, and web development services.\n\n"
                "Here are topics you can ask me about:\n"
                "• **Skills & Stack:** React, Next.js, Node.js, Python, PostgreSQL, AI integrations\n"
                "• **Featured Projects:** Veylohr SaaS, Lizzt app, VendoSphere, Pakhims Healthcare\n"
                "• **Services:** Full-Stack Web Development, SaaS Engineering, Custom APIs\n"
                "• **Hiring & Contact:** Message directly via [WhatsApp (+92 326 8795099)](https://wa.me/923268795099) or [Email](mailto:haseebrehman3460@gmail.com)!\n\n"
                "*(Note: Haseeb specializes strictly in software engineering and web development, and does not offer graphic design, digital marketing, or non-technical services).*"
            ),
            "provider": "guardrail",
            "is_off_topic": True
        }

    # STEP 2: Per-User Rate Limit Check
    is_allowed, current_count, limit = check_user_rate_limit(user_id)
    if not is_allowed:
        # User reached their daily query limit!
        # Do NOT show an error. Provide the complete answer from local knowledge base with a friendly notice.
        answer = get_default_answer(user_query)
        quota_notice = (
            f"\n\n*(Note: You've reached your free AI query allowance ({limit}/{limit}) for this session. "
            f"You can continue browsing with instant answers or connect with Haseeb directly on "
            f"[WhatsApp](https://wa.me/923268795099) or [Email](mailto:haseebrehman3460@gmail.com)!)*"
        )
        return {
            "success": True,
            "answer": answer + quota_notice,
            "provider": "local-quota-exceeded",
            "user_quota_reached": True
        }

    # STEP 3: Attempt AI Provider #1 (Google Gemini)
    gemini_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if gemini_key:
        try:
            answer = call_gemini_api(user_query, history)
            if answer:
                record_user_usage(user_id)
                return {
                    "success": True,
                    "answer": answer,
                    "provider": "gemini"
                }
        except Exception as e:
            # Gemini failed or rate-limited; proceed seamlessly to Provider #2
            pass

    # STEP 4: Attempt AI Provider #2 (Groq Cloud LLM)
    groq_key = os.environ.get("GROQ_API_KEY", "").strip()
    if groq_key:
        try:
            answer = call_groq_api(user_query, history)
            if answer:
                record_user_usage(user_id)
                return {
                    "success": True,
                    "answer": answer,
                    "provider": "groq"
                }
        except Exception as e:
            # Groq failed or rate-limited; proceed seamlessly to Local Default Answers
            pass

    # STEP 5: Fallback to Smart Local Knowledge Base
    # Both AIs exhausted / failed / no keys configured.
    # Return instantaneous high-quality default answers without any disruption!
    answer = get_default_answer(user_query)
    return {
        "success": True,
        "answer": answer,
        "provider": "local-default"
    }

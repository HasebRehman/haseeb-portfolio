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
        "cv_download": "/public/Haseeb_Rehman_CV.pdf"
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

STRICT INSTRUCTIONS & RESPONSE RULES (EXTREME CONCISENESS):
1. ALWAYS answer directly and strictly to the point. Give ONLY what was asked — no extra background, no life stories, no generic filler.
2. MAXIMUM LENGTH: 1 to 2 short sentences. If listing items, provide maximum 2-3 brief bullets.
3. GREETINGS (e.g. "hi", "hello", "hey"):
   - Respond ONLY with a friendly one-liner: "Hey! How can I help you with Haseeb's work or services?"
   - NEVER introduce yourself with a long robotic self-intro.
4. SPECIFIC QUESTIONS:
   - "who is he / about him" -> "Haseeb Rehman is a Senior Full-Stack & SaaS Web Developer with 3+ years experience and 50+ delivered projects."
   - "skills / tech stack" -> "Core stack: React, Next.js, TypeScript, Node.js, Python, PostgreSQL, and AI integrations."
   - "contact / hire" -> "You can reach Haseeb on WhatsApp at +92 326 8795099 or email at haseebrehman3460@gmail.com."
   - "projects" -> "Notable projects include Veylohr (HR SaaS), Lizzt (task app), and VendoSphere (e-commerce)."
   - "services" -> "Haseeb builds full-stack web applications, SaaS platforms, and custom AI chatbots."
5. Unrelated questions: Respond ONLY with: "I can only answer questions related to Haseeb's portfolio and development work."
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
            "Haseeb focuses exclusively on **Full-Stack Web Development, SaaS Applications, and AI Integrations**. He does not provide graphic design or marketing services."
        )

    # 1. Contact & Hire & WhatsApp & Email
    if re.search(r"\b(contact|hire|email|whatsapp|phone|reach|call|touch|quote|rate|price|pricing|freelance)\b", q):
        return (
            "You can connect with Haseeb directly via:\n\n"
            "• **WhatsApp:** [+92 326 8795099](https://wa.me/923268795099)\n"
            "• **Email:** [haseebrehman3460@gmail.com](mailto:haseebrehman3460@gmail.com)\n"
            "• **LinkedIn:** [linkedin.com/in/haseebrehmanweb](https://www.linkedin.com/in/haseebrehmanweb/)"
        )

    # 2. CV / Resume
    if re.search(r"\b(cv|resume)\b", q):
        return (
            "You can download Haseeb's CV here: [Download CV](/public/Haseeb_Rehman_CV.pdf)."
        )

    # 3. Projects & Work
    if re.search(r"\b(project|projects|work|showcase|built|apps|websites|veylohr|lizzt|pakhims|vendosphere|dental|opa)\b", q):
        return (
            "Key projects built by Haseeb:\n\n"
            "• **[Veylohr](https://veylohr.com/)** — HR management SaaS\n"
            "• **[Lizzt](https://lizzt.app/)** — Collaborative event and task app\n"
            "• **[VendoSphere](https://ecommerce-one-tau-62.vercel.app/)** — Modern e-commerce platform\n"
            "• **[Pakhims](https://pakhims.com/)** — Healthcare brand portal\n\n"
            "Explore more on the [Projects Page](/projects)."
        )

    # 4. Skills & Tech Stack
    if re.search(r"\b(skill|skills|tech|stack|technologies|react|next|node|typescript|python|backend|frontend|languages|tools|database|mongo|postgres)\b", q):
        return (
            "Haseeb's core tech stack:\n\n"
            "• **Frontend:** React, Next.js, TypeScript, Tailwind CSS, GSAP\n"
            "• **Backend:** Node.js, Express, NestJS, Python, REST APIs\n"
            "• **Databases & Cloud:** PostgreSQL, MongoDB, Supabase, Redis, Docker"
        )

    # 5. Services
    if re.search(r"\b(service|services|offer|what\s+do\s+you\s+do|capabilities|what\s+can\s+you\s+build)\b", q):
        return (
            "Haseeb offers:\n\n"
            "• **Full-Stack Web Development** (React, Next.js, Node.js)\n"
            "• **SaaS Product Engineering** (Multi-tenant architecture, billing)\n"
            "• **AI Chatbots & Integrations** (Gemini, OpenAI, automation)\n"
            "• **API Development & Speed Optimization**"
        )

    # 6. About & Education & Experience
    if re.search(r"\b(about|bio|education|degree|numl|cgpa|digitsio|experience|who\s+is\s+haseeb|years)\b", q):
        return (
            "Haseeb Rehman is a **Senior Full-Stack & SaaS Developer** with 3+ years of experience and 50+ delivered projects. He holds a BS in Computer Science from NUML (CGPA 3.63) and is currently at Digitsio."
        )

    # 7. Pure Greetings
    if re.search(r"\b(hi|hello|hey|greetings|aoa|assalam)\b", q):
        return (
            "Hi there! 👋 How can I help you regarding Haseeb's work or services today?"
        )

    # Default general portfolio answer
    return (
        "Haseeb Rehman is a Senior Full-Stack & SaaS Developer. Feel free to ask about his **skills**, **projects**, or **services**, or reach him on [WhatsApp (+92 326 8795099)](https://wa.me/923268795099)."
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
            "maxOutputTokens": 450,
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
                "max_tokens": 450
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

    # FAST SHORTCUT: Simple Greetings ("hi", "hello", etc.)
    clean_q = user_query.strip().lower()
    if clean_q in ("hi", "hello", "hey", "hola", "aoa", "assalam o alaikum", "assalamualaikum", "hi there", "hey there", "good morning", "good evening"):
        return {
            "success": True,
            "answer": "Hey! 👋 How can I help you today?",
            "provider": "instant-greet"
        }

    # STEP 1: Strict Scope & Relevance Filter
    if not is_relevant_to_portfolio(user_query):
        return {
            "success": True,
            "answer": "I can only assist with questions about Haseeb Rehman's portfolio, web/SaaS projects, technical skills, and development services.",
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

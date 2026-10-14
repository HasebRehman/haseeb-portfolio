# Haseeb Portfolio

A modern, high-performance personal portfolio website built with rich interactive animations, GSAP SplitText typography effects, smooth scrolling, custom magic cursor, and responsive dark-theme design.

## 🚀 Features

- **Hero & Bio**: Interactive typography reveal animations (`text-anime-style-3`), rotating experience badge, CTA buttons, and video popup.
- **About Me**: Detailed experience counters, skills progress indicators, and client satisfaction metrics.
- **Services Grid**: 6-item glowing gradient-bordered service cards (`UI/UX`, `Frontend`, `Backend`, `Performance`, etc.).
- **Our Projects**: Full project showcase grid with hover zoom and custom `View` cursor interaction.
- **Testimonials & FAQs**: Responsive Swiper carousel and smooth collapsible accordion.
- **Dual Infinite Marquee Tickers**: Smooth continuous bi-directional marquee ribbons.
- **Contact Us**: Responsive contact form with validation states and Google Maps embed.
- **Custom 404 Error Page**: Dedicated 404 artwork and automated server routing fallback.

- **Dual-AI Portfolio Chatbot**: Floating bottom-right chatbot matching the dark neon orange theme with automatic failover (Gemini & Groq), per-user quota management, scope guardrails (portfolio-only), and a smart local knowledge base that guarantees zero error screens for visitors.

## 🛠️ Tech Stack

- **HTML5 / CSS3 / JavaScript (ES6+)**
- **Bootstrap 5 & Custom CSS**
- **GSAP (GreenSock) + SplitText + ScrollTrigger**
- **Swiper.js (Touch-enabled carousels)**
- **WOW.js & Animate.css**
- **Waypoints & CounterUp**
- **Magic Cursor (Spring-physics trailing cursor)**
- **Dual Free AI Engine**: Google Gemini Flash API + Groq Cloud (LLaMA 3.3) with instant failover

## 🤖 AI Chatbot Setup (100% Free)

The chatbot automatically runs out of the box using the built-in local portfolio knowledge base. To activate full generative AI responses:

1. **Google Gemini (Provider 1 - Free)**:
   - Generate your free key at [Google AI Studio](https://aistudio.google.com/app/apikey).
   - Add to `.env`: `GEMINI_API_KEY=your_gemini_key`

2. **Groq Cloud (Provider 2 - Free Failover)**:
   - Generate your free key at [Groq Console](https://console.groq.com/keys).
   - Add to `.env`: `GROQ_API_KEY=your_groq_key`

3. **Per-User Quota & Scope Guardrail**:
   - `USER_QUERY_LIMIT=10` (protects your daily quota from individual users).
   - Automatically rejects off-topic queries before making AI calls to conserve tokens.
   - If both AIs reach their free quota, questions are seamlessly answered using Haseeb's local portfolio knowledge base with zero error messages shown to users.

## 💻 Local Development

To run the local server with custom routing and API handlers:

```bash
python server.py
```

Then visit [http://localhost:3000](http://localhost:3000) in your browser.

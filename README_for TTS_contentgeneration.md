# TCC Content Workflow — Gemini Pipeline

## Project Overview

This is the **second half** of the TCC (The Crazy Careers) content automation system. The first half — trend collection and email delivery — is already built. This README covers everything you need to build the **"Generate Content" pipeline**: the part that runs after the user clicks the button.

```
┌─────────────────────────────────────────────────────────────────┐
│                     FULL SYSTEM OVERVIEW                        │
├──────────────────────────┬──────────────────────────────────────┤
│   PART 1 (DONE ✅)       │   PART 2 (TO BUILD 🔧)              │
│                          │                                       │
│  Trend Collector         │  Generate Content Pipeline           │
│  → Filter by niche       │  → Step 1: Keyword Research          │
│  → Send email with       │  → Step 2: SERP Analysis             │
│    "Generate Content"    │  → Step 3: Content Outline           │
│    button per topic      │  → Step 4: Full Article + FAQ        │
│                          │  → Step 5: HTML for Elementor        │
└──────────────────────────┴──────────────────────────────────────┘
```

---

## What You're Building (Part 2)

When the user clicks **"Generate Content"** in the email:

1. A webhook/endpoint receives the selected topic
2. Five Gemini API calls run in sequence (each output feeds into the next)
3. The final HTML is emailed back to the user, ready to paste into Elementor

---

## Tech Stack

| Layer | Tool | Notes |
|---|---|---|
| AI Model (Steps 1–3, 5) | `gemini-2.0-flash` | Fast + cheap |
| AI Model (Step 4) | `gemini-1.5-pro` | Better long-form writing |
| Keyword + SERP Data | SEMrush API | Required for Steps 1 & 2 |
| Orchestration | Your choice — see options below | Python script / n8n / Make.com |
| Trigger | HTTP webhook (button click from email) | Must match your Part 1 setup |
| Output delivery | Email (same tool as Part 1) | Sends final HTML back to user |

---

## Repository Structure (Suggested)

```
tcc-content-pipeline/
├── README.md                  ← this file
├── .env                       ← API keys (never commit)
├── .env.example               ← template for env vars
│
├── config/
│   └── persona.py             ← Master Persona Prompt (shared across all steps)
│
├── prompts/
│   ├── step1_keywords.py      ← Keyword Research prompt
│   ├── step2_serp.py          ← SERP & Competitor Analysis prompt
│   ├── step3_outline.py       ← Content Outline prompt
│   ├── step4_article.py       ← Full Article + FAQ + Schema prompt
│   └── step5_html.py          ← HTML for Elementor prompt
│
├── pipeline/
│   ├── runner.py              ← Main orchestrator — chains all 5 steps
│   ├── gemini_client.py       ← Gemini API wrapper
│   └── semrush_client.py      ← SEMrush API wrapper (Steps 1 & 2)
│
├── webhook/
│   └── handler.py             ← Receives the button click, kicks off pipeline
│
└── output/
    └── (generated HTML files land here)
```

---

## Environment Variables

Create a `.env` file at the root. Never commit this file.

```env
# Gemini
GEMINI_API_KEY=your_gemini_api_key_here

# SEMrush
SEMRUSH_API_KEY=your_semrush_api_key_here

# Email delivery (match whatever you used in Part 1)
EMAIL_FROM=noreply@thecrazycareers.com
EMAIL_TO=aman@thecrazycareers.com
SMTP_HOST=smtp.yourprovider.com
SMTP_PORT=587
SMTP_USER=your_smtp_user
SMTP_PASS=your_smtp_password

# Webhook
WEBHOOK_SECRET=a_random_secret_string   # validate incoming requests
PORT=8000
```

`.env.example` (commit this):

```env
GEMINI_API_KEY=
SEMRUSH_API_KEY=
EMAIL_FROM=
EMAIL_TO=
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASS=
WEBHOOK_SECRET=
PORT=8000
```

---

## Gemini API — Key Concepts

### Installation

```bash
pip install google-generativeai
```

### Base client (`pipeline/gemini_client.py`)

```python
import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def call_gemini(prompt: str, model: str = "gemini-2.0-flash", temperature: float = 0.4, max_tokens: int = 4096) -> str:
    from config.persona import MASTER_PERSONA

    m = genai.GenerativeModel(
        model_name=model,
        system_instruction=MASTER_PERSONA
    )
    response = m.generate_content(
        contents=prompt,
        generation_config=genai.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
    )
    return response.text
```

### Model selection per step

| Step | Model | Temperature | Max Tokens |
|---|---|---|---|
| Step 1 — Keywords | `gemini-2.0-flash` | 0.3 | 2048 |
| Step 2 — SERP | `gemini-2.0-flash` | 0.3 | 3000 |
| Step 3 — Outline | `gemini-2.0-flash` | 0.4 | 2048 |
| Step 4 — Article | `gemini-1.5-pro` | 0.6 | 8192 |
| Step 5 — HTML | `gemini-2.0-flash` | 0.2 | 8192 |

---

## Master Persona Prompt (`config/persona.py`)

This is injected as `system_instruction` into **every** Gemini call. Keep it in one place so updates propagate automatically.

```python
MASTER_PERSONA = """
You are an SEO Content Strategist with 10+ years of experience in
SEO, Content Marketing, Content Writing, and Microblogging.
You work exclusively for The Crazy Careers (thecrazycareers.com)
— a career guidance platform for Indian students and early professionals.

BRAND RULES:
- Niche: Career guidance, education, study abroad, startups, future skills
- Audience: Indian students (Class 10 to early career, 15-27 years)
- Tone: Expert but approachable, career-guidance counsellor voice
- Never cover: cricket, films, celebrities, generic viral topics
- Always apply: The Crazy Careers editorial angle to every topic

SEO RULES:
- Target evergreen URLs (no year in slug unless unavoidable)
- Long-form pillar pages: 1,800-2,500 words
- Trend/news pieces: 800-1,000 words
- Every article needs: real author byline, schema markup, FAQ section
- Competitor tier to beat: Shiksha, Careers360, Collegedunia
- Keyword tool: SEMrush (connected)

CONTENT MODEL:
- Portals give data. We give decisions.
- Our angle: 'What does this mean for your career/education?'
- Do NOT chase transactional keywords owned by government portals
- Chase decision-stage, informational, and career-angle keywords
"""
```

---

## The 5 Step Prompts

Each prompt is a Python string. Replace `[PREVIOUS_OUTPUT]` with the actual output from the prior step.

### Step 1 — Keyword Research (`prompts/step1_keywords.py`)

```python
def build_step1_prompt(topic: str) -> str:
    return f"""
STEP 1: KEYWORD RESEARCH

Topic received: {topic}
Country: India

Using SEMrush Keyword Magic Tool (phrase_fullsearch), pull the top 20
keywords for this topic in the India database.

Sort results into three buckets:

BUCKET A — NAVIGATIONAL / TRANSACTIONAL (do not target as primary)
List keywords + volumes. Note: government portals own these.

BUCKET B — YEAR-STAMPED (mention in article body, not in the slug)
List keywords. Our evergreen URL strategy makes these slug-irrelevant.

BUCKET C — OWNABLE GOLD (decision-stage, informational, durable)
List keywords + volumes + KD score.
These become our primary and secondary keyword targets.

Final output:
- Recommended primary keyword (1)
- Recommended secondary keywords (3-5)
- Question-format keywords flagged for the FAQ section

Respond in structured plain text with clear section headers.
"""
```

### Step 2 — SERP & Competitor Analysis (`prompts/step2_serp.py`)

```python
def build_step2_prompt(step1_output: str) -> str:
    return f"""
STEP 2: SERP & COMPETITOR ANALYSIS

[Step 1 output]:
{step1_output}

Country: India

Using SEMrush organic research, pull live SERP data for the primary
and secondary keywords identified above.

TIER 1 — Government portals / giants (cannot outrank — do not try)
List URLs + reason they hold these positions.

TIER 2 — Coaching / edtech brands (mid authority — study their depth)
List URLs.

TIER 3 — Smaller content sites (our peer tier — most beatable)
List URLs + one-line note on what makes them beatable.

SERP GAPS TO FLAG:
- Reddit or Quora ranking? (signals unmet demand)
- Weak domain holding a position? (signals low competition)
- A tool or predictor ranking? (signals we should build one)
- Video content ranking? (signals YouTube embed value)

COMPETITIVE VERDICT:
- Can TCC realistically rank page 1 within 6 months?
- Which Tier 3 URL should we model our structure on?
- What does the strongest competitor do that we must match?
- What does the strongest competitor fail to do? (our wedge)
"""
```

### Step 3 — Content Outline (`prompts/step3_outline.py`)

```python
def build_step3_prompt(step1_output: str, step2_output: str) -> str:
    return f"""
STEP 3: BUILD CONTENT OUTLINE

[Step 1 — Keywords]:
{step1_output}

[Step 2 — SERP Analysis]:
{step2_output}

Content type: determine from topic (evergreen hub / trend piece / live blog)
Target word count: 1,800-2,500 words (hub) / 800-1,000 words (trend/news)

META:
- H1 title (primary keyword included naturally)
- URL slug (evergreen, no year)
- Meta title (60 characters max, include primary keyword)
- Meta description (155 characters max, keyword + clear value prop)
- Search intent: informational / decision / navigational

SECTIONS — for each H2 provide:
- Heading text (target keyword noted in brackets where applicable)
- 2-3 sentence description of what this section covers and why
- Word count target for this section
- Special element if needed: table / checklist / comparison / FAQ / tool embed

DIFFERENTIATION NOTES:
- Which sections beat Shiksha/Careers360 on depth
- Where to add the 'what does this mean for YOUR career' layer

TECHNICAL NOTES:
- Schema type: Article / NewsArticle / FAQPage / HowTo
- Internal link suggestions (anchor text + destination page)
"""
```

### Step 4 — Full Article + FAQ + Schema (`prompts/step4_article.py`)

```python
def build_step4_prompt(step3_output: str) -> str:
    return f"""
STEP 4: WRITE ARTICLE + FAQ + SCHEMA

[Content Outline from Step 3]:
{step3_output}

— PART A: FULL ARTICLE —

WRITING RULES:
- Voice: expert career counsellor, not a news reporter
- Short to medium sentences — max 2 clauses per sentence
- No passive voice. Active only.
- No filler phrases: 'In today's world', 'It goes without saying'
- Every H2 section must answer a real student question
- Use 'you' to address the reader directly throughout

SEO RULES:
- Primary keyword in: H1, first 100 words, one H2, meta description
- Secondary keywords distributed naturally — no keyword stuffing
- Internal links: mark as [INTERNAL LINK: suggested anchor text]

EVERGREEN RULES:
- No hard-coded years in the body text
- Use: 'the current cycle', 'this year's schedule', 'typically'
- Mark update points: [UPDATE EACH YEAR: replace with current data]

— PART B: FAQ SECTION —
- Generate 8-10 question-format keywords for the FAQ
- Each answer: 2-4 sentences, plain language, featured-snippet ready
- Start every answer with a direct response (not 'Great question!')

— PART C: JSON-LD SCHEMA —
- FAQPage schema for all FAQ questions
- Article or NewsArticle schema with placeholders:
  headline, author, publisher: The Crazy Careers,
  datePublished: [YYYY-MM-DD], dateModified: [YYYY-MM-DD]

Output: clean markdown article + FAQ + schema in one complete block.
"""
```

### Step 5 — HTML for Elementor (`prompts/step5_html.py`)

```python
def build_step5_prompt(step4_output: str) -> str:
    return f"""
STEP 5: GENERATE HTML FOR ELEMENTOR

[Article + FAQ + Schema from Step 4]:
{step4_output}

Convert the article to styled HTML for thecrazycareers.com.

DESIGN SYSTEM:
Primary blue:  #046bd2     Dark blue:  #045cb4
Light bg:      #F0F5FA     Body text:  #334155
Heading:       #1e293b     Accent:     #f542b0
Font: Inter (Google Fonts)

REQUIRED ELEMENTS:
1. Featured image banner (CSS gradient 16:9 if no real image)
2. Meta bar — category badge + author chip + estimated read time
3. Article H1 title
4. Lead paragraph with left blue border accent
5. Table of Contents (2-column grid)
6. Key stats strip (4 metric cards) if article has statistics
7. Styled H2/H3 headings with bottom border
8. Info boxes: tip (green) / warning (yellow) / info (blue)
9. Tables converted to styled comparison cards or glossary grid
10. Step lists as numbered circle badge steps
11. FAQ section as accordion-style items
12. Related links box at end of article
13. Disclaimer box at end of article

DO NOT include: site header, navbar, footer, sidebar, WP shortcodes

OUTPUT: Output ONLY the raw HTML. No explanation, no markdown fences.
All CSS must be embedded inline in a <style> tag at the top.
This will be pasted directly into: Elementor > Widget > Custom HTML
"""
```

---

## Pipeline Orchestrator (`pipeline/runner.py`)

This is the core file — it chains all 5 steps and returns the final HTML.

```python
from pipeline.gemini_client import call_gemini
from prompts.step1_keywords import build_step1_prompt
from prompts.step2_serp import build_step2_prompt
from prompts.step3_outline import build_step3_prompt
from prompts.step4_article import build_step4_prompt
from prompts.step5_html import build_step5_prompt

def run_pipeline(topic: str) -> dict:
    """
    Runs all 5 Gemini steps for a given topic.
    Returns a dict with each step's output and the final HTML.
    """
    print(f"[Pipeline] Starting for topic: {topic}")

    # Step 1
    print("[Step 1] Keyword Research...")
    step1 = call_gemini(
        prompt=build_step1_prompt(topic),
        model="gemini-2.0-flash",
        temperature=0.3,
        max_tokens=2048
    )

    # Step 2
    print("[Step 2] SERP Analysis...")
    step2 = call_gemini(
        prompt=build_step2_prompt(step1),
        model="gemini-2.0-flash",
        temperature=0.3,
        max_tokens=3000
    )

    # Step 3
    print("[Step 3] Content Outline...")
    step3 = call_gemini(
        prompt=build_step3_prompt(step1, step2),
        model="gemini-2.0-flash",
        temperature=0.4,
        max_tokens=2048
    )

    # Step 4 — switch to Pro for article quality
    print("[Step 4] Writing Article + FAQ + Schema...")
    step4 = call_gemini(
        prompt=build_step4_prompt(step3),
        model="gemini-1.5-pro",
        temperature=0.6,
        max_tokens=8192
    )

    # Step 5
    print("[Step 5] Generating HTML...")
    step5 = call_gemini(
        prompt=build_step5_prompt(step4),
        model="gemini-2.0-flash",
        temperature=0.2,
        max_tokens=8192
    )

    print("[Pipeline] Complete.")

    return {
        "topic": topic,
        "step1_keywords": step1,
        "step2_serp": step2,
        "step3_outline": step3,
        "step4_article": step4,
        "step5_html": step5,       # ← this is what gets emailed
    }
```

---

## Webhook Handler (`webhook/handler.py`)

This receives the button click from the email. Adapt to whichever web framework you're using (Flask shown below).

```python
from flask import Flask, request, jsonify
import hmac, hashlib, os, threading
from pipeline.runner import run_pipeline
from utils.emailer import send_html_email

app = Flask(__name__)

def validate_signature(payload: bytes, signature: str) -> bool:
    """Optional: validate the request came from your Part 1 system."""
    secret = os.getenv("WEBHOOK_SECRET", "").encode()
    expected = hmac.new(secret, payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)

@app.route("/generate", methods=["POST"])
def generate():
    topic = request.json.get("topic")
    if not topic:
        return jsonify({"error": "topic is required"}), 400

    # Run pipeline in background so webhook returns immediately
    def run_and_email():
        result = run_pipeline(topic)
        send_html_email(
            subject=f"[TCC] Content Ready: {topic}",
            html_body=result["step5_html"],
            attachments={
                "article_draft.md": result["step4_article"],
                "keywords.txt": result["step1_keywords"],
            }
        )

    thread = threading.Thread(target=run_and_email)
    thread.start()

    return jsonify({"status": "pipeline started", "topic": topic}), 202

if __name__ == "__main__":
    app.run(port=int(os.getenv("PORT", 8000)))
```

> **Note:** The webhook returns `202 Accepted` immediately and runs the pipeline in a background thread. This prevents email client timeouts (most HTTP clients timeout after 30s; the pipeline takes ~5 min).

---

## Email Delivery (`utils/emailer.py`)

Sends the final HTML back to you. Adapt `SMTP_*` vars to match your Part 1 email provider.

```python
import smtplib, os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def send_html_email(subject: str, html_body: str, attachments: dict = {}):
    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"] = os.getenv("EMAIL_FROM")
    msg["To"] = os.getenv("EMAIL_TO")

    # HTML body (the Elementor-ready article)
    msg.attach(MIMEText(html_body, "html"))

    # Optional attachments (markdown draft, keywords)
    for filename, content in attachments.items():
        part = MIMEBase("application", "octet-stream")
        part.set_payload(content.encode("utf-8"))
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f'attachment; filename="{filename}"')
        msg.attach(part)

    with smtplib.SMTP(os.getenv("SMTP_HOST"), int(os.getenv("SMTP_PORT", 587))) as server:
        server.starttls()
        server.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASS"))
        server.send_message(msg)
```

---

## Connecting Part 1 → Part 2

The "Generate Content" button in your Part 1 email needs to hit your Part 2 webhook. Here's how to generate that button link in your existing email sender:

```python
# In your Part 1 email builder — add this per topic

import urllib.parse

WEBHOOK_URL = "https://your-server.com/generate"  # your Part 2 endpoint

def make_generate_button(topic: str) -> str:
    """Returns an HTML button that POSTs to the pipeline webhook."""
    encoded_topic = urllib.parse.quote(topic)
    # Use a GET endpoint with topic in query string for email button compatibility
    # (HTML emails can't POST — use a redirect page or GET endpoint)
    return f'<a href="{WEBHOOK_URL}?topic={encoded_topic}" style="...">Generate Content</a>'
```

> **Important:** Email clients can't trigger POST requests. Your button should link to a simple GET endpoint (`/generate?topic=...`) that internally POSTs to the pipeline. Or host a one-click confirmation page in between.

---

## Running Locally

```bash
# 1. Clone / navigate to project
cd tcc-content-pipeline

# 2. Install dependencies
pip install google-generativeai flask python-dotenv

# 3. Copy and fill env file
cp .env.example .env
# → fill in your GEMINI_API_KEY, SEMRUSH_API_KEY, SMTP_* values

# 4. Test the pipeline directly (no webhook)
python -c "
from pipeline.runner import run_pipeline
result = run_pipeline('JoSAA counselling guide')
with open('output/test_output.html', 'w') as f:
    f.write(result['step5_html'])
print('Done — open output/test_output.html')
"

# 5. Start the webhook server
python webhook/handler.py
# → listening on http://localhost:8000

# 6. Test the webhook
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"topic": "JoSAA counselling guide"}'
```

---

## Deployment Options

| Option | Cost | Best for |
|---|---|---|
| **Railway / Render (free tier)** | Free (with sleep) | Testing, low volume |
| **Hetzner CX11 VPS** | ~€4/mo | Always-on production |
| **Google Cloud Run** | Pay per request | Sporadic / bursty use |
| **n8n self-hosted** | ~$5/mo VPS | No-code orchestration alternative |

For always-on webhook availability, a small VPS (Hetzner, DigitalOcean) is the most straightforward option.

---

## Error Handling Checklist

When building `runner.py`, handle these failure modes:

- [ ] **Gemini rate limit** (`429`) — add exponential backoff retry on each step
- [ ] **Empty response** — check `response.text` is not None/empty before passing to next step
- [ ] **Step 4 truncation** — if article is cut off, retry with `max_tokens=16384` (gemini-1.5-pro supports it)
- [ ] **SEMrush API failure** — degrade gracefully: tell Gemini to use its own knowledge if SEMrush data is unavailable
- [ ] **Webhook timeout** — always run pipeline in background thread (already shown above)
- [ ] **Email delivery failure** — log the HTML to `output/` as a fallback so content isn't lost

---

## What's Already Done (Part 1 Integration Points)

Since Part 1 is complete, note which pieces must stay in sync:

| Part 1 output | Part 2 expects |
|---|---|
| Topic string sent in email | Same string passed as `topic` to `run_pipeline()` |
| Email provider / SMTP config | Same `SMTP_*` env vars reused in `utils/emailer.py` |
| "Generate Content" button URL | Must point to your Part 2 `/generate` endpoint |
| Auth / secret | `WEBHOOK_SECRET` must match between both systems |

---

## Dependencies

```
google-generativeai>=0.8.0
flask>=3.0.0
python-dotenv>=1.0.0
```

Optional (if you add SEMrush API calls directly in Python):
```
requests>=2.32.0
```

---

*TCC Content Workflow — Part 2 README*
*The Crazy Careers · thecrazycareers.com*

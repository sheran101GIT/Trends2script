"""Step 4 — Full Article + FAQ + Schema prompt"""
import re

def build_step4_prompt(step3_output: str, meta: dict = None, news_context: str = "") -> str:
    meta = meta or {}
    read_time_str = meta.get("read_time", "5")
    
    # Extract minutes to estimate word count (approx 200 words per minute)
    match = re.search(r'(\d+)', read_time_str)
    minutes = int(match.group(1)) if match else 5
    target_words = minutes * 200

    return f"""
STEP 4: WRITE ARTICLE + FAQ + SCHEMA

[Content Outline from Step 3]:
{step3_output}

[RECENT NEWS & SOURCES]:
{news_context}

— PART A: FULL ARTICLE —

═══════════════════════════════════════
TCC VOICE & TONE GUIDE (FOLLOW EXACTLY)
═══════════════════════════════════════

BRAND VOICE MODEL — Study this example from The Crazy Careers and write in this exact voice:

  Opening Hook (observe → reflect): "As an educator and entrepreneur, there are certain conversations that stay with you long after they end. They challenge your assumptions, reshape your understanding of young people, and leave you feeling genuinely optimistic about the future."

  Narrative Transition: "When two Class 12 students sat across from me recently, I expected to talk about board exams, college admissions, or career anxiety. What I got instead was something far more inspiring."

  Callout Quote style: "They didn't come asking for a job. They came with a proposal that would benefit both of us."

  Observation + Insight: "Their focus was not on immediate monetary gain. Instead, they were thinking about exposure, networking, community building, and long-term growth. This was not youthful naivety — it was a deliberately entrepreneurial way of thinking."

  Data Anchor: "What I witnessed is not an isolated example. It reflects a broader, well-documented trend across India and around the world."

  Empowering Closer: "What appears to be impatience may actually be initiative. What appears to be unconventional thinking may actually be innovation."

TONE RULES (non-negotiable):
- Voice: An expert educator and career counsellor who also operates in the real world (entrepreneur, professional). This is NOT a neutral journalist. Write with personal conviction, warmth, and insight.
- Open with a STORY or OBSERVATION that happened in the real world. Do not open with a statistic or a generic statement. The first paragraph must hook the reader with a moment or a thought that feels human.
- Transition from the personal observation to the broader trend/topic naturally (e.g., "What I witnessed is not an isolated example...").
- Use 'you' to address the reader directly throughout the body. Make the reader feel seen and spoken to.
- Every H2 section must answer a real reader question OR unpack a specific insight about the topic.
- Include 1-2 pull-quote moments per article: short, punchy, standalone sentences in quotes that capture a key insight (these will be styled as blockquotes in HTML).
- Include 2-3 emoji-led callout boxes that highlight a key concept, model, or shift. Format them like: "🎯 The [Concept Name]: [1-2 sentence explanation]"
- Short to medium sentences — max 2 clauses per sentence.
- No passive voice. Active only.
- No filler phrases: 'In today's world', 'It goes without saying', 'In conclusion'.
- End with a 'Final Thoughts' section that is empowering, reflective, and optimistic — do not end with a generic summary.

TARGET LENGTH: Write approximately {target_words} words to match the user's '{read_time_str}' read time requirement. Ensure the content is deep and substantial — no padding or fluff.

RELIABILITY & CITATIONS:
- You MUST weave the provided [RECENT NEWS & SOURCES] into the article. For every news event, fact, or statistic you mention from the news sources, you MUST add its citation immediately after it using the exact URL in this format: [LINK: URL]. Do not truncate or modify the URL. Do not invent any URLs.
  Example: "...according to recent reports, over 30.66 lakh applicants registered for the exam [LINK: https://news.google.com/rss/articles/example-url]."
- CURRENT AFFAIRS FOCUS: Integrate the recent news context naturally into the flow of the article. Discuss its significance and implications for career/student decisions. The reader should feel they are reading a timely, up-to-date analysis written by someone who deeply understands both the world and young India.

SEO RULES:
- Primary keyword in: H1, first 100 words, one H2, meta description.
- Secondary keywords distributed naturally — no keyword stuffing.
- Internal links: mark as [INTERNAL LINK: suggested anchor text].

EVERGREEN RULES:
- No hard-coded years in the body text (unless referring to a specific historical event or the specific recent news event/announcement being reported, e.g. 'the 2026 budget announcement', 'the July 2026 exam schedule').
- Use: 'the current cycle', 'this year's schedule', 'typically'.
- Mark update points: [UPDATE EACH YEAR: replace with current data].

— PART B: FAQ SECTION —
- Generate 8-10 question-format keywords for the FAQ.
- Each answer: 2-4 sentences, plain language, featured-snippet ready.
- Start every answer with a direct response (not 'Great question!').

— PART C: JSON-LD SCHEMA —
- FAQPage schema for all FAQ questions.
- Article or NewsArticle schema with placeholders:
  headline, author, publisher: The Crazy Careers,
  datePublished: [YYYY-MM-DD], dateModified: [YYYY-MM-DD]

Output: clean markdown article + FAQ + schema in one complete block.
"""

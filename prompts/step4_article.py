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

WRITING RULES:
- Voice: Professional journalist / reporter for a premium blogging site. Report facts objectively, provide reliable information.
- Target Length: Write approximately {target_words} words to match the user's '{read_time_str}' read time requirement. Ensure the content is deep and substantial enough to hit this target without fluff.
- Short to medium sentences — max 2 clauses per sentence.
- No passive voice. Active only.
- No filler phrases: 'In today's world', 'It goes without saying'.
- Every H2 section must answer a real reader question or cover a core aspect of the topic.
- Use 'you' to address the reader directly throughout.
- RELIABILITY: You MUST weave the provided [RECENT NEWS & SOURCES] into the article. When mentioning a news item, cite the exact URL provided using the format: [LINK: url]. Do not invent URLs.

SEO RULES:
- Primary keyword in: H1, first 100 words, one H2, meta description.
- Secondary keywords distributed naturally — no keyword stuffing.
- Internal links: mark as [INTERNAL LINK: suggested anchor text].

EVERGREEN RULES:
- No hard-coded years in the body text (unless referring to a specific historical event).
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

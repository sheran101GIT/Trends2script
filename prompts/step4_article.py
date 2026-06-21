"""Step 4 — Full Article + FAQ + Schema prompt"""


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

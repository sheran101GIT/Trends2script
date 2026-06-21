"""Step 3 — Content Outline prompt"""


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

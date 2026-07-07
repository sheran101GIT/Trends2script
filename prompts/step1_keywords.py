"""Step 1 — Keyword Research prompt"""


def build_step1_prompt(topic: str, news_context: str = "") -> str:
    return f"""
STEP 1: KEYWORD RESEARCH

Topic received: {topic}
Country: India

[RECENT NEWS & SOURCES]:
{news_context}

Using SEMrush Keyword Magic Tool (phrase_fullsearch), pull the top 20
keywords for this topic in the India database. Make sure to prioritize keywords, user queries, and search intents that directly align with or are triggered by the current affairs and news developments listed above in [RECENT NEWS & SOURCES].

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


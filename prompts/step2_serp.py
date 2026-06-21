"""Step 2 — SERP & Competitor Analysis prompt"""


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

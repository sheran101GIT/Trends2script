"""Step 5a — Extract structured JSON from the Step 4 article.

This is Phase 1 of the new two-phase Step 5.
A cheap, small LLM (8b) reads the article and outputs a compact JSON object.
Phase 2 (html_builder.py) then renders that JSON into pixel-perfect TCC HTML — no LLM needed.
"""


def build_step5a_prompt(step4_output: str) -> str:
    """
    Minimal extraction prompt. The LLM's only job is to parse the article
    into a well-defined JSON schema. No HTML knowledge required.
    """
    return f"""Parse the article below into a JSON object matching EXACTLY this schema.
Output ONLY raw JSON — no markdown fences, no explanation.

SCHEMA:
{{
  "h1": "Article main title (string)",
  "subtitle": "1-2 sentence lead paragraph (string)",
  "tags": ["Tag1", "Tag2"],
  "metrics": [
    {{"label": "STAT NAME", "value": "75%", "note": "short description"}}
  ],
  "quick_facts": [
    {{"label": "Fact Label", "value": "Fact Value"}}
  ],
  "toc": [
    {{"id": "tcc-section-slug", "text": "Section Heading"}}
  ],
  "sections": [
    {{
      "id": "tcc-section-slug",
      "heading": "Section H2 Text",
      "blocks": [
        {{"type": "paragraph", "text": "Paragraph text. Preserve [LINK: URL] and [INTERNAL LINK: text] exactly."}},
        {{"type": "blockquote", "text": "Standalone pull-quote text (text in quotes on its own)"}},
        {{"type": "callout", "color": "pk", "text": "🎯 The Concept: explanation text"}},
        {{"type": "h3", "text": "Sub-heading text"}},
        {{"type": "table", "headers": ["Col1", "Col2"], "rows": [["val1", "val2"]]}},
        {{"type": "shift_grid", "cards": [{{"title": "Concept Name", "desc": "Description"}}]}},
        {{"type": "factor_grid", "cards": [{{"emoji": "🎯", "title": "Factor", "desc": "Description"}}]}},
        {{"type": "bar_chart", "title": "Chart Title", "source": "Source text", "bars": [{{"label": "Label", "value": "50%", "pct": 50}}]}}
      ]
    }}
  ],
  "faq": [
    {{"question": "Question text?", "answer": "Answer text."}}
  ],
  "schema_json": "raw JSON-LD string from the article (the <script type=application/ld+json> content)"
}}

RULES:
1. metrics: pick the 4 most important statistics from the article.
2. quick_facts: pick 5-7 key facts as short label:value pairs.
3. toc: one entry per H2 section. slug = lowercase H2 text with spaces replaced by hyphens, prefixed "tcc-".
4. sections[].blocks:
   - paragraph: any normal text paragraph. Preserve [LINK: URL] and [INTERNAL LINK: anchor text] markers exactly.
   - blockquote: any pull-quote (a sentence/phrase in quotation marks that stands alone).
   - callout: any emoji-led callout line (e.g. "🎯 The Barter Model: ..."). color = "pk" for 🎯, "bl" for 📊/💡, "gn" for ✅, "yw" for ⚠️.
   - shift_grid: any 2x2 or 2x3 named-concept grid (e.g. "Destination → Mindset / Seeking, Not Waiting").
   - factor_grid: any bullet-point list of named factors with descriptions.
   - table: any markdown table.
   - bar_chart: any numeric ranked data. pct = integer 0-100 representing bar height proportion.
   - h3: any H3 sub-heading.
5. faq: all Q&A pairs from the FAQ section.
6. schema_json: copy the raw JSON-LD text if present, else empty string "".
7. tags: 2-3 topic tags relevant to the article (e.g. "Education", "Career", "Exams").
8. Preserve ALL [LINK: URL] and [INTERNAL LINK: text] markers in paragraph text exactly as written.

ARTICLE:
{step4_output}
"""

"""
HTML Builder — Phase 2 of the two-phase Step 5.

Renders the structured JSON (from step5a_extract.py) into a complete
TCC-styled HTML content block using zero LLM tokens.

Usage:
    from services.html_builder import build_html_from_json
    html = build_html_from_json(json_string, meta={"author_name": "...", ...})
    # Returns None on JSON parse failure (caller should fallback to old Step 5).
"""

import json
import html as _html
from datetime import datetime


# ── helpers ───────────────────────────────────────────────────────────────────

def _e(text: str) -> str:
    """HTML-escape a string, but preserve [LINK: ...] and [INTERNAL LINK: ...] markers."""
    return _html.escape(str(text), quote=False)


def _slug(text: str) -> str:
    """Convert heading text to a tcc- prefixed anchor slug."""
    import re
    slug = re.sub(r'[^a-z0-9\s-]', '', text.lower())
    slug = re.sub(r'\s+', '-', slug.strip())
    return f"tcc-{slug[:40]}"


def _callout_class(color: str) -> str:
    allowed = {"pk", "gn", "yw", "bl", "pu"}
    c = color.lower() if color else "bl"
    return f"tcc-cb-{c}" if c in allowed else "tcc-cb-bl"


# ── block renderers ────────────────────────────────────────────────────────────

def _render_paragraph(block: dict) -> str:
    return f'<p class="tcc-p">{_e(block.get("text", ""))}</p>\n'


def _render_blockquote(block: dict) -> str:
    return f'<blockquote class="tcc-blockquote">{_e(block.get("text", ""))}</blockquote>\n'


def _render_callout(block: dict) -> str:
    cls = _callout_class(block.get("color", "bl"))
    return (
        f'<div class="tcc-callout {cls}">'
        f'<p>{_e(block.get("text", ""))}</p>'
        f'</div>\n'
    )


def _render_h3(block: dict) -> str:
    return f'<h3 class="tcc-h3">{_e(block.get("text", ""))}</h3>\n'


def _render_table(block: dict) -> str:
    headers = block.get("headers", [])
    rows = block.get("rows", [])
    th_cells = "".join(f"<th>{_e(h)}</th>" for h in headers)
    tbody = ""
    for row in rows:
        td_cells = "".join(f"<td>{_e(cell)}</td>" for cell in row)
        tbody += f"<tr>{td_cells}</tr>"
    return (
        '<div class="tcc-table-wrap">'
        '<table class="tcc-table">'
        f'<thead><tr>{th_cells}</tr></thead>'
        f'<tbody>{tbody}</tbody>'
        '</table></div>\n'
    )


def _render_shift_grid(block: dict) -> str:
    cards_html = ""
    for card in block.get("cards", []):
        title = _e(card.get("title", ""))
        desc = _e(card.get("desc", ""))
        cards_html += (
            f'<div class="tcc-shift-card">'
            f'<p class="tcc-shift-title">{title}</p>'
            f'<p class="tcc-shift-desc">{desc}</p>'
            f'</div>'
        )
    return f'<div class="tcc-shift-grid">{cards_html}</div>\n'


def _render_factor_grid(block: dict) -> str:
    cards_html = ""
    for card in block.get("cards", []):
        emoji = _e(card.get("emoji", "📌"))
        title = _e(card.get("title", ""))
        desc = _e(card.get("desc", ""))
        cards_html += (
            f'<div class="tcc-factor-card">'
            f'<p class="tcc-fi">{emoji}</p>'
            f'<p class="tcc-ft">{title}</p>'
            f'<p class="tcc-fd">{desc}</p>'
            f'</div>'
        )
    return f'<div class="tcc-factor-grid">{cards_html}</div>\n'


def _render_bar_chart(block: dict) -> str:
    title = _e(block.get("title", ""))
    source = _e(block.get("source", ""))
    bars = block.get("bars", [])

    # Normalise bar heights — tallest bar = 90px
    max_pct = max((b.get("pct", 0) for b in bars), default=1) or 1
    bars_html = ""
    colors = [
        "linear-gradient(180deg,#f542b0,#be185d)",
        "linear-gradient(180deg,#7c3aed,#4f46e5)",
        "linear-gradient(180deg,#0ea5e9,#0284c7)",
        "linear-gradient(180deg,#22c55e,#16a34a)",
        "linear-gradient(180deg,#f59e0b,#d97706)",
    ]
    for i, bar in enumerate(bars):
        pct = bar.get("pct", 0)
        height = max(8, int((pct / max_pct) * 90))
        color = colors[i % len(colors)]
        bars_html += (
            f'<div class="tcc-bar-col">'
            f'<div class="tcc-bar-top">{_e(bar.get("value", ""))}</div>'
            f'<div class="tcc-bar" style="height:{height}px;background:{color};"></div>'
            f'<div class="tcc-bar-btm">{_e(bar.get("label", ""))}</div>'
            f'</div>'
        )

    return (
        '<div class="tcc-charts-row">'
        '<div class="tcc-chart-box">'
        f'<p class="tcc-ct-ttl">{title}</p>'
        f'<p class="tcc-ct-src">{source}</p>'
        f'<div class="tcc-bar-row" style="height:110px;">{bars_html}</div>'
        '</div></div>\n'
    )


_BLOCK_RENDERERS = {
    "paragraph":   _render_paragraph,
    "blockquote":  _render_blockquote,
    "callout":     _render_callout,
    "h3":          _render_h3,
    "table":       _render_table,
    "shift_grid":  _render_shift_grid,
    "factor_grid": _render_factor_grid,
    "bar_chart":   _render_bar_chart,
}


def _render_blocks(blocks: list) -> str:
    out = ""
    for block in blocks:
        btype = block.get("type", "paragraph")
        renderer = _BLOCK_RENDERERS.get(btype, _render_paragraph)
        out += renderer(block)
    return out


# ── section components ─────────────────────────────────────────────────────────

def _build_hero(data: dict, meta: dict) -> str:
    author = _e(meta.get("author_name", "The Crazy Careers"))
    read_time = _e(meta.get("read_time", "5 min read"))
    raw_date = meta.get("publish_date", "Auto")
    publish_date = (
        datetime.now().strftime("%B %d, %Y")
        if str(raw_date).lower() == "auto"
        else _e(raw_date)
    )

    h1 = _e(data.get("h1", ""))
    subtitle = _e(data.get("subtitle", ""))

    # Tags
    tags_html = ""
    for tag in data.get("tags", [])[:3]:
        tags_html += (
            f'<span style="background:rgba(245,66,176,0.15);color:#f9a8d4;'
            f'font-size:11px;font-weight:600;padding:4px 12px;border-radius:20px;'
            f'border:1px solid rgba(245,66,176,0.3);">{_e(tag)}</span>'
        )

    # Metric cards (up to 4)
    metrics_html = ""
    for m in data.get("metrics", [])[:4]:
        metrics_html += (
            f'<div class="tcc-metric-card">'
            f'<p class="tcc-metric-label">{_e(m.get("label", ""))}</p>'
            f'<p class="tcc-metric-value">{_e(m.get("value", ""))}</p>'
            f'<p class="tcc-metric-note">{_e(m.get("note", ""))}</p>'
            f'</div>'
        )

    return f"""<div class="tcc-hero">
  <div class="tcc-hero-inner">
    <div class="tcc-hero-left">
      <div class="tcc-meta-row">
        <span class="tcc-meta-badge pink">{author}</span>
        <span class="tcc-meta-badge">{read_time}</span>
        <span class="tcc-meta-badge">{publish_date}</span>
      </div>
      <h1 class="tcc-hero-title">{h1}</h1>
      <p class="tcc-hero-subtitle">{subtitle}</p>
      <div style="display:flex;flex-wrap:wrap;gap:8px;margin-top:12px;">{tags_html}</div>
    </div>
    <div class="tcc-hero-right">{metrics_html}</div>
  </div>
</div>
"""


def _build_sidebar(data: dict) -> str:
    # TOC
    toc_items = ""
    for item in data.get("toc", []):
        toc_items += (
            f'<li><a href="#{_e(item.get("id", ""))}">'
            f'{_e(item.get("text", ""))}</a></li>'
        )

    # Quick facts
    qf_rows = ""
    for qf in data.get("quick_facts", [])[:7]:
        qf_rows += (
            f'<div class="tcc-quick-row">'
            f'<span class="ql">{_e(qf.get("label", ""))}</span>'
            f'<span class="qv">{_e(qf.get("value", ""))}</span>'
            f'</div>'
        )

    return f"""<div class="tcc-sidebar">
  <div class="tcc-toc-box">
    <p class="tcc-toc-head">📋 Table of Contents</p>
    <ol>{toc_items}</ol>
  </div>
  <div class="tcc-quick-box">
    <p class="tcc-quick-head">⚡ Quick Facts</p>
    {qf_rows}
  </div>
</div>
"""


def _build_content_body(data: dict) -> str:
    out = ""
    for section in data.get("sections", []):
        sec_id = _e(section.get("id", _slug(section.get("heading", ""))))
        heading = _e(section.get("heading", ""))
        out += f'<h2 id="{sec_id}" class="tcc-h2">{heading}</h2>\n'
        out += _render_blocks(section.get("blocks", []))

    # Author bio box (before FAQ)
    out += """<div class="tcc-author-box">
  <div class="tcc-author-avatar">✍️</div>
  <div class="tcc-author-info">
    <p class="tcc-author-name">The Crazy Careers Team</p>
    <p class="tcc-author-bio">The Crazy Careers is India's career guidance platform for students and early professionals — helping you navigate education, careers, and the future of work.</p>
  </div>
</div>
"""
    return out


def _build_faq(data: dict) -> str:
    if not data.get("faq"):
        return ""
    items_html = ""
    for item in data.get("faq", []):
        q = _e(item.get("question", ""))
        a = _e(item.get("answer", ""))
        items_html += (
            f'<div class="tcc-faq-item">'
            f'<div class="tcc-faq-q"><strong>{q}</strong>'
            f'<span class="tcc-faq-icon">+</span></div>'
            f'<div class="tcc-faq-a"><p>{a}</p></div>'
            f'</div>\n'
        )
    return (
        f'<h2 id="tcc-faq" class="tcc-h2">Frequently Asked Questions</h2>\n'
        + items_html
    )


def _build_schema(data: dict) -> str:
    schema_json = data.get("schema_json", "").strip()
    if not schema_json:
        return ""
    # Wrap in script tag if it looks like raw JSON (not already wrapped)
    if schema_json.startswith("{") or schema_json.startswith("["):
        return f'<script type="application/ld+json">\n{schema_json}\n</script>\n'
    return ""  # Malformed — skip


# ── main entry point ───────────────────────────────────────────────────────────

def build_html_from_json(json_string: str, meta: dict = None) -> str | None:
    """
    Parse the JSON string from Step 5a and render it into a complete
    TCC-styled HTML content block (tcc-wrap div).

    Returns None if json_string cannot be parsed (caller should fallback
    to the old LLM-based Step 5).
    """
    meta = meta or {}

    # ── 1. Parse JSON ──────────────────────────────────────────────────────────
    try:
        # Strip markdown fences if the LLM wrapped it anyway
        clean = json_string.strip()
        if clean.startswith("```"):
            lines = clean.splitlines()
            # Drop first line (```json) and last line (```)
            clean = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
        data = json.loads(clean)
    except (json.JSONDecodeError, ValueError) as exc:
        print(f"[HTML Builder] JSON parse failed: {exc} — will fallback to old Step 5")
        return None

    # ── 2. Render ──────────────────────────────────────────────────────────────
    try:
        hero    = _build_hero(data, meta)
        sidebar = _build_sidebar(data)
        body    = _build_content_body(data)
        faq     = _build_faq(data)
        schema  = _build_schema(data)

        html_block = (
            '<div class="tcc-wrap">\n'
            + hero
            + '<div class="tcc-layout">\n'
            + sidebar
            + '<div class="tcc-content">\n'
            + body
            + faq
            + '</div>\n'   # .tcc-content
            + '</div>\n'   # .tcc-layout
            + schema
            + '</div>\n'   # .tcc-wrap
        )
        return html_block

    except Exception as exc:
        print(f"[HTML Builder] Render error: {exc} — will fallback to old Step 5")
        return None

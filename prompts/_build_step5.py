"""
Builder script: reads the CSS from referencehtml_T2C.html and generates step5_html.py
with the exact reference CSS and updated prompt.
"""
import os

# Read the reference HTML
ref_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "referencehtml_T2C.html")
with open(ref_path, "r", encoding="utf-8") as f:
    ref_html = f.read()

# Extract the <style>...</style> block
style_start = ref_html.index("<style>")
style_end = ref_html.index("</style>") + len("</style>")
css_block = ref_html[style_start:style_end]

# Build the new step5_html.py
output = '''"""Step 5 — Generate a complete standalone HTML page matching the TCC reference template.

Strategy: Keep the prompt SMALL (no embedded CSS). The AI generates the HTML structure
and content using the tcc-* class names. The runner then reads the full CSS from the
reference template and wraps the output into a complete standalone HTML file.
"""

import os


def get_reference_css() -> str:
    """
    Returns the full <style>...</style> block for the TCC Design System.
    Extracted verbatim from the manager-approved reference template (referencehtml_T2C.html).
    """
    return """''' + css_block + '''"""


from datetime import datetime

def build_step5_prompt(step4_output: str, meta: dict = None) -> str:
    """
    Lean prompt — asks the model only for the CONTENT HTML using tcc-* classes.
    The full CSS and <html>/<head>/<body> wrapper are added by the runner.
    """
    meta = meta or {}
    author_name = meta.get("author_name", "The Crazy Careers")
    read_time   = meta.get("read_time", "5 min read")
    
    # Process Auto date
    raw_date = meta.get("publish_date", "Auto")
    if raw_date.lower() == "auto":
        publish_date = datetime.now().strftime("%B %d, %Y")
    else:
        publish_date = raw_date

    return f"""
STEP 5: CONVERT ARTICLE TO STYLED HTML CONTENT BLOCK

[Article + FAQ + Schema from Step 4]:
{step4_output}

Convert the article above into an HTML content block using the TCC design system class names.
Do NOT include <html>, <head>, <body>, or any <style> tags — output content only.
The outermost element MUST be <div class="tcc-wrap">.

═══════════════════════════════════════
TCC CSS CLASS REFERENCE (use EXACTLY these class names)
═══════════════════════════════════════

OUTERMOST WRAPPER:
  <div class="tcc-wrap">
    <!-- Everything goes inside here -->
  </div>

HERO BANNER — wrap the title/intro/stats in this structure:
  <div class="tcc-hero">
    <div class="tcc-hero-inner">
      <div class="tcc-hero-left">
        <div class="tcc-meta-row">
          <span class="tcc-meta-badge pink">{author_name}</span>
          <span class="tcc-meta-badge">{read_time}</span>
          <span class="tcc-meta-badge">{publish_date}</span>
        </div>
        <h1 class="tcc-hero-title">Title with <span class="pink">keyword</span></h1>
        <p class="tcc-hero-subtitle">2-sentence subtitle</p>
        <!-- Category tags row -->
        <div style="display:flex;flex-wrap:wrap;gap:8px;">
          <span style="background:rgba(245,66,176,0.15);color:#f9a8d4;font-size:11px;font-weight:600;padding:4px 12px;border-radius:20px;border:1px solid rgba(245,66,176,0.3);">Tag 1</span>
        </div>
      </div>
      <div class="tcc-hero-right">
        <!-- 4 x .tcc-metric-card with .tcc-metric-label / .tcc-metric-value / .tcc-metric-note -->
        <!-- Pull 4 key statistics from the article -->
      </div>
    </div>
  </div>

LAYOUT — sidebar left, content right:
  <div class="tcc-layout">
    <div class="tcc-sidebar">
      <div class="tcc-toc-box">
        <p class="tcc-toc-head">📋 Table of Contents</p>
        <ol><!-- <li><a href="#section-id">Section Name</a></li> for each H2 --></ol>
      </div>
      <div class="tcc-quick-box">
        <p class="tcc-quick-head">⚡ Quick Facts</p>
        <!-- 5-7 x .tcc-quick-row with .ql (label) and .qv (value) spans -->
      </div>
    </div>
    <div class="tcc-content">
      <!-- All article content goes here -->
    </div>
  </div>

SECTION HEADINGS:   <h2 id="unique-id" class="tcc-h2">...</h2>
                    <h3 class="tcc-h3">...</h3>
PARAGRAPHS:         <p class="tcc-p">...</p>
TABLES:             <div class="tcc-table-wrap"><table class="tcc-table">
                      <thead><tr><!-- th cells --></tr></thead>
                      <tbody><!-- td cells --></tbody>
                    </table></div>
BADGES IN TABLES:   <span class="tcc-gn">green</span>  <span class="tcc-yw">yellow</span>
                    <span class="tcc-rd">red</span>     <span class="tcc-pk">pink</span>
                    <span class="tcc-bl">blue</span>    <span class="tcc-pu">purple</span>
SOURCE CREDIT:      <p class="tcc-src">Source: ...</p>
CALLOUT BOXES:      <div class="tcc-callout tcc-cb-yw"><p>💡 <strong>Tip:</strong> ...</p></div>
                    Use tcc-cb-gn (green), tcc-cb-yw (yellow), tcc-cb-bl (blue), tcc-cb-pk (pink), tcc-cb-pu (purple)
BAR CHART:          <div class="tcc-charts-row">
                      <div class="tcc-chart-box">
                        <p class="tcc-ct-ttl">Chart Title</p>
                        <p class="tcc-ct-src">Source info</p>
                        <div class="tcc-bar-row" style="height:110px;">
                          <div class="tcc-bar-col">
                            <div class="tcc-bar-top">value</div>
                            <div class="tcc-bar" style="height:Xpx;background:linear-gradient(180deg,#f542b0,#be185d);"></div>
                            <div class="tcc-bar-btm">label</div>
                          </div>
                        </div>
                      </div>
                    </div>
HORIZONTAL BARS:    <div class="tcc-hbar">
                      <div class="tcc-hbar-meta"><span class="tcc-hbar-name">Label</span><span class="tcc-hbar-val">Value</span></div>
                      <div class="tcc-hbar-track"><div class="tcc-hbar-fill" style="width:85%;background:linear-gradient(to right,#f542b0,#be185d);"></div></div>
                    </div>
COMPANY CARDS:      <div class="tcc-co-grid">
                      <div class="tcc-co-card">
                        <div class="tcc-co-emoji">🏢</div>
                        <p class="tcc-co-name">Company</p>
                        <p class="tcc-co-type">Type · City</p>
                        <div class="tcc-co-row"><span class="cr">Key</span><span class="cs">Value</span></div>
                        <span class="tcc-co-tag">Label</span>
                      </div>
                    </div>
FACTOR CARDS:       <div class="tcc-factor-grid">
                      <div class="tcc-factor-card">
                        <p class="tcc-fi">🎯</p>
                        <p class="tcc-ft">Factor Title</p>
                        <p class="tcc-fd">Description</p>
                      </div>
                    </div>
FAQ ACCORDION:      <div class="tcc-faq-item">
                      <div class="tcc-faq-q"><strong>Question?</strong><span class="tcc-faq-icon">+</span></div>
                      <div class="tcc-faq-a"><p>Answer text.</p></div>
                    </div>

═══════════════════════════════════════
CONTENT RULES
═══════════════════════════════════════

1. Extract ALL data from the Step 4 article — do NOT invent numbers or facts.
2. Put the 4 most important statistics into hero metric cards.
3. Build the TOC from every H2 section (assign each a unique id like "tcc-salary" "tcc-experience").
4. Put 5-7 quick data points in the sidebar Quick Facts.
5. Convert every table in the article to .tcc-table format.
6. Wrap tips/warnings/info as .tcc-callout boxes.
7. Build the FAQ section using .tcc-faq-item accordion markup.
8. Add a bar chart if the article has ranked numeric data (salary levels, etc.).
9. Use horizontal bars (.tcc-hbar) for city or comparison data with percentage widths.
10. Use .tcc-co-grid for company comparisons, .tcc-factor-grid for factor/reason lists.
11. Add 2-3 category tags in the hero banner after the subtitle.
12. Convert any [LINK: url] citations into actual clickable HTML anchor tags.

OUTPUT: Output ONLY the raw HTML block described above, starting with <div class="tcc-wrap"> and ending with </div>.
No explanation. No markdown fences. No <html>/<head>/<body>/<style> tags.
"""
'''

out_path = os.path.join(os.path.dirname(__file__), "step5_html.py")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(output)

print(f"step5_html.py rebuilt successfully ({len(output)} chars)")
print(f"   CSS block: {len(css_block)} chars")

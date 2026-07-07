"""Step 5 — Generate a complete standalone HTML page matching the TCC reference template.

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
    return """<style>
.tcc-wrap { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
.tcc-wrap * { box-sizing: border-box; margin: 0; padding: 0; }

/* ═══════════════════════════
   HERO BANNER
═══════════════════════════ */
.tcc-hero {
  background: linear-gradient(135deg, #14142B 0%, #2d1b4e 55%, #1a0a2e 100%);
  border-radius: 14px;
  padding: 36px 40px;
  margin: 0 0 32px 0;
  position: relative;
  overflow: hidden;
}
.tcc-hero::before {
  content: '';
  position: absolute;
  top: -80px; right: -80px;
  width: 340px; height: 340px;
  background: radial-gradient(circle, rgba(245,66,176,0.25) 0%, transparent 70%);
  border-radius: 50%;
  pointer-events: none;
}
.tcc-hero::after {
  content: '';
  position: absolute;
  bottom: -60px; left: 30%;
  width: 200px; height: 200px;
  background: radial-gradient(circle, rgba(245,66,176,0.1) 0%, transparent 70%);
  border-radius: 50%;
  pointer-events: none;
}

/* Hero 2-col layout */
.tcc-hero-inner {
  display: flex;
  gap: 32px;
  align-items: center;
  position: relative;
  z-index: 1;
}
.tcc-hero-left {
  flex: 1.1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
/* RIGHT: 2x2 grid of metric cards */
.tcc-hero-right {
  flex: 0.85;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  align-self: center;
}

/* Meta badges */
.tcc-meta-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 0 0 14px 0;
  align-items: center;
}
.tcc-meta-badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 11px;
  color: #c0b8d0;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 20px;
  padding: 3px 9px;
  white-space: nowrap;
}
.tcc-meta-badge.pink { background: rgba(245,66,176,0.15); border-color: rgba(245,66,176,0.3); color: #f9a8d4; }
.tcc-meta-badge svg { width: 11px; height: 11px; fill: currentColor; flex-shrink: 0; }

/* Hero title */
.tcc-hero-title {
  font-size: 26px;
  font-weight: 800;
  color: #ffffff;
  line-height: 1.25;
  margin: 0 0 10px 0;
}
.tcc-hero-title .pink { color: #f542b0; }
.tcc-hero-subtitle {
  font-size: 13px;
  color: #a0a0c0;
  line-height: 1.7;
  margin: 0 0 16px 0;
}

/* Updated badge */
.tcc-updated {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: #86efac;
  background: rgba(34,197,94,0.1);
  border: 1px solid rgba(34,197,94,0.25);
  border-radius: 4px;
  padding: 3px 9px;
}

/* Metric cards — compact, 2x2 grid */
.tcc-metric-card {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(245,66,176,0.3);
  border-radius: 10px;
  padding: 12px 14px;
}
.tcc-metric-label {
  font-size: 9px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  color: #f542b0;
  margin: 0 0 4px 0;
}
.tcc-metric-value {
  font-size: 20px;
  font-weight: 800;
  color: #fff;
  line-height: 1;
  margin: 0 0 3px 0;
}
.tcc-metric-note { font-size: 10px; color: #7070a0; margin: 0; line-height: 1.4; }

/* ═══════════════════════════
   MAIN LAYOUT — TOC LEFT + CONTENT RIGHT
═══════════════════════════ */
.tcc-layout {
  display: flex;
  gap: 28px;
  align-items: flex-start;
}
.tcc-sidebar {
  width: 230px;
  flex-shrink: 0;
  position: sticky;
  top: 80px;
}
.tcc-content { flex: 1; min-width: 0; }

/* TOC Box */
.tcc-toc-box {
  background: #fafafa;
  border: 2px solid #f0e0fa;
  border-radius: 12px;
  padding: 18px 20px;
  margin-bottom: 16px;
}
.tcc-toc-head {
  font-size: 13px;
  font-weight: 800;
  color: #14142B;
  margin: 0 0 12px 0;
  display: flex;
  align-items: center;
  gap: 6px;
}
.tcc-toc-box ol {
  list-style: none;
  padding: 0;
  margin: 0;
  counter-reset: toc-counter;
}
.tcc-toc-box ol li {
  counter-increment: toc-counter;
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
  align-items: flex-start;
}
.tcc-toc-box ol li::before {
  content: counter(toc-counter);
  background: #f542b0;
  color: #fff;
  font-size: 10px;
  font-weight: 700;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 2px;
}
.tcc-toc-box a {
  font-size: 12px;
  color: #334155;
  text-decoration: none;
  line-height: 1.5;
  transition: color 0.15s;
}
.tcc-toc-box a:hover { color: #f542b0; }

/* Quick Facts sidebar */
.tcc-quick-box {
  background: linear-gradient(135deg, #14142B, #2d1b4e);
  border-radius: 12px;
  padding: 18px 20px;
  margin-bottom: 16px;
}
.tcc-quick-head {
  font-size: 12px;
  font-weight: 700;
  color: #f542b0;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  margin: 0 0 12px 0;
}
.tcc-quick-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255,255,255,0.07);
  font-size: 12px;
  line-height: 1.5;
}
.tcc-quick-row:last-child { border-bottom: none; }
.tcc-quick-row .ql {
  color: #8080a0;
  min-width: 80px;
  flex-shrink: 0;
  padding-top: 1px;
}
.tcc-quick-row .qv {
  color: #fff;
  font-weight: 700;
  text-align: right;
  word-break: break-word;
}

/* ═══════════════════════════
   SECTION HEADINGS
═══════════════════════════ */
.tcc-h2 {
  font-size: 22px;
  font-weight: 800;
  color: #14142B;
  margin: 40px 0 14px 0;
  padding-bottom: 10px;
  border-bottom: 3px solid #f542b0;
}
.tcc-h2:first-child { margin-top: 0; }
.tcc-h3 {
  font-size: 17px;
  font-weight: 700;
  color: #14142B;
  margin: 24px 0 10px 0;
}
.tcc-p {
  font-size: 15px;
  line-height: 1.8;
  color: #334155;
  margin: 0 0 14px 0;
}

/* ═══════════════════════════
   TABLES
═══════════════════════════ */
.tcc-table-wrap { overflow-x: auto; margin: 14px 0 6px 0; }
.tcc-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 2px 14px rgba(0,0,0,0.07);
}
.tcc-table thead tr { background: #14142B; color: #fff; }
.tcc-table th { padding: 12px 14px; text-align: left; font-weight: 600; font-size: 12px; }
.tcc-table td { padding: 11px 14px; border-bottom: 1px solid #f0f0f5; color: #334155; }
.tcc-table tbody tr:nth-child(even) { background: #fafafa; }
.tcc-table tbody tr:nth-child(odd) { background: #fff; }
.tcc-table tbody tr:hover { background: #fdf2f8; }
.tcc-pk { background: #fce7f3; color: #be185d; padding: 2px 9px; border-radius: 20px; font-weight: 700; font-size: 12px; white-space: nowrap; }
.tcc-gn { background: #dcfce7; color: #166534; padding: 2px 9px; border-radius: 20px; font-weight: 700; font-size: 12px; }
.tcc-yw { background: #fef9c3; color: #854d0e; padding: 2px 9px; border-radius: 20px; font-weight: 700; font-size: 12px; }
.tcc-rd { background: #fee2e2; color: #991b1b; padding: 2px 9px; border-radius: 20px; font-weight: 700; font-size: 12px; }
.tcc-bl { background: #dbeafe; color: #1d4ed8; padding: 2px 9px; border-radius: 20px; font-weight: 600; font-size: 11px; }
.tcc-pu { background: #f3e8ff; color: #6b21a8; padding: 2px 9px; border-radius: 20px; font-weight: 700; font-size: 12px; }
.tcc-src { font-size: 11px; color: #94a3b8; margin: 4px 0 20px 0; }

/* ═══════════════════════════
   CALLOUT BOXES
═══════════════════════════ */
.tcc-callout { border-radius: 10px; padding: 14px 18px; margin: 14px 0 20px 0; }
.tcc-cb-pk { background: #fdf2f8; border-left: 4px solid #f542b0; }
.tcc-cb-gn { background: #f0fdf4; border-left: 4px solid #22c55e; }
.tcc-cb-yw { background: #fffbeb; border-left: 4px solid #f59e0b; }
.tcc-cb-pu { background: #faf5ff; border-left: 4px solid #7c3aed; }
.tcc-cb-bl { background: #eff6ff; border-left: 4px solid #3b82f6; }
.tcc-callout p { margin: 0; font-size: 13px; color: #334155; line-height: 1.7; }

/* ═══════════════════════════
   INTERACTIVE CALCULATOR
═══════════════════════════ */
.tcc-calc-wrap {
  background: #fdf8ff;
  border: 2px solid #f0e0fa;
  border-radius: 14px;
  padding: 24px;
  margin: 16px 0 28px 0;
}
.tcc-calc-ttl { font-size: 17px; font-weight: 800; color: #14142B; margin: 0 0 4px 0; }
.tcc-calc-sub { font-size: 12px; color: #64748b; margin: 0 0 20px 0; }
.tcc-calc-grid { display: flex; gap: 20px; flex-wrap: wrap; }
.tcc-calc-inputs { flex: 1; min-width: 240px; }
.tcc-calc-result {
  flex: 1; min-width: 220px;
  background: #14142B;
  border-radius: 12px;
  padding: 22px;
  color: #fff;
}
.tcc-field { margin-bottom: 14px; }
.tcc-field label {
  display: block;
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  color: #64748b;
  margin-bottom: 5px;
}
.tcc-field select {
  width: 100%;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  padding: 9px 11px;
  font-size: 13px;
  color: #14142B;
  background: #fff;
  outline: none;
  cursor: pointer;
}
.tcc-field select:focus { border-color: #f542b0; }
.tcc-range-lbl { font-size: 12px; font-weight: 700; color: #f542b0; text-align: right; margin-bottom: 3px; }
.tcc-field input[type="range"] {
  width: 100%; height: 4px; border: none; border-radius: 2px;
  outline: none; cursor: pointer;
  accent-color: #f542b0;
}
.tcc-range-ticks { display: flex; justify-content: space-between; font-size: 9px; color: #94a3b8; margin-top: 2px; }
.tcc-res-lbl { font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; color: #f542b0; margin: 0 0 6px 0; }
.tcc-res-ctc { font-size: 36px; font-weight: 900; color: #fff; margin: 0 0 2px 0; line-height: 1; }
.tcc-res-range { font-size: 11px; color: #8080a0; margin: 0 0 18px 0; }
.tcc-res-bdr { border-top: 1px solid rgba(255,255,255,0.1); padding-top: 14px; }
.tcc-res-row { display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 7px; }
.tcc-res-row .rl { color: #a0a0c0; }
.tcc-res-row .rv { color: #fff; font-weight: 600; }
.tcc-res-row .rv.pk { color: #f542b0; }
.tcc-pct-bar { margin-top: 14px; background: rgba(255,255,255,0.1); border-radius: 4px; height: 5px; }
.tcc-pct-fill { height: 100%; background: linear-gradient(to right, #22c55e, #f542b0); border-radius: 4px; transition: width 0.4s; }
.tcc-pct-txt { font-size: 10px; color: #f542b0; text-align: center; margin-top: 5px; font-weight: 600; }

/* ═══════════════════════════
   CHARTS
═══════════════════════════ */
.tcc-charts-row { display: flex; gap: 14px; flex-wrap: wrap; margin: 16px 0 20px 0; }
.tcc-chart-box {
  flex: 1; min-width: 260px;
  background: #fff;
  border: 1px solid #f0f0f5;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}
.tcc-ct-ttl { font-size: 13px; font-weight: 700; color: #14142B; margin: 0 0 3px 0; }
.tcc-ct-src { font-size: 10px; color: #94a3b8; margin: 0 0 16px 0; }
.tcc-bar-row { display: flex; align-items: flex-end; gap: 6px; height: 120px; }
.tcc-bar-col { flex: 1; display: flex; flex-direction: column; align-items: center; }
.tcc-bar-top { font-size: 9px; font-weight: 700; color: #14142B; margin-bottom: 3px; }
.tcc-bar { width: 100%; border-radius: 4px 4px 0 0; }
.tcc-bar-btm { font-size: 9px; color: #64748b; text-align: center; margin-top: 5px; line-height: 1.3; }

/* City H-bars */
.tcc-hbar { margin-bottom: 9px; }
.tcc-hbar-meta { display: flex; justify-content: space-between; font-size: 11px; margin-bottom: 3px; }
.tcc-hbar-name { color: #334155; font-weight: 600; }
.tcc-hbar-val { color: #f542b0; font-weight: 700; }
.tcc-hbar-track { background: #f0f0f5; border-radius: 3px; height: 8px; overflow: hidden; }
.tcc-hbar-fill { height: 100%; border-radius: 3px; }

/* ═══════════════════════════
   COMPANY CARDS
═══════════════════════════ */
.tcc-co-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
  margin: 16px 0 24px 0;
}
.tcc-co-card {
  border: 2px solid #f0f0f5;
  border-radius: 12px;
  padding: 18px;
  background: #fff;
  transition: box-shadow 0.2s, border-color 0.2s;
}
.tcc-co-card:hover { box-shadow: 0 4px 20px rgba(245,66,176,0.12); border-color: #f542b0; }
.tcc-co-card.top { border-color: #f542b0; }
.tcc-co-rank { font-size: 10px; font-weight: 700; color: #94a3b8; text-align: right; margin: 0 0 8px 0; }
.tcc-co-rank.pk { color: #f542b0; }
.tcc-co-emoji { font-size: 26px; }
.tcc-co-name { font-size: 15px; font-weight: 800; color: #14142B; margin: 6px 0 3px 0; }
.tcc-co-type { font-size: 10px; color: #94a3b8; margin: 0 0 12px 0; }
.tcc-co-row { display: flex; justify-content: space-between; font-size: 12px; padding: 5px 0; border-bottom: 1px solid #f5f5fa; }
.tcc-co-row .cr { color: #64748b; }
.tcc-co-row .cs { font-weight: 700; color: #14142B; }
.tcc-co-tag { display: inline-block; margin-top: 12px; background: #fdf2f8; color: #f542b0; font-size: 10px; font-weight: 700; padding: 3px 9px; border-radius: 4px; text-transform: uppercase; letter-spacing: 0.5px; }
.tcc-co-tag.rd { background: #fee2e2; color: #991b1b; }

/* ═══════════════════════════
   FACTOR CARDS
═══════════════════════════ */
.tcc-factor-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin: 14px 0 24px 0;
}
.tcc-factor-card {
  background: #fff;
  border: 1px solid #f0f0f5;
  border-radius: 10px;
  padding: 16px 18px;
  box-shadow: 0 1px 6px rgba(0,0,0,0.04);
  transition: box-shadow 0.2s;
}
.tcc-factor-card:hover { box-shadow: 0 4px 14px rgba(245,66,176,0.09); }
.tcc-fi { font-size: 20px; margin: 0 0 6px 0; }
.tcc-ft { font-size: 14px; font-weight: 700; color: #14142B; margin: 0 0 5px 0; }
.tcc-fd { font-size: 12px; color: #64748b; line-height: 1.6; margin: 0; }

/* ═══════════════════════════
   FAQ
═══════════════════════════ */
.tcc-faq-item { border: 1px solid #f0f0f5; border-radius: 10px; margin-bottom: 8px; overflow: hidden; }
.tcc-faq-q {
  background: #fafafa; padding: 14px 18px; cursor: pointer;
  display: flex; justify-content: space-between; align-items: center; user-select: none;
}
.tcc-faq-q:hover { background: #fdf2f8; }
.tcc-faq-q strong { font-size: 13px; color: #14142B; flex: 1; padding-right: 10px; }
.tcc-faq-icon { color: #f542b0; font-size: 18px; font-weight: 700; transition: transform 0.2s; line-height: 1; }
.tcc-faq-a { display: none; padding: 14px 18px; border-top: 1px solid #f0f0f5; background: #fff; }
.tcc-faq-a p { margin: 0; font-size: 13px; color: #334155; line-height: 1.7; }
.tcc-faq-item.open .tcc-faq-a { display: block; }
.tcc-faq-item.open .tcc-faq-icon { transform: rotate(45deg); }

/* ═══════════════════════════════════════════
   ROOT FIX — PREVENT HORIZONTAL SCROLL
═══════════════════════════════════════════ */
.tcc-wrap {
  max-width: 100%;
  overflow-x: hidden;
}
.tcc-wrap * {
  max-width: 100%;
}

/* ═══════════════════════════════════════════
   RESPONSIVE — TABLET (max 900px)
═══════════════════════════════════════════ */
@media (max-width: 900px) {

  /* Hero */
  .tcc-hero { padding: 24px 20px; border-radius: 10px; margin-bottom: 20px; }
  .tcc-hero-inner { flex-direction: column; gap: 20px; }
  .tcc-hero-left { width: 100%; }
  .tcc-hero-right { grid-template-columns: 1fr 1fr; width: 100%; gap: 10px; }
  .tcc-hero-title { font-size: 22px; }
  .tcc-hero-subtitle { font-size: 13px; }
  .tcc-metric-value { font-size: 18px; }

  /* Layout: sidebar above content */
  .tcc-layout { flex-direction: column; gap: 20px; }
  .tcc-sidebar { width: 100%; position: static; display: flex; gap: 14px; flex-wrap: wrap; }
  .tcc-toc-box { flex: 2; min-width: 240px; }
  .tcc-quick-box { flex: 1; min-width: 160px; }
  .tcc-toc-box ol { column-count: 2; column-gap: 16px; }

  /* Tables */
  .tcc-table-wrap { overflow-x: auto; -webkit-overflow-scrolling: touch; width: 100%; }
  .tcc-table { min-width: 500px; font-size: 12px; }
  .tcc-table th, .tcc-table td { padding: 9px 10px; font-size: 12px; }

  /* Charts */
  .tcc-charts-row { flex-direction: column; }
  .tcc-chart-box { min-width: 0; width: 100%; }

  /* Calculator */
  .tcc-calc-grid { flex-direction: column; }
  .tcc-calc-inputs { min-width: 0; width: 100%; }
  .tcc-calc-result { min-width: 0; width: 100%; }

  /* Company grid */
  .tcc-co-grid { grid-template-columns: 1fr 1fr; gap: 12px; }

  /* Factor grid */
  .tcc-factor-grid { grid-template-columns: 1fr 1fr; }
}

/* ═══════════════════════════════════════════
   RESPONSIVE — MOBILE (max 580px)
═══════════════════════════════════════════ */
@media (max-width: 580px) {

  /* Hero */
  .tcc-hero { padding: 18px 14px; border-radius: 10px; }
  .tcc-hero-inner { gap: 16px; }
  .tcc-hero-title { font-size: 18px; line-height: 1.3; }
  .tcc-hero-subtitle { font-size: 12px; line-height: 1.6; }
  .tcc-hero-right { grid-template-columns: 1fr 1fr; gap: 8px; }
  .tcc-metric-card { padding: 10px 10px; border-radius: 8px; }
  .tcc-metric-value { font-size: 15px; }
  .tcc-metric-label { font-size: 8px; letter-spacing: 0.5px; }
  .tcc-metric-note { font-size: 9px; }
  .tcc-meta-row { gap: 5px; margin-bottom: 10px; }
  .tcc-meta-badge { font-size: 10px; padding: 2px 7px; }

  /* Sidebar: stack vertically */
  .tcc-sidebar { flex-direction: column; gap: 12px; }
  .tcc-toc-box { min-width: 0; width: 100%; }
  .tcc-quick-box { min-width: 0; width: 100%; }
  .tcc-toc-box ol { column-count: 1; }
  .tcc-toc-box a { font-size: 12px; }
  .tcc-quick-row { font-size: 11px; }

  /* Content typography */
  .tcc-content { min-width: 0; width: 100%; overflow: hidden; }
  .tcc-h2 { font-size: 17px; margin: 28px 0 10px 0; padding-bottom: 8px; }
  .tcc-h3 { font-size: 15px; margin: 18px 0 8px 0; }
  .tcc-p { font-size: 13px; line-height: 1.7; }

  /* Tables — scrollable container, DO NOT let table overflow */
  .tcc-table-wrap {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    width: 100%;
    border-radius: 8px;
  }
  .tcc-table { min-width: 440px; font-size: 11px; }
  .tcc-table th { font-size: 10px; padding: 8px 9px; white-space: nowrap; }
  .tcc-table td { font-size: 11px; padding: 8px 9px; }

  /* Charts — prevent overflow */
  .tcc-chart-box { padding: 14px; overflow: hidden; }
  .tcc-ct-ttl { font-size: 12px; }
  .tcc-ct-src { font-size: 10px; }
  .tcc-bar-row { gap: 4px; height: 90px; }
  .tcc-bar-top { font-size: 8px; }
  .tcc-bar-btm { font-size: 8px; }

  /* City horizontal bars */
  .tcc-hbar { margin-bottom: 8px; }
  .tcc-hbar-meta { font-size: 10px; }
  .tcc-hbar-name { font-size: 10px; min-width: 65px; }
  .tcc-hbar-val { font-size: 10px; }
  .tcc-hbar-track { height: 18px; }
  .tcc-hbar-fill { padding-left: 5px; }

  /* SVG trend chart */
  .tcc-trend-wrap svg { width: 100%; }

  /* Calculator */
  .tcc-calc-wrap { padding: 16px 14px; border-radius: 10px; }
  .tcc-calc-ttl { font-size: 14px; }
  .tcc-calc-sub { font-size: 11px; }
  .tcc-field { margin-bottom: 12px; }
  .tcc-field label { font-size: 10px; }
  .tcc-field select { font-size: 12px; padding: 8px 10px; }
  .tcc-range-lbl { font-size: 11px; }
  .tcc-range-ticks { font-size: 8px; }
  .tcc-calc-result { padding: 16px 14px; border-radius: 10px; }
  .tcc-res-lbl { font-size: 9px; }
  .tcc-res-ctc { font-size: 28px; }
  .tcc-res-range { font-size: 10px; }
  .tcc-res-row { font-size: 11px; }
  .tcc-pct-txt { font-size: 10px; }

  /* Company cards */
  .tcc-co-grid { grid-template-columns: 1fr; gap: 10px; }
  .tcc-co-card { padding: 14px; }
  .tcc-co-name { font-size: 14px; }
  .tcc-co-type { font-size: 10px; }
  .tcc-co-row { font-size: 11px; padding: 5px 0; }
  .tcc-co-emoji { font-size: 22px; }
  .tcc-co-tag { font-size: 9px; padding: 3px 8px; }

  /* Factor cards */
  .tcc-factor-grid { grid-template-columns: 1fr; gap: 10px; }
  .tcc-factor-card { padding: 13px 14px; }
  .tcc-fi { font-size: 18px; }
  .tcc-ft { font-size: 13px; }
  .tcc-fd { font-size: 12px; }

  /* Callout boxes */
  .tcc-callout { padding: 12px 13px; }
  .tcc-callout p { font-size: 12px; line-height: 1.6; }

  /* FAQ */
  .tcc-faq-item { margin-bottom: 7px; }
  .tcc-faq-q { padding: 12px 14px; }
  .tcc-faq-q strong { font-size: 12px; }
  .tcc-faq-a { padding: 12px 14px; }
  .tcc-faq-a p { font-size: 12px; }

  /* AI widget */
  .tcc-ai-widget { padding: 12px 12px; gap: 10px; }
  .tcc-ai-text { font-size: 12px; width: 100%; text-align: center; }
  .tcc-ai-icon { height: 24px; width: 24px; }

  /* Content images */
  .tcc-content-img { max-height: 180px; border-radius: 8px; }

  /* Badges */
  .tcc-pk, .tcc-gn, .tcc-yw, .tcc-rd, .tcc-bl, .tcc-pu {
    font-size: 10px; padding: 2px 7px;
  }

  /* Source text */
  .tcc-src { font-size: 10px; }
}

/* ═══════════════════════════════════════════
   RESPONSIVE — SMALL MOBILE (max 380px)
═══════════════════════════════════════════ */
@media (max-width: 380px) {
  .tcc-hero { padding: 14px 12px; }
  .tcc-hero-title { font-size: 16px; }
  .tcc-metric-value { font-size: 13px; }
  .tcc-metric-card { padding: 8px; }
  .tcc-h2 { font-size: 15px; }
  .tcc-table { min-width: 380px; }
  .tcc-table th, .tcc-table td { padding: 7px 8px; font-size: 10px; }
  .tcc-res-ctc { font-size: 24px; }
}
  .tcc-hero-title { font-size: 17px; }
  .tcc-hero-right { grid-template-columns: 1fr 1fr; gap: 6px; }
  .tcc-metric-value { font-size: 14px; }
  .tcc-metric-card { padding: 8px 10px; }
  .tcc-h2 { font-size: 16px; }
  .tcc-table { min-width: 420px; }
}

/* ═══════════════════════════
   AI SUMMARY WIDGET
═══════════════════════════ */
.tcc-ai-widget {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-wrap: wrap;
  gap: 14px;
  margin: 0 0 24px 0;
  padding: 14px 20px;
  background: #f8f4ff;
  border-radius: 10px;
  border: 1px solid #e0d0f5;
}
.tcc-ai-text {
  font-size: 14px;
  font-weight: 700;
  color: #14142B;
}
.tcc-ai-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
  border: none;
  transition: transform 0.15s ease;
}
.tcc-ai-link:hover { transform: translateY(-2px); }
.tcc-ai-icon {
  height: 28px;
  width: 28px;
  object-fit: contain;
  display: block;
}

/* ═══════════════════════════
   CONTENT IMAGES
═══════════════════════════ */
.tcc-content-img {
  width: 100%;
  border-radius: 10px;
  margin: 16px 0 20px 0;
  display: block;
  object-fit: cover;
  max-height: 320px;
}
/* ═══════════════════════════
   BLOCKQUOTE / PULL QUOTE
═══════════════════════════ */
.tcc-blockquote {
  background: #fdf2f8;
  border-left: 4px solid #f542b0;
  border-radius: 0 10px 10px 0;
  padding: 16px 20px;
  margin: 20px 0;
  font-size: 15px;
  font-style: italic;
  color: #334155;
  line-height: 1.7;
}
.tcc-blockquote::before {
  content: '\201C';
  font-size: 32px;
  color: #f542b0;
  font-style: normal;
  line-height: 0;
  vertical-align: -10px;
  margin-right: 4px;
}

/* ═══════════════════════════
   SHIFT / CONCEPT CARDS GRID
   (2x2 or 2x3 named-concept grids)
═══════════════════════════ */
.tcc-shift-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin: 16px 0 24px 0;
}
.tcc-shift-card {
  background: linear-gradient(135deg, #14142B 0%, #2d1b4e 100%);
  border: 1px solid rgba(245,66,176,0.25);
  border-radius: 10px;
  padding: 16px 18px;
  transition: border-color 0.2s;
}
.tcc-shift-card:hover { border-color: rgba(245,66,176,0.6); }
.tcc-shift-title {
  font-size: 13px;
  font-weight: 800;
  color: #f542b0;
  margin: 0 0 6px 0;
  letter-spacing: 0.2px;
}
.tcc-shift-desc {
  font-size: 12px;
  color: #c0b8d0;
  line-height: 1.6;
  margin: 0;
}
@media (max-width: 580px) {
  .tcc-shift-grid { grid-template-columns: 1fr; }
}

/* ═══════════════════════════
   AUTHOR BIO BOX
═══════════════════════════ */
.tcc-author-box {
  display: flex;
  gap: 16px;
  align-items: flex-start;
  background: #fafafa;
  border: 1px solid #f0e0fa;
  border-radius: 12px;
  padding: 20px 22px;
  margin: 32px 0 24px 0;
}
.tcc-author-avatar {
  font-size: 32px;
  background: linear-gradient(135deg, #14142B, #2d1b4e);
  width: 56px;
  height: 56px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.tcc-author-info { flex: 1; }
.tcc-author-name {
  font-size: 15px;
  font-weight: 800;
  color: #14142B;
  margin: 0 0 5px 0;
}
.tcc-author-bio {
  font-size: 13px;
  color: #64748b;
  line-height: 1.6;
  margin: 0;
}
@media (max-width: 580px) {
  .tcc-author-box { flex-direction: column; align-items: center; text-align: center; }
}

</style>"""



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
6. Wrap any emoji-led callout text (e.g. "🎯 The Barter Model:", "📊 Shifting Benchmark:") as .tcc-callout boxes. Use tcc-cb-pk for 🎯, tcc-cb-bl for 📊/💡, tcc-cb-gn for ✅, tcc-cb-yw for ⚠️.
7. Build the FAQ section using .tcc-faq-item accordion markup.
8. Add a bar chart if the article has ranked numeric data (salary levels, percentages, etc.).
9. Use horizontal bars (.tcc-hbar) for city or comparison data with percentage widths.
10. Use .tcc-co-grid for company comparisons, .tcc-factor-grid for factor/reason lists.
11. Add 2-3 category tags in the hero banner after the subtitle.
12. Preserve any citation reference tags like [LINK: X] (e.g. [LINK: 1], [LINK: 2]) exactly as they are in the text. Do NOT modify them or remove them; they will be resolved post-generation.
13. For any pull-quote or standalone quote from the article (text in quotation marks on its own line), wrap it in a BLOCKQUOTE element:
    <blockquote class="tcc-blockquote">"Quote text here."</blockquote>
14. For any section that lists a 2x2 or 2x3 grid of named concepts with descriptions (e.g. "Destination → Mindset", "Seeking, Not Waiting"), render them as a SHIFT CARD GRID:
    <div class="tcc-shift-grid">
      <div class="tcc-shift-card">
        <p class="tcc-shift-title">Card Title</p>
        <p class="tcc-shift-desc">Card description text.</p>
      </div>
    </div>
15. At the very end of the article body (before FAQ), add an AUTHOR BIO BOX:
    <div class="tcc-author-box">
      <div class="tcc-author-avatar">✍️</div>
      <div class="tcc-author-info">
        <p class="tcc-author-name">The Crazy Careers Team</p>
        <p class="tcc-author-bio">The Crazy Careers is India's career guidance platform for students and early professionals — helping you navigate education, careers, and the future of work.</p>
      </div>
    </div>
16. End the article content with a "Final Thoughts" H2 section that is empowering, reflective, and optimistic.

OUTPUT: Output ONLY the raw HTML block described above, starting with <div class="tcc-wrap"> and ending with </div>.
No explanation. No markdown fences. No <html>/<head>/<body>/<style> tags.
"""


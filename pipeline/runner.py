"""
Pipeline Runner — chains all 5 Gemini steps for content generation.

Each step's output feeds into the next:
  Step 1 (Keywords) → Step 2 (SERP) → Step 3 (Outline) → Step 4 (Article) → Step 5 (HTML)

Reports progress via pipeline.status so the frontend can show real-time updates.
The final HTML is ready to paste into Elementor.
"""

import html
import os
import time
import traceback
import threading
from datetime import datetime
from pipeline.gemini_client import call_gemini
from pipeline.groq_client import call_groq
from pipeline.status import update_step, complete_job, fail_job, cleanup_job
from prompts.step1_keywords import build_step1_prompt
from prompts.step2_serp import build_step2_prompt
from prompts.step3_outline import build_step3_prompt
from prompts.step4_article import build_step4_prompt
from prompts.step5_html import build_step5_prompt, get_reference_css
from services.news_service import fetch_recent_news


def run_pipeline(topic: str, job_id: str = None, meta: dict = None) -> dict:
    """
    Runs all 5 Gemini steps for a given topic.
    Returns a dict with each step's output and the final HTML.
    
    Uses gemini-3.5-flash for all steps (proven to work on free tier).
    Step 4 uses higher temperature + tokens for better article quality.
    
    Args:
        topic: The trending topic to generate content for.
        job_id: Optional job ID for status tracking. If provided,
                pipeline progress is reported to pipeline.status.
    
    Returns:
        Dict with each step's output. Contains 'error' key on failure.
    """
    print(f"[Pipeline] Starting for topic: {topic}")
    result = {"topic": topic, "started_at": datetime.now().isoformat()}

    try:
        # Step 1 — Keyword Research
        if job_id:
            update_step(job_id, 1, "running")
        print("[Step 1] Keyword Research...")
        step1 = call_groq(
            prompt=build_step1_prompt(topic),
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            max_tokens=2048,
        )
        result["step1_keywords"] = step1
        if job_id:
            update_step(job_id, 1, "complete", chars=len(step1))
        print(f"[Step 1] Complete — {len(step1)} chars")

        # Step 2 — SERP & Competitor Analysis
        if job_id:
            update_step(job_id, 2, "running")
        print("[Step 2] SERP Analysis...")
        step2 = call_groq(
            prompt=build_step2_prompt(step1),
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            max_tokens=3000,
        )
        result["step2_serp"] = step2
        if job_id:
            update_step(job_id, 2, "complete", chars=len(step2))
        print(f"[Step 2] Complete — {len(step2)} chars")

        # Step 3 — Content Outline
        if job_id:
            update_step(job_id, 3, "running")
        print("[Step 3] Content Outline...")
        step3 = call_groq(
            prompt=build_step3_prompt(step1, step2),
            model="llama-3.3-70b-versatile",
            temperature=0.4,
            max_tokens=2048,
        )
        result["step3_outline"] = step3
        if job_id:
            update_step(job_id, 3, "complete", chars=len(step3))
        print(f"[Step 3] Complete — {len(step3)} chars")

        # Step 4 — Full Article + FAQ + Schema (higher temp + tokens for quality)
        if job_id:
            update_step(job_id, 4, "running")
        print("[Step 4] Writing Article + FAQ + Schema...")
        
        news_context = fetch_recent_news(topic)
        print(f"[Step 4] Fetched recent news for context.")
        
        step4 = call_groq(
            prompt=build_step4_prompt(step3, meta=meta, news_context=news_context),
            model="llama-3.3-70b-versatile",
            temperature=0.6,
            max_tokens=6000,
        )
        result["step4_article"] = step4
        if job_id:
            update_step(job_id, 4, "complete", chars=len(step4))
        print(f"[Step 4] Complete — {len(step4)} chars")

        # Step 5 — Full standalone HTML page
        # Using Groq instead of Gemini due to rate limits
        if job_id:
            update_step(job_id, 5, "running")
        print("[Step 5] Generating HTML content block...")
        step5_raw = call_groq(
            prompt=build_step5_prompt(step4, meta=meta),
            model="llama-3.3-70b-versatile",
            temperature=0.2,
            max_tokens=5000,
        )
        print(f"[Step 5] Content block complete — {len(step5_raw)} chars")

        # Wrap the content block into a complete standalone HTML page
        print("[Step 5] Wrapping with reference CSS into standalone HTML file...")
        css_block = get_reference_css()
        # PIPE-06: Escape topic for safe use inside HTML attribute (title tag)
        # html.escape handles <, >, &, ", ' — safe to inject into <title>
        safe_title = html.escape(topic)
        step5 = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{safe_title} | The Crazy Careers</title>
  {css_block}
</head>
<body>
{step5_raw}
<script>
  document.querySelectorAll('.tcc-faq-q').forEach(function(q) {{
    q.addEventListener('click', function() {{
      this.closest('.tcc-faq-item').classList.toggle('open');
    }});
  }});
</script>
</body>
</html>"""

        result["step5_html"] = step5
        if job_id:
            update_step(job_id, 5, "complete", chars=len(step5))
        print(f"[Step 5] Complete — {len(step5)} chars total")

        result["completed_at"] = datetime.now().isoformat()
        if job_id:
            complete_job(job_id)
            # CRASH-05: Schedule cleanup to free memory after 1 hour
            _schedule_cleanup(job_id, delay_seconds=3600)
        print(f"[Pipeline] Complete for topic: {topic}")

    except Exception as e:
        error_msg = str(e)
        print(f"[Pipeline] ERROR: {traceback.format_exc()}")
        result["error"] = error_msg

        if job_id:
            # Figure out which step failed
            failed_step = None
            for i in range(1, 6):
                key = f"step{i}_" 
                if not any(k.startswith(key) for k in result.keys() if k != "topic"):
                    failed_step = i
                    break
            fail_job(job_id, error_msg, failed_step)

    # Save output to file as fallback (in case email fails)
    _save_output(topic, result)

    if job_id and "error" in result:
        # CRASH-05: Also schedule cleanup on failure
        _schedule_cleanup(job_id, delay_seconds=3600)

    return result


def _schedule_cleanup(job_id: str, delay_seconds: int = 3600):
    """CRASH-05: Remove job from memory after delay_seconds to prevent unbounded growth."""
    def _cleanup():
        time.sleep(delay_seconds)
        cleanup_job(job_id)
        print(f"[Pipeline] Job {job_id} cleaned up from memory.")
    t = threading.Thread(target=_cleanup, daemon=True)
    t.start()


def _save_output(topic: str, result: dict):
    """Save the final HTML page to the output/ directory as a local backup."""
    try:
        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
        os.makedirs(output_dir, exist_ok=True)

        # Sanitize topic for filename
        safe_name = "".join(c if c.isalnum() or c in " -_" else "" for c in topic)
        safe_name = safe_name.strip().replace(" ", "_")[:60]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save the complete HTML page
        if "step5_html" in result:
            html_path = os.path.join(output_dir, f"{safe_name}_{timestamp}.html")
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(result["step5_html"])
            print(f"[Pipeline] HTML saved to: {html_path}")

    except Exception as e:
        print(f"[Pipeline] Warning: Could not save output file: {e}")

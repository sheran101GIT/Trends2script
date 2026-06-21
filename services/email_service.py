import os
import html
import urllib.parse
from datetime import datetime
import smtplib
import uuid
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.utils import formatdate, make_msgid

# ── SMTP configuration ───────────────────────────────────────────────────────
_SMTP_HOST    = "smtp.gmail.com"
_SMTP_PORT    = 587
_SMTP_TIMEOUT = 30  # CRASH-03: prevent thread hanging forever on slow SMTP


def _get_smtp_creds() -> tuple[str, str] | tuple[None, None]:
    """Return (sender_email, sender_password) from env, or (None, None) if missing."""
    return os.getenv("SENDER_EMAIL"), os.getenv("SENDER_PASSWORD")


def send_trends_email(trends_data, base_url, receiver_email: str) -> bool:
    """
    Sends an email with the trending topics and a button to generate content.
    receiver_email is passed in per-user rather than read from .env.
    """
    sender_email, sender_password = _get_smtp_creds()

    if not sender_email or not sender_password:
        print("[Email] SENDER_EMAIL / SENDER_PASSWORD missing in .env")
        return False

    if not receiver_email:
        print("[Email] No receiver email configured for this user.")
        return False

    msg = MIMEMultipart("alternative")
    today = datetime.now().strftime("%d %b %Y")
    msg['Subject']    = f"📈 Trending Topics – {today} | Trend to Script"
    msg['From']       = f"Trend To Script <{sender_email}>"
    msg['To']         = receiver_email
    msg['Date']       = formatdate(localtime=True)
    msg['Message-ID'] = make_msgid(domain="trendtoscript.com")
    msg.add_header("Reply-To", sender_email)

    text_body = f"Today's Top Trends ({today})\n\nHere are the AI-curated trending topics for today. Go to the dashboard to generate content."
    msg.attach(MIMEText(text_body, "plain"))

    html_body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333; background:#f8f9fa; margin:0; padding:0;">
        <div style="max-width:680px; margin:32px auto; background:#fff; border-radius:12px; overflow:hidden; box-shadow:0 4px 24px rgba(0,0,0,.08);">
          <div style="background:linear-gradient(135deg,#6366F1,#EC4899); padding:32px 36px;">
            <h1 style="color:#fff; margin:0; font-size:24px; font-weight:800;">📈 Today's Top Trends</h1>
            <p style="color:rgba(255,255,255,.8); margin:6px 0 0; font-size:14px;">{html.escape(today)} — Powered by Trend to Script</p>
          </div>
          <div style="padding:28px 36px;">
            <p style="margin-bottom:20px; color:#555; font-size:15px;">Here are the AI-curated trending topics for today. Click <strong>Generate Content</strong> on any topic to kick off the 5-step content pipeline.</p>
            <hr style="border:none; border-top:1px solid #eee; margin-bottom:24px;">
    """

    for item in trends_data:
        # SEC-03: HTML-escape all user/API-sourced values before injecting into HTML
        topic       = html.escape(str(item.get("topic", "Unknown")))
        explanation = html.escape(str(item.get("explanation", "No explanation provided.")))
        traffic     = html.escape(str(item.get("traffic", "N/A")))
        category    = html.escape(str(item.get("category", "General")))

        encoded_topic = urllib.parse.quote(item.get("topic", ""))
        script_link   = f"{base_url}/generate_script?topic={encoded_topic}"

        html_body += f"""
        <div style="margin-bottom:22px; padding:20px; border:1px solid #e5e7eb; border-radius:10px; background:#fafafa;">
          <div style="display:flex; align-items:flex-start; gap:12px; flex-wrap:wrap;">
            <div style="flex:1; min-width:200px;">
              <h3 style="margin:0 0 4px; color:#1e1e2e; font-size:16px;">{topic}</h3>
              <span style="display:inline-block; padding:2px 10px; border-radius:20px; background:#EEF2FF; color:#6366F1; font-size:11px; font-weight:600; margin-bottom:10px;">{category}</span>
              <p style="margin:0 0 6px; font-size:13px; color:#555;"><strong>Traffic:</strong> {traffic}</p>
              <p style="margin:0; font-size:13px; color:#555; line-height:1.5;">{explanation}</p>
            </div>
          </div>
          <div style="margin-top:14px;">
            <a href="{script_link}" style="display:inline-block; padding:10px 20px; background:linear-gradient(135deg,#6366F1,#818CF8); color:#fff; text-decoration:none; border-radius:8px; font-size:13px; font-weight:600;">✨ Generate Content</a>
          </div>
        </div>
        """

    html_body += """
          </div>
          <div style="background:#f1f5f9; padding:18px 36px; text-align:center; border-top:1px solid #e5e7eb;">
            <p style="margin:0; font-size:12px; color:#94a3b8;">Automated by <strong>Trend to Script</strong> · You can update your notification email in your dashboard settings.</p>
          </div>
        </div>
      </body>
    </html>
    """

    msg.attach(MIMEText(html_body, "html"))

    try:
        # CRASH-03: Added timeout=_SMTP_TIMEOUT to prevent thread hang
        server = smtplib.SMTP(_SMTP_HOST, _SMTP_PORT, timeout=_SMTP_TIMEOUT)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print(f"[Email] Trends email sent to {receiver_email}")
        return True
    except smtplib.SMTPAuthenticationError:
        print("[Email] SMTP authentication failed — check SENDER_EMAIL / SENDER_PASSWORD")
        return False
    except Exception as e:
        print(f"[Email] Failed to send trends email: {type(e).__name__}")
        return False


def send_content_email(topic, html_body, receiver_email: str,
                       article_md=None, keywords_txt=None):
    """
    Legacy function — kept for backward compatibility.
    Sends the final generated content (HTML for Elementor) back to the user.
    """
    sender_email, sender_password = _get_smtp_creds()

    if not sender_email or not sender_password:
        print("[Content Email] SENDER_EMAIL / SENDER_PASSWORD missing in .env")
        return False

    if not receiver_email:
        print("[Content Email] No receiver email provided.")
        return False

    msg = MIMEMultipart("mixed")
    msg["Subject"]    = f"[TTS] Content Ready: {topic}"
    msg["From"]       = sender_email
    msg["To"]         = receiver_email
    msg["Message-ID"] = make_msgid(domain="trendtoscript.com")

    msg.attach(MIMEText(html_body or "", "html"))

    if article_md:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(article_md.encode("utf-8"))
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", 'attachment; filename="article_draft.md"')
        msg.attach(part)

    if keywords_txt:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(keywords_txt.encode("utf-8"))
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", 'attachment; filename="keywords.txt"')
        msg.attach(part)

    try:
        # CRASH-03: Added timeout
        server = smtplib.SMTP(_SMTP_HOST, _SMTP_PORT, timeout=_SMTP_TIMEOUT)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print(f"[Content Email] Sent content for '{topic}' to {receiver_email}")
        return True
    except smtplib.SMTPAuthenticationError:
        print("[Content Email] SMTP authentication failed")
        return False
    except Exception as e:
        print(f"[Content Email] Failed: {type(e).__name__}")
        return False


def send_html_file_email(topic: str, html_content: str, receiver_email: str) -> bool:
    """
    Sends the final generated page as a single self-contained .html file attachment.
    """
    sender_email, sender_password = _get_smtp_creds()

    if not sender_email or not sender_password:
        print("[HTML Email] SENDER_EMAIL / SENDER_PASSWORD missing in .env")
        return False

    if not receiver_email:
        print("[HTML Email] No receiver email provided.")
        return False

    # EMAIL-06 fix: Guard against None html_content
    if not html_content:
        print("[HTML Email] html_content is empty or None — cannot attach.")
        return False

    today = datetime.now().strftime("%d %b %Y")

    # Build a clean filename from the topic
    safe_name = "".join(c if c.isalnum() or c in " -_" else "" for c in topic)
    safe_name = safe_name.strip().replace(" ", "_")[:60]
    filename  = f"{safe_name}.html"

    # SEC-03: Escape topic for use inside HTML body
    safe_topic    = html.escape(topic)
    safe_filename = html.escape(filename)

    msg = MIMEMultipart("mixed")
    msg["Subject"]    = f"[TTS] Article Ready: {topic}"
    msg["From"]       = f"Trend To Script <{sender_email}>"
    msg["To"]         = receiver_email
    msg["Date"]       = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid(domain="trendtoscript.com")
    msg.add_header("Reply-To", sender_email)

    # ── Notification body (plain text & HTML) ──────────────────────────────────
    body_part = MIMEMultipart("alternative")

    text_body = f"""Your Article Is Ready
{today} — Powered by Trend to Script

Your content pipeline has finished for: {topic}

The complete article is attached as {filename}. Open it in any browser to see the fully styled web page.

Automated by Trend to Script
"""
    body_part.attach(MIMEText(text_body, "plain"))

    email_body = f"""
    <html>
      <body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
                   color:#334155;background:#f8f9fa;margin:0;padding:0;">
        <div style="max-width:600px;margin:32px auto;background:#fff;border-radius:14px;
                    overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,.08);">

          <!-- Header -->
          <div style="background:linear-gradient(135deg,#14142B 0%,#2d1b4e 55%,#1a0a2e 100%);
                      padding:28px 32px;">
            <h1 style="color:#fff;margin:0;font-size:20px;font-weight:800;">
              ✅ Your Article Is Ready
            </h1>
            <p style="color:rgba(255,255,255,.7);margin:6px 0 0;font-size:13px;">
              {html.escape(today)} — Powered by Trend to Script
            </p>
          </div>

          <!-- Body -->
          <div style="padding:28px 32px;">
            <p style="margin:0 0 14px;font-size:15px;color:#334155;">
              Your content pipeline has finished for:
            </p>
            <p style="margin:0 0 20px;font-size:17px;font-weight:700;color:#14142B;">
              {safe_topic}
            </p>
            <p style="margin:0 0 20px;font-size:14px;color:#64748b;line-height:1.6;">
              The complete article is attached as <strong>{safe_filename}</strong>.
              Open it in any browser to see the fully styled web page — ready to copy
              into your CMS or publish directly.
            </p>
            <div style="background:#fdf2f8;border-left:4px solid #f542b0;
                        border-radius:6px;padding:14px 18px;margin-bottom:20px;">
              <p style="margin:0;font-size:13px;color:#334155;">
                💡 <strong>Tip:</strong> Open the <code>.html</code> file in Chrome or Firefox,
                then use <em>File → Save Page As</em> if you need a local copy, or copy the
                source code directly into your WordPress / Elementor custom HTML widget.
              </p>
            </div>
          </div>

          <!-- Footer -->
          <div style="background:#f1f5f9;padding:16px 32px;border-top:1px solid #e5e7eb;
                      text-align:center;">
            <p style="margin:0;font-size:12px;color:#94a3b8;">
              Automated by <strong>Trend to Script</strong> ·
              You can update your notification email in your dashboard settings.
            </p>
          </div>
        </div>
      </body>
    </html>
    """

    body_part.attach(MIMEText(email_body, "html"))
    msg.attach(body_part)

    # ── HTML file attachment ─────────────────────────────────────────────────
    attachment = MIMEBase("text", "html")
    attachment.set_payload(html_content.encode("utf-8"))
    encoders.encode_base64(attachment)
    attachment.add_header(
        "Content-Disposition",
        f'attachment; filename="{filename}"'
    )
    msg.attach(attachment)

    try:
        # CRASH-03: Added timeout
        server = smtplib.SMTP(_SMTP_HOST, _SMTP_PORT, timeout=_SMTP_TIMEOUT)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print(f"[HTML Email] Sent '{filename}' to {receiver_email}")
        return True
    except smtplib.SMTPAuthenticationError:
        print("[HTML Email] SMTP authentication failed")
        return False
    except Exception as e:
        print(f"[HTML Email] Failed: {type(e).__name__}")
        return False

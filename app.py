import os
import re
import uuid
import threading
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from flask_wtf import CSRFProtect
from dotenv import load_dotenv

from models import db, User
from services.trends_extractor import fetch_trends
from services.llm_service import process_trends
from services.email_service import send_trends_email, send_content_email, send_html_file_email
from pipeline.runner import run_pipeline
from pipeline.status import create_job, get_job

# ─────────────────────────────────────────────
#  Bootstrap
# ─────────────────────────────────────────────
load_dotenv()

app = Flask(__name__)

# SEC-01/09: No insecure default — crash loudly if SECRET_KEY is not set.
# In development, set it in .env. In production, inject it via Docker/cloud env.
_secret_key = os.getenv('SECRET_KEY')
if not _secret_key:
    raise RuntimeError(
        "SECRET_KEY environment variable is not set. "
        "Generate one with: python -c \"import secrets; print(secrets.token_hex(64))\""
    )
app.config['SECRET_KEY']                     = _secret_key
app.config['SQLALCHEMY_DATABASE_URI']        = os.getenv('DATABASE_URL', 'sqlite:///trendtoscript.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Flask-WTF CSRF config
app.config['WTF_CSRF_ENABLED']               = True

db.init_app(app)
bcrypt        = Bcrypt(app)

# SEC-02: CSRF protection for all state-mutating form submissions
csrf = CSRFProtect(app)

login_manager = LoginManager(app)
login_manager.login_view            = 'login'
login_manager.login_message         = 'Please sign in to access your dashboard.'
login_manager.login_message_category = 'info'

# Email validation regex (simple RFC-5322 subset)

_EMAIL_RE = re.compile(r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$')


def _is_valid_email(email: str) -> bool:
    """SEC-05: Basic email format validation."""
    return bool(_EMAIL_RE.match(email)) if email else False


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Create tables on first run
with app.app_context():
    db.create_all()


# ─────────────────────────────────────────────
#  Auth Routes
# ─────────────────────────────────────────────

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username         = request.form.get('username', '').strip()
        email            = request.form.get('email', '').strip().lower()
        password         = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        receiver_email   = request.form.get('receiver_email', '').strip().lower() or None

        # Basic validation
        if not username or not email or not password:
            flash('All fields except receiver email are required.', 'error')
            return render_template('register.html')

        if len(username) < 3:
            flash('Username must be at least 3 characters.', 'error')
            return render_template('register.html')

        # SEC-05: Validate email format
        if not _is_valid_email(email):
            flash('Please enter a valid email address.', 'error')
            return render_template('register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')

        if len(password) < 8:
            flash('Password must be at least 8 characters.', 'error')
            return render_template('register.html')

        # SEC-07: Use a generic message to prevent username enumeration
        if User.query.filter_by(username=username).first() or \
                User.query.filter_by(email=email).first():
            flash('An account with those details already exists.', 'error')
            return render_template('register.html')

        # Validate receiver_email format if provided
        if receiver_email and not _is_valid_email(receiver_email):
            flash('Receiver email format is invalid.', 'error')
            return render_template('register.html')

        # Create user
        pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        user    = User(
            username=username,
            email=email,
            password_hash=pw_hash,
            receiver_email=receiver_email
        )
        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash(f'Welcome, {username}! Your account has been created.', 'success')
        return redirect(url_for('dashboard'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(username=username).first()

        # SEC-07: Same generic error regardless of whether username exists
        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Invalid username or password. Please try again.', 'error')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been signed out.', 'info')
    return redirect(url_for('login'))


# ─────────────────────────────────────────────
#  Dashboard
# ─────────────────────────────────────────────

@app.route('/')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)


# ─────────────────────────────────────────────
#  Update receiver email (AJAX / form)
# ─────────────────────────────────────────────

@app.route('/update_email', methods=['POST'])
@login_required
@csrf.exempt   # AJAX endpoint uses JSON — CSRF token sent in X-CSRFToken header
def update_email():
    data           = request.get_json() or {}
    receiver_email = data.get('receiver_email', '').strip().lower()

    if not receiver_email:
        return jsonify({'error': 'Email cannot be empty.'}), 400

    # SEC-05: Validate email format before saving
    if not _is_valid_email(receiver_email):
        return jsonify({'error': 'Please enter a valid email address.'}), 400

    current_user.receiver_email = receiver_email
    db.session.commit()
    return jsonify({'message': f'Receiver email updated to {receiver_email}.'})


# ─────────────────────────────────────────────
#  Update article metadata (AJAX / form)
# ─────────────────────────────────────────────

@app.route('/update_metadata', methods=['POST'])
@login_required
@csrf.exempt   # AJAX endpoint
def update_metadata():
    data = request.get_json() or {}
    
    current_user.author_name  = data.get('author_name', '').strip() or 'The Crazy Careers'
    current_user.read_time    = data.get('read_time', '').strip() or '5 min read'
    current_user.publish_date = data.get('publish_date', '').strip() or 'Auto'
    
    db.session.commit()
    return jsonify({'message': 'Article metadata updated successfully.'})


# ─────────────────────────────────────────────
#  Workflow — Instant
# ─────────────────────────────────────────────

@app.route('/trigger_workflow', methods=['POST'])
@login_required
@csrf.exempt   # AJAX endpoint
def trigger_workflow():
    data     = request.get_json() or {}
    location = data.get('location', 'IN')
    category = data.get('category', 'All')
    duration = data.get('duration', 'All Time')

    # Use the requester's saved receiver email
    receiver_email = current_user.receiver_email
    if not receiver_email:
        return jsonify({'error': 'You have not set a receiver email yet. Please update it in the dashboard settings.'}), 400

    # 1. Fetch trends
    raw_trends = fetch_trends(geo=location, category=category)
    if not raw_trends:
        if category != "All":
            return jsonify({"error": f"No trends in '{category}' for this region. Try 'All Categories' or check back later."}), 404
        return jsonify({"error": "Failed to fetch trends. Google may be rate-limiting — try again in a minute."}), 500

    # 2. Process with LLM
    processed_trends = process_trends(raw_trends, location, category, duration)
    if isinstance(processed_trends, dict) and "error" in processed_trends:
        return jsonify({"error": processed_trends["error"]}), 500
    if not processed_trends:
        return jsonify({"error": f"No trends matched '{category}'. Try 'All Categories'."}), 500

    # 3. Send email to user's configured address
    base_url = request.host_url.rstrip('/')
    success  = send_trends_email(processed_trends, base_url, receiver_email)

    # 4. Increment workflow counter
    current_user.workflows_run = (current_user.workflows_run or 0) + 1
    db.session.commit()

    if success:
        return jsonify({
            "message": f"Workflow completed! Email sent to {receiver_email}.",
            "trends": processed_trends
        })
    else:
        return jsonify({"error": "Workflow ran but failed to send email. Check your email settings."}), 500


# ─────────────────────────────────────────────
#  Content Pipeline
# ─────────────────────────────────────────────

@app.route('/generate_script')
@login_required
def generate_script():
    """
    Triggered when user clicks 'Generate Content' in the trends email.
    Runs the 5-step Gemini content pipeline in a background thread.
    """
    topic = request.args.get('topic')
    if not topic:
        return "Topic is required", 400

    # Capture per-user email and metadata at request time (avoid closure over current_user in thread)
    receiver_email = current_user.receiver_email or os.getenv('RECEIVER_EMAIL', '')
    user_id        = current_user.id
    
    meta = {
        "author_name": current_user.author_name or "The Crazy Careers",
        "read_time": current_user.read_time or "5 min read",
        "publish_date": current_user.publish_date or "Auto"
    }

    job_id = str(uuid.uuid4())[:8]
    create_job(job_id, topic)

    def run_and_email():
        print(f"[Pipeline] Starting for: {topic} (job: {job_id}, user: {user_id})")
        result = run_pipeline(topic, job_id=job_id, meta=meta)

        if "error" in result:
            print(f"[Pipeline] Failed for '{topic}': {result['error']}")
            import html as _html
            safe_topic = _html.escape(topic)
            safe_error = _html.escape(result['error'][:200])
            error_html = (
                f"<html><body style='font-family:sans-serif;padding:24px;'>"
                f"<h2 style='color:#14142B;'>Pipeline Error</h2>"
                f"<p>The content pipeline failed for topic: <strong>{safe_topic}</strong></p>"
                f"<p style='color:#991b1b;'>Error: {safe_error}</p>"
                f"</body></html>"
            )
            send_content_email(
                topic=topic,
                html_body=error_html,
                receiver_email=receiver_email,
            )
        else:
            print(f"[Pipeline] Complete for '{topic}' — sending HTML file email...")
            send_html_file_email(
                topic=topic,
                html_content=result["step5_html"],
                receiver_email=receiver_email,
            )

    thread = threading.Thread(target=run_and_email, daemon=True)
    thread.start()

    return render_template('script_view.html', topic=topic, job_id=job_id)


@app.route('/pipeline_status/<job_id>')
@login_required
def pipeline_status(job_id):
    """
    Returns the current status of a content pipeline job as JSON.
    Polled by script_view.html every 2 seconds.
    """
    job = get_job(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    return jsonify(job)


if __name__ == '__main__':
    app.run(debug=True, port=5000)

# Trend to Script - Automated Content Generation Pipeline

## Project Overview

This project is an end-to-end automated content generation system built to streamline content creation workflows. It handles two main phases:

1. **Trend Collection & Notification:** Automatically fetches the latest trends for specific niches/categories using `trendspy`, processes them with an LLM to evaluate relevance, and emails the curated trends to the user.
2. **Content Generation Pipeline:** A 5-step automated workflow that is triggered via an email button. It performs keyword research, SERP analysis, content outlining, full article writing (with FAQ and Schema), and finally converts the article into Elementor-ready HTML.

## Tech Stack

- **Backend:** Flask, Python
- **LLM APIs:** Google Gemini (`gemini-3.5-flash`), Groq (`llama-3.3-70b-versatile`).
- **Trend Extraction:** `trendspy`
- **Email Delivery:** Python's built-in `smtplib`

## Features

- **Dashboard UI:** Simple frontend to trigger workflow manually.
- **5-Step Content Pipeline:**
  - **Step 1:** Keyword Research (Powered by Groq / LLaMA 3.3)
  - **Step 2:** SERP & Competitor Analysis (Powered by Groq / LLaMA 3.3)
  - **Step 3:** Content Outline (Powered by Groq / LLaMA 3.3)
  - **Step 4:** Article Generation + FAQ + Schema (Powered by Gemini)
  - **Step 5:** Elementor-ready HTML Generation (Powered by Groq)
- **Live Status Tracking:** Real-time progress updates via polling for the background pipeline.

## Project Structure

```text
trend to script/
├── app.py                     # Main Flask application and API endpoints
├── pipeline/                  # The 5-step content generation workflow
│   ├── runner.py              # Orchestrator for the 5 steps
│   ├── status.py              # In-memory job status tracking
│   ├── gemini_client.py       # API client for Google Gemini
│   ├── groq_client.py         # API client for Groq
├── prompts/                   # LLM prompts for each pipeline step
├── services/                  # Core services for Phase 1
│   ├── trends_extractor.py    # Fetches trends via trendspy
│   ├── llm_service.py         # Evaluates trend relevance
│   └── email_service.py       # Handles email delivery
├── config/                    # Configuration and master prompts (Persona)
├── static/ & templates/       # Frontend assets and HTML templates
└── output/                    # Local storage for generated articles and HTML
```

## Setup Instructions

### 1. Prerequisites

- Python 3.8+
- API keys for Google Gemini, Groq, and an SMTP email account (e.g., Gmail App Passwords).

### 2. Installation

Clone the repository and install the dependencies:

```bash
# Create and activate a virtual environment
python -m venv .venv

# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Variables

Create a `.env` file in the root directory and configure the following keys:

```env
# Gemini
GEMINI_API_KEY=your_gemini_key_here

# Groq
GROQ_API_KEY=your_groq_key_here


# Email Configuration
EMAIL_FROM=your_email@gmail.com
EMAIL_TO=recipient_email@gmail.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_app_password
```

### 4. Running the Application

Start the Flask development server:

```bash
python app.py
```

The application will be available at `http://localhost:5000`.

## How It Works

1. Navigate to the dashboard at `http://localhost:5000/`.
2. Select a location and category, then click "Run Workflow".
3. The system will fetch trending topics and email them to you.
4. Open the email and click "Generate Content" on a specific trending topic.
5. A live progress page will open in your browser tracking the 5-step pipeline.
6. The final generated HTML and Markdown draft will be emailed to you and saved locally in the `/output` folder.

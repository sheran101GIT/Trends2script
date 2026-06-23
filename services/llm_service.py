import os
from google import genai
from google.genai import types

def get_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        raise ValueError("Valid GEMINI_API_KEY is required in .env file.")
    return genai.Client(api_key=api_key)

import time
import json
from datetime import datetime, timezone, timedelta
from dateutil import parser
from services.rate_limiter import wait_for_slot

def generate_with_retry(client, prompt, max_retries=5, initial_delay=5):
    """Helper function to retry Gemini API calls on failure (e.g. 503 Unavailable, 429 Quota)"""
    delay = initial_delay
    for attempt in range(max_retries):
        try:
            # Wait for rate limiter slot before calling API
            waited = wait_for_slot()
            if waited > 0:
                print(f"[LLM Service] Rate limiter held for {waited:.1f}s")

            # Use gemini-2.0-flash with thinking_budget=0 to disable thinking mode.
            # Thinking mode consumes output tokens on hidden reasoning, which can truncate
            # the actual JSON response. Disabling it gives full output budget to the response.
            return client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_budget=0)
                )
            )
        except Exception as e:
            error_str = str(e)
            print(f"API Attempt {attempt + 1} failed: {error_str}")
            if attempt == max_retries - 1:
                raise e
            # If it's a 503 or 429, wait and retry
            if "503" in error_str or "429" in error_str or "UNAVAILABLE" in error_str or "quota" in error_str.lower():
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
                delay = min(delay * 2, 60) # Exponential backoff with cap
            else:
                # For other errors like ValueError for missing API key, fail immediately
                raise e

def process_trends(trends_list, location="IN", category="All", duration="All Time"):
    """
    Takes a list of generic trends and asks Gemini to identify up to 10 
    that are most related to the specific category.
    It also generates a brief explanation for why each is trending.
    Returns a list of dicts: [{'topic': '...', 'traffic': '...', 'explanation': '...', 'category': '...'}]
    """
    if not trends_list:
        return []
        
    try:
        client = get_client()
        
        # Filter by duration if specified
        filtered_trends = []
        now = datetime.now(timezone.utc)
        
        duration_hours = None
        if duration == "Past 4 Hours":
            duration_hours = 4
        elif duration == "Past 24 Hours":
            duration_hours = 24
        elif duration == "Past 48 Hours":
            duration_hours = 48
            
        for t in trends_list:
            if duration_hours and t.get('published'):
                try:
                    pub_date = parser.parse(t['published'])
                    if (now - pub_date) <= timedelta(hours=duration_hours):
                        filtered_trends.append(t)
                except Exception:
                    filtered_trends.append(t) # Keep if parsing fails just in case
            else:
                filtered_trends.append(t)
                
        if not filtered_trends:
            print("No trends found after filtering by duration.")
            return []
        
        print(f"[DEBUG] Sending {len(filtered_trends)} trends to LLM for processing...")
        
        # Format the trends for the prompt
        trends_str = "\n".join([f"{i+1}. {t['topic']} (Traffic: {t['traffic']}, Published: {t.get('published', 'N/A')})" for i, t in enumerate(filtered_trends)])
        
        category_instruction = (
            f'most relevant to the category: "{category}". '
            f'If "{category}" is "All", return ALL top trends overall — do not skip any.'
        )

        strict_filter_rule = (
            ""
            if category == "All"
            else (
                f'STRICT EXCLUSION RULE: A trend qualifies for the "{category}" category ONLY IF '
                f'the PRIMARY and CORE reason it is trending is directly about "{category}" itself. '
                f'Ask yourself: "Is this trend fundamentally a {category} topic?" — if the answer is NO, EXCLUDE it. '
                f'Specifically, EXCLUDE any trend where "{category}" is only a secondary or incidental element, '
                f'such as when a {category}-related word appears in a news story that is actually about '
                f'politics, government, law, crime, sports, business, health, celebrity gossip, or any other domain. '
                f'The trend\'s main subject must live squarely inside the "{category}" category — '
                f'not just reference it from the outside.'
            )
        )

        prompt = f"""
Here is a list of {len(filtered_trends)} daily search trends in {location}:
{trends_str}

Your task:
1. Select up to 10 trends that are {category_instruction}
2. {strict_filter_rule}
3. For EVERY selected trend, write a brief 1-2 sentence explanation of WHY it is trending today.
4. You MUST return EXACTLY a valid JSON array — no markdown, no text outside the array.
   Each element must have these exact keys:
   - "topic": the exact trend name from the list above
   - "traffic": the traffic value shown (or "N/A" if missing)
   - "explanation": your 1-2 sentence reason
   - "category": the category label you assigned
   - "timestamp": the timestamp of the trend in HH:MM AM/PM format

IMPORTANT: 1.Return ALL selected items in ONE complete JSON array. Do not truncate or summarize.
Example format:
[{{"topic": "...", "traffic": "...", "explanation": "...", "category": "...", "timestamp": "..."}}, ...]
2. Return all the 10 trending suggestions even if there are more than 10 in the list.
"""
        response = generate_with_retry(client, prompt)
        
        # Parse JSON from the response
        text = response.text.strip()
        print(f"[DEBUG] Raw LLM response length: {len(text)} chars")
        
        # Clean up markdown code blocks if present
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        # Try direct parse first
        try:
            result = json.loads(text)
        except json.JSONDecodeError:
            # Fallback: extract array using regex in case there's surrounding text
            import re
            match = re.search(r'\[.*\]', text, re.DOTALL)
            if match:
                result = json.loads(match.group(0))
            else:
                raise ValueError(f"Could not find valid JSON array in response. Response was: {text[:300]}")

        print(f"[DEBUG] LLM returned {len(result)} processed trends.")
        return result
    except Exception as e:
        error_msg = str(e)
        print(f"[ERROR] in LLM processing trends: {error_msg}")
        # Return error info so the caller can show a meaningful message
        if "429" in error_msg or "quota" in error_msg.lower():
            return {"error": "Gemini API quota exceeded. Please wait a few minutes and try again."}
        elif "503" in error_msg or "UNAVAILABLE" in error_msg:
            return {"error": "Gemini API is temporarily overloaded. Please try again in 30-60 seconds."}
        else:
            return {"error": f"LLM processing failed: {error_msg[:200]}"}

def generate_content_script(topic):
    """
    Generates a YouTube/Reel/Post content script for the given topic.
    """
    try:
        client = get_client()
        
        prompt = f"""
You are an expert content creator. The topic "{topic}" is currently trending in India.
Write an engaging, short-form video script (e.g., for YouTube Shorts or Instagram Reels) or a post for the topic "{topic}" about this topic.

The script should include:
- A catchy Hook (first 3 seconds)
- The main body (explaining the context or news)
- A Call to Action (CTA) at the end.

Keep it dynamic, informative, and around 60 seconds of speaking time.
"""
        response = generate_with_retry(client, prompt)
        return response.text
    except Exception as e:
        print(f"Error generating script: {e}")
        return f"Could not generate script due to error: {e}"

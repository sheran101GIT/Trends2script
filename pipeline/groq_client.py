"""
Groq API wrapper for the content pipeline.
"""
import os
import time
from groq import Groq
from config.persona import MASTER_PERSONA
from services.rate_limiter import wait_for_slot

def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        raise ValueError("Valid GROQ_API_KEY is required in .env file.")
    return Groq(api_key=api_key)

def call_groq(
    prompt: str,
    model: str = "llama-3.3-70b-versatile",
    temperature: float = 0.4,
    max_tokens: int = 4096,
    max_retries: int = 5,
    initial_delay: int = 5,
) -> str:
    client = get_groq_client()
    delay = initial_delay

    for attempt in range(max_retries):
        try:
            waited = wait_for_slot()
            if waited > 0:
                print(f"[Pipeline Groq] Rate limiter held for {waited:.1f}s")

            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": MASTER_PERSONA},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )

            text = response.choices[0].message.content
            if not text or text.strip() == "":
                raise ValueError(f"Empty response from Groq on model={model}")

            return text

        except Exception as e:
            error_str = str(e)
            print(f"[Pipeline Groq] Attempt {attempt + 1}/{max_retries} failed: {error_str}")

            if attempt == max_retries - 1:
                raise

            if any(code in error_str.lower() for code in ["503", "429", "rate limit", "too many requests"]) or "quota" in error_str.lower():
                import re
                retry_match = None
                try:
                    retry_match = re.search(r'retry.*?(\d+\.?\d*)s', error_str.lower())
                except Exception:
                    pass
                
                if retry_match:
                    wait_time = max(float(retry_match.group(1)), delay)
                else:
                    wait_time = delay
                
                print(f"[Pipeline Groq] Rate limited. Retrying in {wait_time:.0f}s...")
                time.sleep(wait_time)
                delay = min(delay * 2, 60)
            else:
                raise

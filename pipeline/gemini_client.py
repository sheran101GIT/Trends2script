"""
Gemini API wrapper for the content pipeline.

Uses the google-genai SDK (already installed in this project).
Configured for gemini-3.5-flash with thinking disabled to avoid
output token budget being consumed by hidden reasoning.
Includes retry logic with exponential backoff for rate limits.
"""

import os
import time
from google import genai
from google.genai import types
from config.persona import MASTER_PERSONA
from services.rate_limiter import wait_for_slot


def get_client():
    """Returns a configured Gemini client."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        raise ValueError("Valid GEMINI_API_KEY is required in .env file.")
    return genai.Client(api_key=api_key)


def call_gemini(
    prompt: str,
    model: str = "gemini-3.5-flash",
    temperature: float = 0.4,
    max_tokens: int = 4096,
    max_retries: int = 5,
    initial_delay: int = 5,
) -> str:
    """
    Calls Gemini with the Master Persona as system instruction.
    Waits for a rate limiter slot before each attempt.
    Retries on 503/429 with exponential backoff.
    
    Uses thinking_budget=0 to disable thinking mode — this prevents
    the model from consuming output tokens on hidden reasoning, which
    can truncate the actual response.
    
    Args:
        prompt: The user prompt to send.
        model: Gemini model name (default: gemini-3.5-flash).
        temperature: Sampling temperature.
        max_tokens: Max output tokens.
        max_retries: Number of retry attempts on transient failures.
        initial_delay: Initial delay in seconds before first retry.
    
    Returns:
        The generated text response.
    """
    client = get_client()
    delay = initial_delay

    for attempt in range(max_retries):
        try:
            # Wait for rate limiter slot before calling API
            waited = wait_for_slot()
            if waited > 0:
                print(f"[Pipeline Gemini] Rate limiter held for {waited:.1f}s")

            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                    system_instruction=MASTER_PERSONA,
                    thinking_config=types.ThinkingConfig(thinking_budget=0),
                ),
            )

            text = response.text
            if not text or text.strip() == "":
                raise ValueError(f"Empty response from Gemini on model={model}")

            return text

        except Exception as e:
            error_str = str(e)
            print(f"[Pipeline Gemini] Attempt {attempt + 1}/{max_retries} failed: {error_str}")

            if attempt == max_retries - 1:
                raise

            # Retry on transient errors (rate limits, server overload)
            if any(code in error_str for code in ["503", "429", "UNAVAILABLE", "RESOURCE_EXHAUSTED"]) or "quota" in error_str.lower():
                # Parse retry delay from error if available
                retry_match = None
                try:
                    import re
                    retry_match = re.search(r'retry.*?(\d+\.?\d*)s', error_str.lower())
                except Exception:
                    pass
                
                if retry_match:
                    wait_time = max(float(retry_match.group(1)), delay)
                else:
                    wait_time = delay
                
                print(f"[Pipeline Gemini] Rate limited. Retrying in {wait_time:.0f}s...")
                time.sleep(wait_time)
                delay = min(delay * 2, 60)  # Cap at 60 seconds
            else:
                # Non-transient error — fail immediately
                raise

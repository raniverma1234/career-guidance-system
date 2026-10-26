"""
Step 12: optional AI model connection (Gemini or Claude).

Which one is used?
  - AI_PROVIDER=gemini  or  AI_PROVIDER=claude   in .env  -> that one (its key must be set)
  - not set -> GEMINI_API_KEY if present, otherwise ANTHROPIC_API_KEY
  - no key at all -> assistant uses its built-in rule-based answers

If the AI call fails for any reason, the caller falls back to the rule-based answer.
"""
import logging
import os
from dotenv import load_dotenv

load_dotenv()
log = logging.getLogger("assistant")

CLAUDE_DEFAULT = "claude-haiku-4-5-20251001"
GEMINI_DEFAULT = "gemini-2.5-flash"
GEMINI_BACKUP = "gemini-2.5-flash-lite"      # tried if the first Gemini model fails


def _env(name):
    return os.getenv(name, "").strip()


def provider():
    choice = _env("AI_PROVIDER").lower()
    if choice == "gemini":
        return "gemini" if _env("GEMINI_API_KEY") else None
    if choice == "claude":
        return "claude" if _env("ANTHROPIC_API_KEY") else None
    if _env("GEMINI_API_KEY"):
        return "gemini"
    if _env("ANTHROPIC_API_KEY"):
        return "claude"
    return None


def is_enabled():
    return provider() is not None


def model_name():
    p = provider()
    if p == "gemini":
        return _env("GEMINI_MODEL") or GEMINI_DEFAULT
    if p == "claude":
        return _env("ANTHROPIC_MODEL") or CLAUDE_DEFAULT
    return None


def _ask_gemini(system_prompt, history, message):
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=_env("GEMINI_API_KEY"))
    contents = []
    for m in history:
        role = "user" if m["role"] == "user" else "model"
        contents.append(types.Content(role=role, parts=[types.Part(text=m["content"])]))
    contents.append(types.Content(role="user", parts=[types.Part(text=message)]))

    # room for the model's own "thinking" tokens as well as the visible answer
    config = types.GenerateContentConfig(
        system_instruction=system_prompt, max_output_tokens=1200, temperature=0.4)

    models = [model_name()]
    if models[0] != GEMINI_BACKUP:
        models.append(GEMINI_BACKUP)

    last_error = None
    for model in models:
        try:
            response = client.models.generate_content(model=model, contents=contents, config=config)
            text = (response.text or "").strip()
            if text:
                return text
        except Exception as e:
            last_error = e
            log.warning("Gemini model %s failed: %s", model, e)
    if last_error:
        raise last_error
    return None


def _ask_claude(system_prompt, history, message):
    import anthropic

    client = anthropic.Anthropic(api_key=_env("ANTHROPIC_API_KEY"), timeout=25.0, max_retries=1)
    messages = list(history) + [{"role": "user", "content": message}]
    response = client.messages.create(
        model=model_name(), max_tokens=600, system=system_prompt, messages=messages)
    text = "".join(b.text for b in response.content if getattr(b, "type", "") == "text").strip()
    return text or None


def ask(system_prompt, history, message):
    """Returns the AI reply text, or None. Raises if the call fails (the caller falls back)."""
    p = provider()
    if p == "gemini":
        return _ask_gemini(system_prompt, history, message)
    if p == "claude":
        return _ask_claude(system_prompt, history, message)
    return None
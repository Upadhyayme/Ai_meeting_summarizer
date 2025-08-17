import requests
from typing import Optional, Dict, Any, List
from .settings import settings

class SummarizerClient:
    """
    Calls an OpenAI-compatible /v1/chat/completions endpoint.
    Works with:
      - OpenAI (default base URL)
      - Groq (set OPENAI_BASE_URL to Groq's OpenAI-compatible endpoint and choose a Groq model)
    """
    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model

    def summarize(self, transcript: str, custom_prompt: str) -> str:
        system_prompt = (
            "You are a precise meeting notes summarizer. "
            "Produce clear, structured notes. Use headings, bullet points, and an Action Items section when applicable. "
            "Keep names, dates, decisions, and blockers. Be concise and faithful to the transcript."
        )

        user_prompt = (
            f"Custom instruction: {custom_prompt.strip() or 'Summarize the meeting clearly.'}\n\n"
            f"Transcript:\n{transcript.strip()}"
        )

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.2,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        url = f"{self.base_url}/v1/chat/completions"
        resp = requests.post(url, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        data = resp.json()

        # OpenAI-compatible response
        content = data["choices"][0]["message"]["content"]
        return content

client = SummarizerClient(
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_BASE_URL,
    model=settings.OPENAI_MODEL,
)
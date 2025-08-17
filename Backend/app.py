import os
import requests
import smtplib
from email.mime.text import MIMEText
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any

# ============================================================
# Settings (env vars or defaults)
# ============================================================
class Settings:
    # OpenAI-compatible config (works with OpenAI, Groq, etc.)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

    # CORS / Frontend origin
    FRONTEND_ORIGIN: str = os.getenv("FRONTEND_ORIGIN", "*")

    # SMTP / Email
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASS: str = os.getenv("SMTP_PASS", "")
    SMTP_FROM: str = os.getenv("SMTP_FROM") or SMTP_USER
    SMTP_USE_TLS: bool = os.getenv("SMTP_USE_TLS", "true").lower() in ("true", "1", "yes")

settings = Settings()


# ============================================================
# Summarizer Client
# ============================================================
class SummarizerClient:
    """Calls an OpenAI-compatible /v1/chat/completions endpoint."""

    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model

    def summarize(self, transcript: str, custom_prompt: str) -> str:
        system_prompt = (
            "You are a precise meeting notes summarizer. "
            "Produce clear, structured notes with headings, bullet points, and an Action Items section. "
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
        return data["choices"][0]["message"]["content"]


summarizer_client = SummarizerClient(
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_BASE_URL,
    model=settings.OPENAI_MODEL,
)


# ============================================================
# Email Sender
# ============================================================
def send_summary_email(to_email: str, subject: str, summary_body: str):
    if not settings.SMTP_USER or not settings.SMTP_PASS:
        raise RuntimeError("SMTP credentials missing. Set SMTP_USER and SMTP_PASS.")

    msg = MIMEText(summary_body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_FROM
    msg["To"] = to_email

    if settings.SMTP_USE_TLS:
        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
        server.starttls()
    else:
        server = smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT)

    try:
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        server.send_message(msg)
    finally:
        server.quit()


# ============================================================
# FastAPI App
# ============================================================
app = FastAPI(title="AI Meeting Summarizer")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN] if settings.FRONTEND_ORIGIN != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Routes
# ============================================================
class SummarizeBody(BaseModel):
    transcript: str
    prompt: Optional[str] = ""


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/upload-text")
async def upload_text(transcript: str = Form(...)):
    if not transcript.strip():
        raise HTTPException(400, "Transcript is empty.")
    return {"ok": True, "length": len(transcript)}


@app.post("/upload-file")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".txt"):
        raise HTTPException(400, "Only .txt files are supported in this demo.")
    content = (await file.read()).decode("utf-8", errors="ignore")
    return {"filename": file.filename, "content": content}


@app.post("/summarize")
async def summarize(body: SummarizeBody):
    if not settings.OPENAI_API_KEY:
        raise HTTPException(500, "OPENAI_API_KEY missing. Configure env vars.")
    if not body.transcript.strip():
        raise HTTPException(400, "Transcript is required.")

    try:
        summary = summarizer_client.summarize(body.transcript, body.prompt or "")
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(500, f"Summarization failed: {e}")


@app.post("/share")
async def share(email: EmailStr = Form(...), subject: str = Form("Meeting Summary"),
                summary: str = Form(...)):
    try:
        send_summary_email(email, subject, summary)
        return {"message": "Email sent successfully"}
    except Exception as e:
        raise HTTPException(500, f"Email failed: {e}")

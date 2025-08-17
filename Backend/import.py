from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional
from .settings import settings
from .summarizer import client as summarizer_client
from .emailer import send_summary_email

app = FastAPI(title="AI Meeting Summarizer")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN] if settings.FRONTEND_ORIGIN != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SummarizeBody(BaseModel):
    transcript: str
    prompt: Optional[str] = ""

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/upload-text")
async def upload_text(transcript: str = Form(...)):
    """If you want a separate endpoint to accept plain text via multipart/form-data."""
    if not transcript.strip():
        raise HTTPException(400, "Transcript is empty.")
    return {"ok": True, "length": len(transcript)}

@app.post("/upload-file")
async def upload_file(file: UploadFile = File(...)):
    """Accepts a .txt file and returns its content so the UI can place it in the textarea."""
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

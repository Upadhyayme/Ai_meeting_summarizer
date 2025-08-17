import os

class Settings:
    # OpenAI-compatible config: works with OpenAI or Groq (or any OpenAI-style API)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com")  # set Groq base to use Groq
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")  # for Groq, e.g. "llama3-8b-8192"

    # CORS / Frontend origin
    FRONTEND_ORIGIN: str = os.getenv("FRONTEND_ORIGIN", "*")  # set your Netlify URL in prod

    # SMTP / Email
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASS: str = os.getenv("SMTP_PASS", "")
    SMTP_FROM: str = os.getenv("SMTP_FROM", SMTP_USER)
    SMTP_USE_TLS: str = os.getenv("SMTP_USE_TLS", "true").lower()  # "true" or "false"
settings = Settings()
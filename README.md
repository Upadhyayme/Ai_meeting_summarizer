# Ai_meeting_summarizer
🚀 Features

Summarize meeting transcripts with AI (OpenAI/Groq).

Upload .txt files or paste text directly.
Custom prompts for summaries.
Email the summary to participants.
CORS enabled for frontend integration.

🛠️ Installation
1️⃣ Clone the repository
git clone https://github.com/your-username/ai-meeting-summarizer.git
cd ai-meeting-summarizer

2️⃣ Create & activate a virtual environment
python -m venv venv
source venv/bin/activate   # Linux / Mac
venv\Scripts\activate      # Windows

3️⃣ Install dependencies
pip install -r requirements.txt

⚙️ Environment Variables

Create a .env file in the root folder (or set system env vars):

# OpenAI / Groq API
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com   # For Groq, replace with their endpoint
OPENAI_MODEL=gpt-3.5-turbo

# CORS (frontend origin)
FRONTEND_ORIGIN=*

# SMTP (for email sending)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_email_password_or_app_password
SMTP_FROM=your_email@gmail.com
SMTP_USE_TLS=true

This gives you an interactive Swagger API UI to test endpoints.

📡 API Endpoints
🔹 Health Check
GET /health

🔹 Upload Text
POST /upload-text


Form-data:
transcript: text
🔹 Upload File
POST /upload-file

Form-data:
file: .txt file

🔹 Summarize
POST /summarize

🔹 Share via Email
POST /share

Form-data:
email: recipient email
subject: optional
summary: meeting summary

📦 Deployment

You can deploy this project on:
Railway / Render / Heroku for backend hosting
Netlify / Vercel for frontend integration

📝 License

MIT License. Free to use and modify.

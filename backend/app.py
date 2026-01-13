from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="NovaShield API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 🔒 Change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Email configuration
MAIL_SERVER = os.getenv("MAIL_SERVER")
MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")


# =======================
# Pydantic Schema
# =======================

class ContactFormRequest(BaseModel):
    name: str
    email: EmailStr
    company: Optional[str] = None
    phone: Optional[str] = None
    message: str
    service_type: Optional[str] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError("Name is required")
        return v.strip()

    @field_validator("message")
    @classmethod
    def validate_message(cls, v):
        if not v.strip():
            raise ValueError("Message is required")
        return v.strip()


# =======================
# Email Utility
# =======================

async def send_email(
    to_email: str,
    subject: str,
    body: str,
    is_html: bool = True
) -> bool:
    """
    Sends an email using Gmail SMTP (STARTTLS)
    """
    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = MAIL_USERNAME
        msg["To"] = to_email
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "html" if is_html else "plain"))

        smtp = aiosmtplib.SMTP(
            hostname=MAIL_SERVER,
            port=MAIL_PORT,
            start_tls=True,
            timeout=20
        )

        await smtp.connect()
        await smtp.login(MAIL_USERNAME, MAIL_PASSWORD)
        await smtp.send_message(msg)
        await smtp.quit()

        return True

    except Exception as e:
        print("❌ Email Error:", e)
        return False


# =======================
# API Endpoints
# =======================

@app.get("/")
async def root():
    return {"message": "NovaShield API is running"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "NovaShield API"}

@app.post("/api/submit-form")
async def submit_form(form: ContactFormRequest):
    try:
        # Extra regex check (optional)
        if not re.match(r"^[^@]+@[^@]+\.[^@]+$", form.email):
            raise HTTPException(status_code=400, detail="Invalid email format")

        # Admin email content
        admin_body = f"""
        <html>
        <body style="font-family: Arial;">
            <h2>New Contact Form Submission</h2>
            <p><b>Name:</b> {form.name}</p>
            <p><b>Email:</b> {form.email}</p>
            <p><b>Company:</b> {form.company or 'N/A'}</p>
            <p><b>Phone:</b> {form.phone or 'N/A'}</p>
            <p><b>Service:</b> {form.service_type or 'N/A'}</p>
            <hr>
            <p><b>Message:</b></p>
            <p>{form.message}</p>
        </body>
        </html>
        """

        # User confirmation email
        user_body = f"""
        <html>
        <body style="font-family: Arial;">
            <h2>Thank you, {form.name}!</h2>
            <p>Your message has been received.</p>
            <p>Our team will contact you shortly.</p>
            <br>
            <p>Regards,<br><b>NovaShield Team</b></p>
        </body>
        </html>
        """

        admin_sent = await send_email(
            ADMIN_EMAIL,
            f"New Contact Request - {form.name}",
            admin_body
        )

        user_sent = await send_email(
            form.email,
            "We received your message - NovaShield",
            user_body
        )

        if not admin_sent:
            print("⚠ Admin email failed")

        return {
            "status": "success",
            "message": "Your submission has been received.",
            "user_email_sent": user_sent
        }

    except HTTPException:
        raise
    except Exception as e:
        print("❌ Submission Error:", e)
        raise HTTPException(status_code=500, detail="Internal server error")


# =======================
# Global Error Handler
# =======================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return {
        "status": "error",
        "status_code": exc.status_code,
        "detail": exc.detail
    }


# =======================
# Run Server
# =======================

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 5000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)

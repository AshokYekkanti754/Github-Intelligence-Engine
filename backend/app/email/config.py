import os
from dotenv import load_dotenv

load_dotenv()

# Email Configuration
EMAIL_CONFIG = {
    "SMTP_HOST": os.getenv("SMTP_HOST", "smtp.gmail.com"),
    "SMTP_PORT": int(os.getenv("SMTP_PORT", 587)),
    "SMTP_USER": os.getenv("SMTP_USER", ""),
    "SMTP_PASSWORD": os.getenv("SMTP_PASSWORD", ""),
    "FROM_EMAIL": os.getenv("FROM_EMAIL", "noreply@github-intelligence.com"),
    "FROM_NAME": os.getenv("FROM_NAME", "GitHub Intelligence Engine"),
    "USE_TLS": os.getenv("SMTP_USE_TLS", "True").lower() == "true",
}

# Email Templates Directory
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
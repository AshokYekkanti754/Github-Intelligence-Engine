import asyncio
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import os
import logging

from .config import EMAIL_CONFIG, TEMPLATES_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Setup Jinja2 templates
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

class EmailService:
    """Handle email notifications"""
    
    def __init__(self):
        self.smtp_host = EMAIL_CONFIG["SMTP_HOST"]
        self.smtp_port = EMAIL_CONFIG["SMTP_PORT"]
        self.smtp_user = EMAIL_CONFIG["SMTP_USER"]
        self.smtp_password = EMAIL_CONFIG["SMTP_PASSWORD"]
        self.from_email = EMAIL_CONFIG["FROM_EMAIL"]
        self.from_name = EMAIL_CONFIG["FROM_NAME"]
        self.use_tls = EMAIL_CONFIG["USE_TLS"]
        
    async def send_email(self, to_email: str, subject: str, html_content: str, text_content: str = None):
        """Send email using SMTP"""
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email
            
            # Add plain text version
            if text_content:
                part_text = MIMEText(text_content, "plain")
                message.attach(part_text)
            
            # Add HTML version
            part_html = MIMEText(html_content, "html")
            message.attach(part_html)
            
            # Send email
            async with aiosmtplib.SMTP(
                hostname=self.smtp_host,
                port=self.smtp_port,
                use_tls=self.use_tls
            ) as smtp:
                if not self.use_tls:
                    await smtp.starttls()
                
                if self.smtp_user and self.smtp_password:
                    await smtp.login(self.smtp_user, self.smtp_password)
                
                await smtp.send_message(message)
                
            logger.info(f"✅ Email sent to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send email to {to_email}: {e}")
            return False
    
    async def send_weekly_digest(self, user_email: str, username: str, 
                                 profiles_data: List[Dict], week_range: str):
        """Send weekly digest email"""
        try:
            template = env.get_template("weekly_digest.html")
            html_content = template.render(
                username=username,
                week_range=week_range,
                profiles=profiles_data,
                total_profiles=len(profiles_data),
                total_changes=sum(1 for p in profiles_data if p.get('score_change', 0) != 0)
            )
            
            subject = f"📊 GitHub Intelligence Weekly Digest - {week_range}"
            
            return await self.send_email(user_email, subject, html_content)
            
        except Exception as e:
            logger.error(f"Failed to generate weekly digest: {e}")
            return False
    
    async def send_profile_update_notification(self, user_email: str, username: str,
                                               profile_name: str, old_score: int, 
                                               new_score: int, changes: Dict):
        """Send immediate notification when saved profile changes significantly"""
        try:
            change_text = f"from {old_score} to {new_score}"
            if new_score > old_score:
                subject = f"🎉 {profile_name}'s portfolio improved!"
                body = f"Good news! {profile_name}'s portfolio score increased {change_text}!"
            else:
                subject = f"📉 {profile_name}'s portfolio changed"
                body = f"{profile_name}'s portfolio score changed {change_text}."
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head><style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ max-width: 500px; margin: 0 auto; padding: 20px; }}
                .score-up {{ color: green; }}
                .score-down {{ color: red; }}
            </style></head>
            <body>
                <div class="container">
                    <h2>Profile Update: @{profile_name}</h2>
                    <p>Score changed: <strong>{old_score}</strong> → <strong>{new_score}</strong></p>
                    <a href="http://localhost:5173/?user={profile_name}">View Profile →</a>
                </div>
            </body>
            </html>
            """
            
            return await self.send_email(user_email, subject, html_content)
            
        except Exception as e:
            logger.error(f"Failed to send profile update notification: {e}")
            return False

# Global email service instance
email_service = EmailService()
"""Settings API endpoints."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.models.settings import SettingsModel
from app.utils.helpers import load_settings, save_settings

router = APIRouter(prefix="/api/settings", tags=["settings"])


class EmailAlertsConfig(BaseModel):
    """Email alerts configuration."""
    enabled: bool = False
    smtp_server: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    from_email: str = ""
    recipients: List[str] = []
    alert_types: Dict[str, bool] = {}


@router.get("")
def get_settings_endpoint():
    """Get current settings."""
    return load_settings().dict()


@router.put("")
def update_settings_endpoint(new_settings: SettingsModel):
    """Update settings."""
    save_settings(new_settings)
    return {"ok": True}


@router.post("/test-email")
async def test_email_endpoint(email_config: EmailAlertsConfig):
    """Test email configuration by sending a test email."""
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        if not email_config.enabled:
            raise HTTPException(status_code=400, detail="Email alerts are not enabled")
        
        if not email_config.smtp_server:
            raise HTTPException(status_code=400, detail="SMTP server is required")
        
        if not email_config.from_email:
            raise HTTPException(status_code=400, detail="From email is required")
        
        if not email_config.recipients:
            raise HTTPException(status_code=400, detail="At least one recipient is required")
        
        # Create test email
        msg = MIMEMultipart()
        msg['From'] = email_config.from_email
        msg['To'] = ", ".join(email_config.recipients)
        msg['Subject'] = "Test Email from AI Agent System"
        
        body = """
        This is a test email from the AI Agent System.
        
        If you receive this email, your email configuration is working correctly.
        
        Configuration Details:
        - SMTP Server: {smtp_server}
        - SMTP Port: {smtp_port}
        - From: {from_email}
        - Recipients: {recipients}
        """.format(
            smtp_server=email_config.smtp_server,
            smtp_port=email_config.smtp_port,
            from_email=email_config.from_email,
            recipients=", ".join(email_config.recipients)
        )
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        try:
            server = smtplib.SMTP(email_config.smtp_server, email_config.smtp_port)
            server.starttls()
            if email_config.smtp_username and email_config.smtp_password:
                server.login(email_config.smtp_username, email_config.smtp_password)
            server.send_message(msg)
            server.quit()
            
            return {
                "success": True,
                "message": "Test email sent successfully"
            }
        except smtplib.SMTPException as e:
            raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Email error: {str(e)}")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


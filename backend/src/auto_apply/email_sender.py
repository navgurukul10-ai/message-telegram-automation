"""
Email Application Sender with CC support
"""
import smtplib
import json
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from typing import Dict
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils.logger import get_logger

logger = get_logger('email_sender')


class EmailApplicationSender:
    """Send job applications via email with CC support"""
    
    def __init__(self, profile_path: str, email_config_path: str = None):
        with open(profile_path, 'r') as f:
            self.profile = json.load(f)
        
        self.from_email = self.profile['personal_info']['email']
        self.cc_emails = self.profile['application_settings'].get('cc_emails', [])
        self.resume_path = self.profile['application_settings'].get('resume_path')
        
        # Email credentials (you'll need to set these)
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.email_password = None  # Will be loaded from environment or config
        
        # Load email config if provided
        if email_config_path and os.path.exists(email_config_path):
            with open(email_config_path, 'r') as f:
                email_config = json.load(f)
                self.smtp_server = email_config.get('smtp_server', self.smtp_server)
                self.smtp_port = email_config.get('smtp_port', self.smtp_port)
                self.email_password = email_config.get('password')
        
        # Try to get password from environment
        if not self.email_password:
            self.email_password = os.environ.get('EMAIL_APP_PASSWORD')
    
    def generate_subject(self, job_info: Dict) -> str:
        """Generate email subject"""
        
        # Try to extract job title from first line
        first_line = job_info['message_text'].split('\n')[0]
        
        # Clean up the title
        title = first_line.strip('*#-_').strip()
        
        if len(title) > 100:
            title = title[:100] + "..."
        
        return f"Application for {title}"
    
    def generate_body(self, job_info: Dict) -> str:
        """Generate email body"""
        
        template = f"""Hi there,

I noticed your hiring post and it made me think of Gaurav.

He's a seasoned DevOps engineer from Bangalore with {self.profile['professional_summary']['experience_years']}+ years of experience across fintech, cybersecurity, and analytics domains. Currently working as {self.profile['professional_summary']['current_role']} at {self.profile['professional_summary']['current_company']}.

His key strengths:
• AWS, Azure, GCP cloud platforms
• Docker, Kubernetes, Terraform
• CI/CD pipelines and automation
• Security & compliance (PCI-DSS, ISO)

Gaurav is passionate about the "automate everything" philosophy and has led teams while working with globally distributed companies.

I've attached his resume. Would love to connect if this seems like a good fit!

Best,
NavGurukul Team
{self.profile['personal_info']['phone']}
{self.profile['personal_info']['email']}
LinkedIn: {self.profile['personal_info']['linkedin']}
"""
        
        return template
    
    def send_application(self, to_email: str, job_info: Dict, dry_run: bool = False) -> Dict:
        """Send job application email with CC"""
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            # Add CC if configured
            if self.cc_emails:
                msg['Cc'] = ', '.join(self.cc_emails)
            
            msg['Subject'] = self.generate_subject(job_info)
            
            # Email body
            body = self.generate_body(job_info)
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach resume if exists
            if self.resume_path and os.path.exists(self.resume_path):
                with open(self.resume_path, 'rb') as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                
                encoders.encode_base64(part)
                
                filename = os.path.basename(self.resume_path)
                part.add_header('Content-Disposition', f'attachment; filename= {filename}')
                
                msg.attach(part)
                
                logger.info(f"Attached resume: {filename}")
            else:
                logger.warning(f"Resume not found at {self.resume_path}")
            
            if dry_run:
                logger.info("DRY RUN - Email would be sent to:")
                logger.info(f"  To: {to_email}")
                if self.cc_emails:
                    logger.info(f"  CC: {', '.join(self.cc_emails)}")
                logger.info(f"  Subject: {msg['Subject']}")
                
                return {
                    'status': 'dry_run',
                    'to': to_email,
                    'cc': self.cc_emails,
                    'subject': msg['Subject'],
                    'timestamp': datetime.now().isoformat()
                }
            
            # Send email
            if not self.email_password:
                raise Exception("Email password not configured. Set EMAIL_APP_PASSWORD environment variable.")
            
            # Recipients include To + CC
            recipients = [to_email]
            if self.cc_emails:
                recipients.extend(self.cc_emails)
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.from_email, self.email_password)
                server.send_message(msg, to_addrs=recipients)
            
            logger.info(f"Application sent successfully to {to_email}")
            if self.cc_emails:
                logger.info(f"CC sent to {', '.join(self.cc_emails)}")
            
            return {
                'status': 'sent',
                'to': to_email,
                'cc': self.cc_emails,
                'subject': msg['Subject'],
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return {
                'status': 'failed',
                'to': to_email,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }


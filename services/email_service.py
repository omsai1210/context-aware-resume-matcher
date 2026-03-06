import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import settings
import logging

logger = logging.getLogger(__name__)

class EmailDispatcher:
    """
    Handles sending recruitment emails with personalized feedback 
    using SMTP.
    """

    def send_decision_email(self, candidate_email: str, candidate_name: str, job_title: str, score: float, llm_feedback: str):
        """
        Sends an HTML formatted email based on the match score.
        """
        is_shortlisted = score >= 80
        subject = f"Application Update: {job_title} - {'Next steps for interview' if is_shortlisted else 'Feedback on your profile'}"
        
        status_text = "Congratulations! You've been shortlisted for the next round." if is_shortlisted else "Thank you for your interest in the role."
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px;">
                <h2 style="color: {'#2e7d32' if is_shortlisted else '#d32f2f'};">{status_text}</h2>
                <p>Hello {candidate_name},</p>
                <p>We have evaluated your application for the <strong>{job_title}</strong> position using our context-aware matching system.</p>
                
                <div style="background: #f9f9f9; padding: 15px; border-left: 4px solid {'#4caf50' if is_shortlisted else '#ff9800'}; margin: 15px 0;">
                    <p><strong>Recruiter's Perspective:</strong></p>
                    <p><i>{llm_feedback}</i></p>
                </div>
                
                {"<p>Our team will reach out shortly to schedule a technical interview.</p>" if is_shortlisted else "<p>While we won't be moving forward at this time due to specific skill gaps, we've added your profile to our talent pool for future roles that match your expertise.</p>"}
                
                <p>Best regards,<br>
                GraphRAG-ATS Recruitment Team</p>
            </div>
        </body>
        </html>
        """

        msg = MIMEMultipart()
        msg['From'] = settings.SMTP_USERNAME
        msg['To'] = candidate_email
        msg['Subject'] = subject
        msg.attach(MIMEText(html_body, 'html'))

        try:
            with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                server.send_message(msg)
                logger.info(f"Sent decision email to {candidate_email} (Score: {score})")
        except Exception as e:
            logger.error(f"Failed to send email to {candidate_email}: {e}")
            # In a production app, we might queue this for retry.
            raise e

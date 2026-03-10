import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

def send_feedback_email(to_email: str, candidate_name: str, score: int, total_reqs: int, explanation: str):
    """
    Sends an automated feedback email to the candidate containing the GraphRAG score and 
    the personalized LLM 'Glass Box' explanation.
    """
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    
    if not smtp_user or not smtp_password:
        print(f"Warning: SMTP_USER or SMTP_PASSWORD not set. Mocking email to {to_email}.")
        print(f"Subject: Update on your application\nBody:\nScore: {score}/{total_reqs}\nFeedback: {explanation}")
        return
        
    subject = "Update on Your Application - Feedback Enclosed"
    
    body = f"""
Dear {candidate_name},

Thank you for applying for the role. We have carefully reviewed your application using our context-aware ATS.

Your Skill Profile Match Score: {score} out of {total_reqs}

Feedback based on your required skill profile:
{explanation}

Best regards,
The Hiring Team
    """

    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        text = msg.as_string()
        server.sendmail(smtp_user, to_email, text)
        server.quit()
        print(f"Successfully sent automated feedback email to {to_email}")
    except Exception as e:
        print(f"Failed to send email to {to_email}: {str(e)}")

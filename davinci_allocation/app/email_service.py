import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailService:
    """
    handles all the emails we need to send out when teachers get assigned
    """
    def __init__(self):
        self.server = os.getenv('EMAIL_SERVER', 'smtp.example.com')
        self.port = int(os.getenv('EMAIL_PORT', 587))
        self.username = os.getenv('EMAIL_USER', 'noreply@cga.edu')
        self.password = os.getenv('EMAIL_PASSWORD', 'password')
        self.from_email = os.getenv('EMAIL_FROM', 'davinci@cga.edu')
        
        # check if we should actually send or just log for testing
        self.send_emails = os.getenv('SEND_EMAILS', 'false').lower() == 'true'
    
    def send_confirmation_email(self, allocation, teacher_info):
        """
        let everyone know we've matched a teacher & student!
        sends to student, parent, AO and the teacher
        """
        teacher_name = teacher_info.get('name', 'Your Teacher')
        teacher_email = teacher_info.get('email', 'teacher@cga.edu')
        subject = allocation.current_subject or allocation.subjects[0]
        
        # setup the email
        msg = MIMEMultipart()
        msg['From'] = self.from_email
        msg['To'] = allocation.student_email
        msg['Cc'] = f"{allocation.guardian_email}, {teacher_email}, {allocation.request_email}"
        msg['Subject'] = f"Da Vinci Allocation: {subject} with {teacher_name}"
        
        # fill in our template with the right names etc
        body = self._get_confirmation_email_template().format(
            student_name=allocation.student_name,
            subject=subject,
            teacher_name=teacher_name,
            teacher_email=teacher_email
        )
        
        msg.attach(MIMEText(body, 'plain'))
        
        # off it goes!
        self._send_email(
            to_email=allocation.student_email,
            cc_emails=[allocation.guardian_email, teacher_email, allocation.request_email],
            msg=msg
        )
    
    def _send_email(self, to_email, cc_emails, msg):
        """actually send the email (or just log it in testing)"""
        recipients = [to_email] + cc_emails
        
        if not self.send_emails:
            # just print it for testing - don't actually send
            print(f"Email would be sent to: {', '.join(recipients)}")
            print(f"Subject: {msg['Subject']}")
            print("Body:")
            
            # grab the text part
            for part in msg.walk():
                if part.get_content_type() == 'text/plain':
                    print(part.get_payload())
            
            return True
        
        try:
            # do the real email sending
            with smtplib.SMTP(self.server, self.port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.sendmail(self.from_email, recipients, msg.as_string())
            return True
        except Exception as e:
            # oops, something went wrong
            print(f"Error sending email: {str(e)}")
            return False
    
    def _get_confirmation_email_template(self):
        """template for the teacher confirmation email"""
        return """Hi {student_name},

Your {subject} teacher {teacher_name} is ready to meet you! Here's their email: {teacher_email}

Please contact your teacher to schedule your first lesson. Remember to have the following ready:
1. Your learning goals and any specific areas you want to focus on
2. Any materials or textbooks you already have
3. Questions about the course structure or assessment methods

If you have any issues connecting with your teacher, please let us know.

Best regards,
The CGA Da Vinci Team
""" 
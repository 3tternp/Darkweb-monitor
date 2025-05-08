import smtplib
from email.mime.text import MIMEText

# Function to send email notification
def send_alert_email(alert):
    msg = MIMEText(f"Alert triggered! Details: {alert.message}")
    msg['Subject'] = f"Alert for keyword: {alert.keyword}"
    msg['From'] = 'noreply@example.com'
    msg['To'] = 'user@example.com'

    try:
        with smtplib.SMTP('smtp.example.com') as server:
            server.sendmail('noreply@example.com', ['user@example.com'], msg.as_string())
        print("Alert email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")


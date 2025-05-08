from .alert_model import Alert
from datetime import datetime

# Function to filter alerts by date range
def filter_alerts(alerts, start_date: datetime, end_date: datetime):
    return [alert for alert in alerts if start_date <= alert.date <= end_date]

# Function to process a new alert (for example, saving it)
def process_new_alert(alert: Alert):
    # You can expand this to integrate with the database or trigger further processing
    save_alert_to_db(alert)
    trigger_alert_notification(alert)


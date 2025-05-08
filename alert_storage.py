from app.db import SessionLocal
from app.models.alert import Alert as AlertModel  # Assuming you have the Alert model defined

# Function to store alert in the database
def save_alert_to_db(alert):
    db = SessionLocal()
    db_alert = AlertModel(
        keyword=alert.keyword,
        source=alert.source,
        date=alert.date,
        message=alert.message
    )
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    db.close()

def get_alerts_from_db():
    db = SessionLocal()
    alerts = db.query(AlertModel).all()
    db.close()
    return alerts


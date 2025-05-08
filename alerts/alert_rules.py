class AlertRule:
    def __init__(self, keyword, severity_level):
        self.keyword = keyword
        self.severity_level = severity_level

    def check_alert(self, message):
        # Simple rule: check if keyword is in message
        if self.keyword in message:
            return True
        return False


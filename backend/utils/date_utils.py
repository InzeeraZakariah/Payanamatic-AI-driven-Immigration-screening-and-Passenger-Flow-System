from datetime import datetime

def days_until(date_value):
    if not date_value:
        return None
    
    today = datetime.now().date()

    return (date_value - today).days

from datetime import date

def days_until(date_value):
    if not date_value:
        return 9999

    today = date.today()
    return (target_date - today).days

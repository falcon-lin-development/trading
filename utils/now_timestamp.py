from datetime import datetime, timedelta, timezone

def get_timestamp_from_today_midnight_utc(days: int):
    # Get the current UTC time
    now_utc = datetime.now(timezone.utc)
    
    # Truncate the time to midnight (00:00:00)
    midnight_utc = now_utc.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Adjust for the specified number of days
    target_date = midnight_utc + timedelta(days=days)
    
    # Convert to timestamp and then to milliseconds
    midnight_timestamp = int(target_date.timestamp()) * 1000
    
    return midnight_timestamp

def get_today_midnight_utc_timestamp():
    return get_timestamp_from_today_midnight_utc(0)
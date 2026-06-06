import re
from datetime import datetime, date, timedelta

def parse_quick_add(text: str) -> tuple[str, str, str]:
    """
    Parses a natural language string to extract a title, due_date (YYYY-MM-DD), and due_time (HH:MM).
    Examples:
        "Java practice 8 PM" -> ("Java practice", "2026-06-06", "20:00")
        "Gym tomorrow 6 AM" -> ("Gym", "2026-06-07", "06:00")
        "Submit assignment Friday" -> ("Submit assignment", "2026-06-12", "12:00")
    Default time is 12:00 if not specified.
    Default date is today if not specified (or tomorrow if the time has already passed today).
    """
    cleaned_text = text.strip()
    
    # 1. Parse Time
    # Formats: "10:30 PM", "8 PM", "14:00", "8pm", "12 am"
    time_pattern = r'\b(\d{1,2})(?::(\d{2}))?\s*(AM|PM|am|pm)?\b'
    time_matches = list(re.finditer(time_pattern, cleaned_text))
    
    parsed_time = None
    time_match_span = None
    
    for match in reversed(time_matches):
        hour_str = match.group(1)
        minute_str = match.group(2) or "00"
        period = match.group(3)
        
        hour = int(hour_str)
        minute = int(minute_str)
        
        # Validate hours/minutes
        if minute < 0 or minute > 59:
            continue
            
        if period:
            period = period.upper()
            if hour < 1 or hour > 12:
                continue
            if period == "PM" and hour < 12:
                hour += 12
            elif period == "AM" and hour == 12:
                hour = 0
        else:
            if hour < 0 or hour > 23:
                continue
        
        parsed_time = f"{hour:02d}:{minute:02d}"
        time_match_span = match.span()
        break
        
    # Remove the matched time substring from the text
    text_no_time = cleaned_text
    if time_match_span:
        text_no_time = cleaned_text[:time_match_span[0]] + cleaned_text[time_match_span[1]:]
        
    # 2. Parse Date
    # Keywords: "today", "tomorrow", weekdays ("monday", "tuesday", etc.)
    today = date.today()
    parsed_date = today
    date_match_span = None
    
    weekdays = {
        "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
        "friday": 4, "saturday": 5, "sunday": 6,
        "mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6
    }
    
    words = text_no_time.lower().split()
    
    # Check for "tomorrow"
    if "tomorrow" in words:
        parsed_date = today + timedelta(days=1)
        # Find span of "tomorrow" to remove it
        match = re.search(r'\btomorrow\b', text_no_time, re.IGNORECASE)
        if match:
            date_match_span = match.span()
    elif "today" in words:
        parsed_date = today
        match = re.search(r'\btoday\b', text_no_time, re.IGNORECASE)
        if match:
            date_match_span = match.span()
    else:
        # Check weekdays
        for word in words:
            # Clean punctuation
            clean_word = re.sub(r'[^\w]', '', word)
            if clean_word in weekdays:
                target_day = weekdays[clean_word]
                current_day = today.weekday()
                days_ahead = target_day - current_day
                if days_ahead <= 0:  # Target day is earlier in the week or today, schedule for next week
                    days_ahead += 7
                parsed_date = today + timedelta(days=days_ahead)
                match = re.search(rf'\b{clean_word}\b', text_no_time, re.IGNORECASE)
                if match:
                    date_match_span = match.span()
                break
                
    # Remove the matched date substring from the text
    text_no_date = text_no_time
    if date_match_span:
        text_no_date = text_no_time[:date_match_span[0]] + text_no_time[date_match_span[1]:]
        
    # Clean up title (remove extra spaces, connectors like "at", "on", "by")
    title = text_no_date.strip()
    title = re.sub(r'\b(at|on|by|in|for|to)\b\s*$', '', title, flags=re.IGNORECASE).strip()
    title = re.sub(r'\s+', ' ', title)
    
    # Fallbacks
    if not title:
        title = "Quick Reminder"
        
    if not parsed_time:
        parsed_time = "12:00"
    else:
        # If time is in the past and no explicit date was set, set date to tomorrow
        current_time_str = datetime.now().strftime("%H:%M")
        if parsed_date == today and parsed_time < current_time_str:
            parsed_date = today + timedelta(days=1)
            
    return title, parsed_date.strftime("%Y-%m-%d"), parsed_time

if __name__ == "__main__":
    tests = [
        "Java practice 8 PM",
        "Gym tomorrow 6 AM",
        "Submit assignment Friday",
        "Meeting at 2:30 PM today",
        "Write report tomorrow",
        "Email boss at 15:00"
    ]
    for t in tests:
        print(f"'{t}' -> {parse_quick_add(t)}")

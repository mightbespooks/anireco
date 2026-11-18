from datetime import date

def format_date(date_dict):
    if not date_dict:
        return None
    
    year = date_dict.get("year")
    month = date_dict.get("month") 
    day = date_dict.get("day")

    if not year:
        return None

    return date(
        year, 
        month if month else 1, 
        day if day else 1
    )

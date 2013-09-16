from datetime import datetime

def convert_to_date(alleged_date):
    try:
        return datetime.strptime(alleged_date, "%Y-%m-%d")
    except ValueError:
        try:
            return datetime.strptime(alleged_date, "%Y-%m")
        except ValueError:
            try:
                return datetime.strptime(alleged_date, "%Y")
            except ValueError:
                return ""     

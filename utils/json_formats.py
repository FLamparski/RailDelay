import datetime

def date_handler(obj):
    if isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date):
        return obj.isoformat()
    else:
        return None

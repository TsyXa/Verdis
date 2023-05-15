from datetime import datetime, timedelta

def dur(reason):
    time = lambda n, d : n * d
    
    try:
        reason = reason.split("-duration ")[1]
    except:
        duration = None
        durmessage = "is permanent"
        return durmessage, duration

    if reason[-1:].lower() == "d":
        try:
            duration = int(reason[:-1])
            durmessage = f"expires in {duration} days"

        except:
            duration = None
            durmessage = "is permanent"

    elif reason[-1:].lower() == "w":
        try:
            duration = time(int(reason[:-1]), 7)
            durmessage = f"expires in {duration} days"

        except:
            duration = None
            durmessage = "is permanent"

    elif reason[-1:].lower() == "m":
        try:
            duration = time(int(reason[:-1]), 30)
            durmessage = f"expires in {reason[:-1]} months"

        except:
            duration = None
            durmessage = "is permanent"

    elif reason[-1:].lower() == "y":
        try:
            duration = time(int(reason[:-1]), 365)
            durmessage = f"expires in {reason[:-1]} years"

        except:
            duration = None
            durmessage = "is permanent"

    else:
        durmessage = "is permanent"
        duration = None

    return durmessage, duration

def expdate(start: datetime, days: int):
    return timedelta(days) + start

def to_dur(duration):
    if duration[-1:] == "m":
        durmessage = f"expires in {duration[:-1]} minutes"
        duration = timedelta(minutes = int(duration[:-1]))

    elif duration[-1:] == "h":
        durmessage = f"expires in {duration[:-1]} hours"
        duration = timedelta(hours = int(duration[:-1]))

    elif duration[-1:] == "d":
        durmessage = f"expires in {duration[:-1]} days"
        duration = timedelta(days = int(duration[:-1]))

    return durmessage, duration
from datetime import timedelta
from time import time as unix
from math import floor

def dur(durin):
    time = lambda n, d : n * d * 24 * 60 * 60

    if durin == None:
        duration = 0
        durmessage = "is permanent"

    elif durin[-1:].lower() == "d":
        try:
            duration = time(int(durin[:-1]), 1)
            durmessage = f"expires <t:{floor(unix() + duration)}:R>"

        except:
            duration = 0
            durmessage = "is permanent"

    elif durin[-1:].lower() == "w":
        try:
            duration = time(int(durin[:-1]), 7)
            durmessage = f"expires <t:{floor(unix() + duration)}:R>"

        except:
            duration = 0
            durmessage = "is permanent"

    elif durin[-1:].lower() == "m":
        try:
            duration = time(int(durin[:-1]), 30)
            durmessage = f"expires <t:{floor(unix() + duration)}:R>"

        except:
            duration = 0
            durmessage = "is permanent"

    elif durin[-1:].lower() == "y":
        try:
            duration = time(int(durin[:-1]), 365)
            durmessage = f"expires <t:{floor(unix() + duration)}:R>"

        except:
            duration = 0
            durmessage = "is permanent"

    else:
        duration = 0
        durmessage = "is permanent"

    return durmessage, duration

def to_dur(duration):
    time = lambda n, d : n * d
    intdur = int(duration[:-1])

    if duration[-1:] == "m":
        if intdur > 40320:
            intdur = 40320
        duration = time(intdur, 60)
        durmessage = f"expires <t:{floor(unix() + duration)}:R>"
        todur = timedelta(minutes = intdur)

    elif duration[-1:] == "h":
        if intdur > 672:
            intdur = 672
        duration = time(intdur, 3600)
        durmessage = f"expires <t:{floor(unix() + duration)}:R>"
        todur = timedelta(hours = intdur)

    elif duration[-1:] == "d":
        if intdur > 28:
            intdur = 28
        duration = time(intdur, 86400)
        durmessage = f"expires <t:{floor(unix() + duration)}:R>"
        todur = timedelta(days = intdur)

    elif duration[-1:] == "w":
        if intdur > 4:
            intdur = 4
        duration = time(intdur, 604800)
        durmessage = f"expires <t:{floor(unix() + duration)}:R>"
        todur = timedelta(days = intdur)

    return durmessage, duration, todur

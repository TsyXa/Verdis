import string
from random import choice

charlist = string.ascii_letters + string.digits

def new(chars: int):
    newid = ""
    for i in range(chars):
        newid += choice(charlist)
    return newid
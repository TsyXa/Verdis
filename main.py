import discord
import json
from discord.ext import commands
from datetime import datetime
import random
import idgen
import durationcalc

client = commands.Bot(intents = discord.Intents.all(), command_prefix = "!", allowed_mentions=discord.AllowedMentions(roles=False, users=False, everyone=False))

@client.event
async def on_ready():
    print("Client Ready")

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f"> :x: You cannot do that! Required permissions: `{error.missing_permissions}`")
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send(f">>> :x: I cannot do that! I require the following permissions: `{error.missing_permissions}`\n:bulb: Try moving my role above all others, or toggling `Administrator` permissions to True.")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send(f">>> :x: I could not find the user `{error.argument}`.\n:bulb: Try tagging the user, or using their User ID.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"> :x: You forgot to input the following arguments: `{error.param}`")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send(f">>> :x: I could not find the user `{error.argument}`.\n:bulb: Try tagging the user, or using their User ID.")
    elif isinstance(error, commands.UserNotFound):
        await ctx.send(f">>> :x: I could not find the user `{error.argument}`.\n:bulb: Try tagging the user, or using their User ID.")
    elif isinstance(error, commands.ChannelNotFound):
        await ctx.send(f">>> :x: I could not find the channel `{error.argument}`.\n:bulb: Try tagging the channel, or using its Channel ID.")
    else:
        await ctx.send(f">>> :x: **Unexpected Error**\nAn error occurred. Please report this message to <@!476457324609929226> along with the original command you entered.```\n{error}\n```")

@client.command()
@commands.has_permissions(manage_messages=True)
async def warn(ctx, member: discord.Member, *, reason: str):
    with open(f"{ctx.guild.id}logs.json", "a"): #Check if file exists, if not create it
        pass

    with open(f"{ctx.guild.id}logs.json") as logsf: #Open file
        logs = logsf.read()

        try: #Json -> Dict
            logs = json.loads(logs)
        except:
            logs = {}

    durmessage, duration = durationcalc.dur(reason)

    if duration == None:
        date = None
    else:
        date = str(durationcalc.expdate(start = datetime.now(), days = duration))

    reason = reason.split("-duration ")[0]

    try: #Logs the warning in server logs
        logs[str(member.id)][f"WRN-{idgen.new(6)}"] = {"reason": reason, "mod": ctx.author.id, "date": str(datetime.now()), "expires": date}
    except:
        logs[str(member.id)] = {}
        logs[str(member.id)][f"WRN-{idgen.new(6)}"] = {"reason": reason, "mod": ctx.author.id, "date":str(datetime.now()), "expires": date}
        
    with open(f"{ctx.guild.id}logs.json", "w") as logsf: #Dump back into json
        logs = json.dumps(logs, indent=4)
        logsf.write(logs)
    
    try:
        await member.send(f">>> You have been warned in the server **{ctx.guild.name}** for **{reason}**.\n:warning: This warning **{durmessage}**.")
        await ctx.send(f">>> Successfully warned <@!{member.id}> for **{reason}**. This warning **{durmessage}**.")
    except:
        await ctx.send(f">>> Successfully warned <@!{member.id}> for **{reason}**. This warning **{durmessage}**.\n:warning: I could not DM the user to inform of them of this warning, either due to their DMs being closed or them having blocked this bot.")

@client.command()
@commands.has_permissions(moderate_members=True)
async def timeout(ctx, member: discord.Member, duration, *, reason: str):
    with open(f"{ctx.guild.id}logs.json", "a"): #Check if file exists, if not create it
        pass

    with open(f"{ctx.guild.id}logs.json") as logsf: #Open file
        logs = logsf.read()

        try: #Json -> Dict
            logs = json.loads(logs)
        except:
            logs = {}

    if int(duration[:-1]) > 28:
        await ctx.send(f"> :x: You cannot time out a user for more than 28 days.")
        return
    
    durmessage, duration = durationcalc.to_dur(duration)

    date = str(duration + datetime.now())

    try: #Logs the time out in server logs
        logs[str(member.id)][f"TMO-{idgen.new(6)}"] = {"reason": reason, "mod": ctx.author.id, "date": str(datetime.now()), "expires": date}
    except:
        logs[str(member.id)] = {}
        logs[str(member.id)][f"TMO-{idgen.new(6)}"] = {"reason": reason, "mod": ctx.author.id, "date":str(datetime.now()), "expires": date}
        
    with open(f"{ctx.guild.id}logs.json", "w") as logsf: #Dump back into json
        logs = json.dumps(logs, indent=4)
        logsf.write(logs)
    
    try:
        await member.send(f">>> You have been timed out in the server **{ctx.guild.name}** for **{reason}**.\n:warning: This time out **{durmessage}**.")
        await member.timeout(duration, reason = f"Timed out by {ctx.author.name}#{ctx.author.discriminator} (ID {ctx.author.id}) for reason {reason}. This time out {durmessage}.")
        await ctx.send(f">>> Successfully timed out <@!{member.id}> for **{reason}**. This time out **{durmessage}**.")
    except:
        await member.timeout(duration, reason = f"Timed out by {ctx.author.name}#{ctx.author.discriminator} (ID {ctx.author.id}) for reason {reason}. This time out {durmessage}.")
        await ctx.send(f">>> Successfully timed out <@!{member.id}> for **{reason}**. This time out **{durmessage}**.\n:warning: I could not DM the user to inform of them of this time out, either due to their DMs being closed or them having blocked this bot.")

@client.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason: str):
    with open(f"{ctx.guild.id}logs.json", "a"): #Check if file exists, if not create it
        pass

    with open(f"{ctx.guild.id}logs.json") as logsf: #Open file
        logs = logsf.read()

        try: #Json -> Dict
            logs = json.loads(logs)
        except:
            logs = {}

    try: #Logs the kick in server logs
        logs[str(member.id)][f"KCK-{idgen.new(6)}"] = {"reason": reason, "mod": ctx.author.id, "date": str(datetime.now()), "expires": None}
    except:
        logs[str(member.id)] = {}
        logs[str(member.id)][f"KCK-{idgen.new(6)}"] = {"reason": reason, "mod": ctx.author.id, "date":str(datetime.now()), "expires": None}
        
    with open(f"{ctx.guild.id}logs.json", "w") as logsf: #Dump back into json
        logs = json.dumps(logs, indent=4)
        logsf.write(logs)
    
    try:
        await member.send(f">>> You have been kicked from the server **{ctx.guild.name}** for **{reason}**.\n:information_source: You may rejoin the server at any time.")
        await member.kick(reason=f"Kicked by {ctx.author.name}#{ctx.author.discriminator} (ID {ctx.author.id}) for reason {reason}")
        await ctx.send(f">>> Successfully kicked <@!{member.id}> for **{reason}**.")
    except:
        await member.kick(reason=f"Kicked by {ctx.author.name}#{ctx.author.discriminator} (ID {ctx.author.id}) for reason {reason}")
        await ctx.send(f">>> Successfully kicked <@!{member.id}> for **{reason}**.\n:warning: I could not DM the user to inform of them of this kick, either due to their DMs being closed or them having blocked this bot.")

@client.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason: str):
    with open(f"{ctx.guild.id}logs.json", "a"): #Check if file exists, if not create it
        pass

    with open(f"{ctx.guild.id}logs.json") as logsf: #Open file
        logs = logsf.read()

        try: #Json -> Dict
            logs = json.loads(logs)
        except:
            logs = {}

    durmessage, duration = durationcalc.dur(reason)

    if duration == None:
        date = None
    else:
        date = str(durationcalc.expdate(start = datetime.now(), days = duration))

    reason = reason.split("-duration ")[0]

    try: #Logs the ban in server logs
        logs[str(member.id)][f"BAN-{idgen.new(6)}"] = {"reason": reason, "mod": ctx.author.id, "date": str(datetime.now()), "expires": date}
    except:
        logs[str(member.id)] = {}
        logs[str(member.id)][f"BAN-{idgen.new(6)}"] = {"reason": reason, "mod": ctx.author.id, "date":str(datetime.now()), "expires": date}
        
    with open(f"{ctx.guild.id}logs.json", "w") as logsf: #Dump back into json
        logs = json.dumps(logs, indent=4)
        logsf.write(logs)

    try:
        await member.send(f">>> You have been banned from the server **{ctx.guild.name}** for **{reason}**.\n:warning: This ban **{durmessage}**.")
        await member.ban(reason=f"Banned by {ctx.author.name}#{ctx.author.discriminator} (ID {ctx.author.id}) for reason {reason}. This ban {durmessage}.")
        await ctx.send(f">>> Successfully banned <@!{member.id}> for **{reason}**. This ban {durmessage}.")
    except:
        await member.ban(reason=f"Banned by {ctx.author.name}#{ctx.author.discriminator} (ID {ctx.author.id}) for reason {reason}. This ban {durmessage}.")
        await ctx.send(f">>> Successfully banned <@!{member.id}> for **{reason}**. This ban {durmessage}.\n:warning: I could not DM the user to inform of them of this ban, either due to their DMs being closed or them having blocked this bot.")

token = open("token.txt", "r").read()
client.run(token, log_handler=None)

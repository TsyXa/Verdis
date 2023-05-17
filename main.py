import discord
import json
from discord.ext import commands
from datetime import datetime
import random
import idgen
import durationcalc
from time import mktime
import asyncio
import os

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
    case = idgen.new(6)

    try: #Logs the warning in server logs
        logs[str(member.id)][f"WRN-{case}"] = {"reason": reason, "mod": ctx.author.id, "date": str(datetime.now()), "expires": date}
    except:
        logs[str(member.id)] = {}
        logs[str(member.id)][f"WRN-{case}"] = {"reason": reason, "mod": ctx.author.id, "date":str(datetime.now()), "expires": date}
        
    with open(f"{ctx.guild.id}logs.json", "w") as logsf: #Dump back into json
        logs = json.dumps(logs, indent=4)
        logsf.write(logs)
    
    try:
        await member.send(f">>> You have been warned in the server **{ctx.guild.name}** for **{reason}** with case ID `WRN-{case}`.\n:warning: This warning **{durmessage}**.")
        await ctx.send(f">>> Successfully warned <@!{member.id}> for **{reason}** with case ID `WRN-{case}`. This warning **{durmessage}**.")
    except:
        await ctx.send(f">>> Successfully warned <@!{member.id}> for **{reason}** with case ID `WRN-{case}`. This warning **{durmessage}**.\n:warning: I could not DM the user to inform of them of this warning, either due to their DMs being closed or them having blocked this bot.")

@client.command(aliases=["warnings"])
@commands.has_permissions(manage_messages=True)
async def logs(ctx, member: discord.Member = None):
    if member == None: #If member not inputted present ALL logs
        logstring = ">>> "
        try:
            with open(f"{ctx.guild.id}logs.json", "r") as f:
                logs = json.loads(f.read()) #Open logs file

            for i in logs:
                logstring += f"**User: <@!{i}>**\n" #Lists logs by user
                for j in logs[i]:
                    ts = lambda t : str(mktime(datetime.strptime(t, "%Y-%m-%d %H:%M:%S.%f").timetuple()))[:-2] #Function to turn datetime into unix
                    try:
                        expry = f"<t:{ts(logs[i][j]['expires'])}:R>" #Expiry date
                    except:
                        expry = "Never"

                    _type = ""

                    if j[:3] == "WRN":
                        _type = "Warning"
                    elif j[:3] == "TMO":
                        _type = "Timeout"
                    elif j[:3] == "KCK":
                        _type = "Kick"
                    elif j[:3] == "BAN":
                        _type = "Ban"
                    
                    #Adds each warning to the string
                    logstring += f"__{_type}__ - ID `{j}`\nModerator: <@!{logs[i][j]['mod']}>\nDate: <t:{ts(logs[i][j]['date'])}:f>\nExpires: {expry}\nReason: {logs[i][j]['reason']}\n\n"
                logstring += "\n"

            if logstring == ">>> ":
                await ctx.send("There are no logs for this server!")
                return
            
            while len(logstring) >= 2000: #Ensures messages can be sent and if not splits them up
                await ctx.send(logstring[:1999])
                logstring = ">>>", logstring[1999:]
            await ctx.send(logstring)
                
        except:
            await ctx.send("There are no logs for this server!")
            
    else:
        logstring = ">>> "
        try:
            with open(f"{ctx.guild.id}logs.json", "r") as f:
                logs = json.loads(f.read()) #Open logs file
            
            for j in logs[str(member.id)]:
                ts = lambda t : str(mktime(datetime.strptime(t, "%Y-%m-%d %H:%M:%S.%f").timetuple()))[:-2] #Function to turn datetime into unix
                try:
                    expry = f"<t:{ts(logs[str(member.id)][j]['expires'])}:R>" #Expiry date
                except:
                    expry = "Never"
                
                _type = ""
                if j[:3] == "WRN":
                    _type = "Warning"
                elif j[:3] == "TMO":
                    _type = "Timeout"
                elif j[:3] == "KCK":
                    _type = "Kick"
                elif j[:3] == "BAN":
                    _type = "Ban"

                #Adds each warning to the string
                logstring += f"__{_type}__ - ID `{j}`\nModerator: <@!{logs[str(member.id)][j]['mod']}>\nDate: <t:{ts(logs[str(member.id)][j]['date'])}:f>\nExpires: {expry}\nReason: {logs[str(member.id)][j]['reason']}\n\n"                
            
            while len(logstring) >= 2000: #Ensures messages can be sent and if not splits them up
                await ctx.send(logstring[:1999])
                logstring = ">>>", logstring[1999:]
            await ctx.send(logstring)

        except:
            await ctx.send("There are no logs for this user!")
    
@client.command(aliases=["mute"])
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
    case = idgen.new(6)

    try: #Logs the time out in server logs
        logs[str(member.id)][f"TMO-{case}"] = {"reason": reason, "mod": ctx.author.id, "date": str(datetime.now()), "expires": date}
    except:
        logs[str(member.id)] = {}
        logs[str(member.id)][f"TMO-{case}"] = {"reason": reason, "mod": ctx.author.id, "date":str(datetime.now()), "expires": date}
        
    with open(f"{ctx.guild.id}logs.json", "w") as logsf: #Dump back into json
        logs = json.dumps(logs, indent=4)
        logsf.write(logs)
    
    try:
        await member.send(f">>> You have been timed out in the server **{ctx.guild.name}** for **{reason}** with case ID `TMO-{case}`.\n:warning: This time out **{durmessage}**.")
        await member.timeout(duration, reason = f"Timed out by {ctx.author.name}#{ctx.author.discriminator} (ID {ctx.author.id}) for reason {reason} with case ID `TMO-{case}`. This time out {durmessage}.")
        await ctx.send(f">>> Successfully timed out <@!{member.id}> for **{reason}** with case ID `TMO-{case}`. This time out **{durmessage}**.")
    except:
        await member.timeout(duration, reason = f"Timed out by {ctx.author.name}#{ctx.author.discriminator} (ID {ctx.author.id}) for reason {reason} with case ID `TMO-{case}`. This time out {durmessage}.")
        await ctx.send(f">>> Successfully timed out <@!{member.id}> for **{reason}** with case ID `TMO-{case}`. This time out **{durmessage}**.\n:warning: I could not DM the user to inform of them of this time out, either due to their DMs being closed or them having blocked this bot.")

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
            
    case = idgen.new(6)

    try: #Logs the kick in server logs
        logs[str(member.id)][f"KCK-{case}"] = {"reason": reason, "mod": ctx.author.id, "date": str(datetime.now()), "expires": None}
    except:
        logs[str(member.id)] = {}
        logs[str(member.id)][f"KCK-{case}"] = {"reason": reason, "mod": ctx.author.id, "date":str(datetime.now()), "expires": None}
        
    with open(f"{ctx.guild.id}logs.json", "w") as logsf: #Dump back into json
        logs = json.dumps(logs, indent=4)
        logsf.write(logs)
    
    try:
        await member.send(f">>> You have been kicked from the server **{ctx.guild.name}** for **{reason}** with case ID `KCK-{case}`.\n:information_source: You may rejoin the server at any time.")
        await member.kick(reason=f"Kicked by {ctx.author.name}#{ctx.author.discriminator} (ID {ctx.author.id}) for reason {reason} with case ID `KCK-{case}`")
        await ctx.send(f">>> Successfully kicked <@!{member.id}> for **{reason}** with case ID `KCK-{case}`.")
    except:
        await member.kick(reason=f"Kicked by {ctx.author.name}#{ctx.author.discriminator} (ID {ctx.author.id}) for reason {reason} with case ID `KCK-{case}`")
        await ctx.send(f">>> Successfully kicked <@!{member.id}> for **{reason}** with case ID `KCK-{case}`.\n:warning: I could not DM the user to inform of them of this kick, either due to their DMs being closed or them having blocked this bot.")

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
    case = idgen.new(6)

    try: #Logs the ban in server logs
        logs[str(member.id)][f"BAN-{case}"] = {"reason": reason, "mod": ctx.author.id, "date": str(datetime.now()), "expires": date}
    except:
        logs[str(member.id)] = {}
        logs[str(member.id)][f"BAN-{case}"] = {"reason": reason, "mod": ctx.author.id, "date":str(datetime.now()), "expires": date}
        
    with open(f"{ctx.guild.id}logs.json", "w") as logsf: #Dump back into json
        logs = json.dumps(logs, indent=4)
        logsf.write(logs)

    try:
        await member.send(f">>> You have been banned from the server **{ctx.guild.name}** for **{reason}** with case ID `BAN-{case}`.\n:warning: This ban **{durmessage}**.")
        await member.ban(reason=f"Banned by {ctx.author.name}#{ctx.author.discriminator} (ID {ctx.author.id}) for reason {reason} with case ID `BAN-{case}`. This ban {durmessage}.")
        await ctx.send(f">>> Successfully banned <@!{member.id}> for **{reason}** with case ID `BAN-{case}`. This ban **{durmessage}**.")
    except:
        await member.ban(reason=f"Banned by {ctx.author.name}#{ctx.author.discriminator} (ID {ctx.author.id}) for reason {reason} with case ID `BAN-{case}`. This ban {durmessage}.")
        await ctx.send(f">>> Successfully banned <@!{member.id}> for **{reason}** with case ID `BAN-{case}`. This ban **{durmessage}**.\n:warning: I could not DM the user to inform of them of this ban, either due to their DMs being closed or them having blocked this bot.")

@client.command()
@commands.has_permissions(ban_members=True)
async def idban(ctx, user: discord.User, *, reason: str):
    with open(f"{ctx.guild.id}logs.json", "a"): #Check if file exists, if not create it
        pass

    with open(f"{ctx.guild.id}logs.json") as logsf: #Open file
        logs = logsf.read()

        try: #Json -> Dict
            logs = json.loads(logs)
        except:
            logs = {}

    duration = None #Sets variables manually rather than using the duration calculator
    date = None
    durmessage = "is permanent"
    case = case = idgen.new(6)

    try: #Logs the ban in server logs
        logs[str(user.id)][f"BAN-{case}"] = {"reason": reason, "mod": ctx.author.id, "date": str(datetime.now()), "expires": date}
    except:
        logs[str(user.id)] = {}
        logs[str(user.id)][f"BAN-{case}"] = {"reason": reason, "mod": ctx.author.id, "date":str(datetime.now()), "expires": date}
        
    with open(f"{ctx.guild.id}logs.json", "w") as logsf: #Dump back into json
        logs = json.dumps(logs, indent=4)
        logsf.write(logs)

    try:
        await user.send(f">>> You have been banned from the server **{ctx.guild.name}** for **{reason}** with case ID `BAN-{case}`.\n:warning: This ban **{durmessage}**.")
        await ctx.guild.ban(user, reason=f"Banned by {ctx.author.name}#{ctx.author.discriminator} (ID {ctx.author.id}) for reason {reason} with case ID `BAN-{case}`. This ban {durmessage}.")
        await ctx.send(f">>> Successfully banned <@!{user.id}> for **{reason}** with case ID `BAN-{case}`. This ban **{durmessage}**.")
    except:
        await ctx.guild.ban(user, reason=f"Banned by {ctx.author.name}#{ctx.author.discriminator} (ID {ctx.author.id}) for reason {reason} with case ID `BAN-{case}`. This ban {durmessage}.")
        await ctx.send(f">>> Successfully banned <@!{user.id}> for **{reason}** with case ID `BAN-{case}`. This ban **{durmessage}**.\n:warning: I could not DM the user to inform of them of this ban, either due to their DMs being closed or them having blocked this bot.")

@client.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, user: discord.User, case = f"BAN-{idgen.new(6)}"):
    with open(f"{ctx.guild.id}logs.json", "a"): #Check if file exists, if not create it
        pass

    with open(f"{ctx.guild.id}logs.json") as logsf: #Open file
        logs = logsf.read()

        try: #Json -> Dict
            logs = json.loads(logs)
        except:
            logs = {}
            
    try: #Logs the unban in server logs
        logs[str(user.id)][f"{case}"]["expires"] = str(datetime.now())
    except:
        logs[str(user.id)] = {}
        logs[str(user.id)][f"{case}"] = {"reason": None, "mod": None, "date": None, "expires": str(datetime.now())}
        
    with open(f"{ctx.guild.id}logs.json", "w") as logsf: #Dump back into json
        logs = json.dumps(logs, indent=4)
        logsf.write(logs)
        
    try:
        await user.send(f">>> You have been unbanned from the server **{ctx.guild.name}** (case ID `{case}`). You may rejoin at any time.")
        await ctx.guild.unban(user, reason = f"Unbanned by {ctx.author.name}#{ctx.author.discriminator} (ID {ctx.author.id})  (case ID {case})")
        await ctx.send(f">>> Successfully unbanned <@!{user.id}> (case ID `{case}`).")
    except:
        await ctx.guild.unban(user, reason=f"=Unbanned by {ctx.author.name}#{ctx.author.discriminator} (ID {ctx.author.id}) (case ID `{case}`).")
        await ctx.send(f">>> Successfully unbanned <@!{user.id}> (case ID `{case}`).\n:warning: I could not DM the user to inform of them of this unban, either due to their DMs being closed or them having blocked this bot.")

@client.command(aliases=["clearlog", "clearlogs", "clearwarns", "clearwarning", "clearwarnings"])
@commands.has_permissions(kick_members=True)
async def clearwarn(ctx, member: discord.Member = None, case = None):
    with open(f"{ctx.guild.id}logs.json", "a"): #Check if file exists, if not create it
                pass

    with open(f"{ctx.guild.id}logs.json") as logsf: #Open file
        logs = logsf.read()

        try: #Json -> Dict
            logs = json.loads(logs)
        except:
            await ctx.send(":x: There aren't any logs for this server!")
            return

    if member != None: #If member specified
        if case == None: #If no specific case
            del logs[str(member.id)] #Clear all
            await ctx.send(f"Successfully removed all logs for user <@!{member.id}>")

        else: #If case specified
            try:
                del logs[str(member.id)][case] #Clear specific case
                await ctx.send(f"Successfully removed case `{case}` from user <@!{member.id}>.")
            except:
                await ctx.send(f":x: Sorry, I could not find case `{case}` for user <@!{member.id}>.\n:bulb: Case IDs are case-sensitive. Make sure you used capital letters where necessary.")

    else: #If clear ALL logs
        checkmsg = await ctx.send(":information_source: Are you sure you want to remove **all** logs for this server? This action is **irreversible**.\nReact with :white_check_mark: to continue (auto cancel in 5s).")
        await checkmsg.add_reaction("✅")

        def claimCheck(reaction, user): #Check to confirm delete all logs
            return reaction.message.id == checkmsg.id and reaction.emoji == "✅" and not user.bot
        
        try:
            reaction, user = await client.wait_for("reaction_add", check=claimCheck, timeout=5)
        except asyncio.TimeoutError: #If no reaction within 5s
            await checkmsg.edit(content=":x: Clear all server logs cancelled")
        else:
            try:
                logs = {}
                await checkmsg.edit(content="All server logs deleted.")
            except: #If there is no logs file
                await checkmsg.edit(content=":x: There aren't any logs for this server!")

    with open(f"{ctx.guild.id}logs.json", "w") as logsf: #Dump back into json
        logs = json.dumps(logs, indent=4)
        logsf.write(logs)

token = open("token.txt", "r").read()
client.run(token, log_handler=None)

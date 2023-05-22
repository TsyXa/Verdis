import discord
import json
from discord.ext import commands
from datetime import datetime
import idgen
import durationcalc
from time import mktime, time as unix
import asyncio
import sqlite3 as sql
from math import floor

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
    #Set up logs database
    logs = sql.connect(f"{ctx.guild.id}.db")
    cursor = logs.cursor()
    try:
        cursor.execute("""CREATE TABLE logs (
                        log_id text,
                        user_id integer,
                        mod_id integer,
                        reason text,
                        date integer,
                        expires integer
                        )""")
    except sql.OperationalError: #If db already exists
        pass

    durmessage, duration = durationcalc.dur(reason)

    if duration == 0:
        date = 0
    else:
        date = floor(unix() + duration) #Calculate expiry date

    reason = reason.split("-duration ")[0] #Remove duration from reason message
    case = idgen.new(6) #Create case number

    #Update and close logs database
    cursor.execute(f"INSERT INTO logs VALUES ('WRN-{case}', {member.id}, {ctx.author.id}, '{reason}', {floor(unix())}, {date})")
    logs.commit()
    logs.close()

    try:
        await member.send(f">>> You have been warned in the server **{ctx.guild.name}** for **{reason}** with case ID `WRN-{case}`.\n:warning: This warning **{durmessage}**.")
        await ctx.send(f">>> Successfully warned <@!{member.id}> for **{reason}** with case ID `WRN-{case}`. This warning **{durmessage}**.")
    except:
        await ctx.send(f">>> Successfully warned <@!{member.id}> for **{reason}** with case ID `WRN-{case}`. This warning **{durmessage}**.\n:warning: I could not DM the user to inform of them of this warning, either due to their DMs being closed or them having blocked this bot.")

@client.command(aliases=["warnings"])
@commands.has_permissions(manage_messages=True)
async def logs(ctx, member: discord.Member = None):
    #Set up logs database
    logs = sql.connect(f"{ctx.guild.id}.db")
    cursor = logs.cursor()
    try:
        cursor.execute("""CREATE TABLE logs (
                        log_id text,
                        user_id integer,
                        mod_id integer,
                        reason text,
                        date integer,
                        expires integer
                        )""")
        await ctx.send("There are no logs for this server!")
        return
    except sql.OperationalError: #If db already exists
        pass

    logstring = ">>> "

    if member == None: #If member not inputted present ALL logs
        cursor.execute(f"SELECT * FROM logs")
    else:
        cursor.execute(f"SELECT * FROM logs WHERE user_id = {member.id}")

    loglist = cursor.fetchall()

    if len(loglist) == 0: #If list is empty
        await ctx.send("There are no logs for this server!")
        return
    
    print (loglist)
    for i in loglist:
        _type = ""
        if i[0][:3] == "WRN":
            _type = "Warning"
        elif i[0][:3] == "TMO":
            _type = "Timeout"
        elif i[0][:3] == "KCK":
            _type = "Kick"
        elif i[0][:3] == "BAN":
            _type = "Ban"
        
        #Format both initial and expiry dates
        date, expiry = i[4], i[5]
        if date == 0: 
            date = "Unknown"
        if expiry == 0:
            expiry = "Never"
        else:
            expiry = f"<t:{expiry}:f>"

        #Adds the warning to the string and repeats
        logstring += f"**Case ID** - `{i[0]}` ({_type})\nUser: <@!{i[1]}>\nModerator: <@!{i[2]}>\nReason: {i[3]}\nDate: <t:{date}:f>\nExpires: {expiry}\n\n"

    if logstring == ">>> ":
        if member.id == None:
            await ctx.send("There are no logs for this server!")
        else:
            await ctx.send("There are no logs for this user!")
        return
    
    while len(logstring) >= 2000: #Ensures messages can be sent and if not splits them up
        await ctx.send(logstring[:1999])
        logstring = ">>>", logstring[1999:]
    await ctx.send(logstring)
            
    logs.close()
    
@client.command(aliases=["mute"])
@commands.has_permissions(moderate_members=True)
async def timeout(ctx, member: discord.Member, duration, *, reason: str):
    #Set up logs database
    logs = sql.connect(f"{ctx.guild.id}.db")
    cursor = logs.cursor()
    try:
        cursor.execute("""CREATE TABLE logs (
                        log_id text,
                        user_id integer,
                        mod_id integer,
                        reason text,
                        date integer,
                        expires integer
                        )""")
    except sql.OperationalError: #If db already exists
        pass

    durmessage, duration, todur = durationcalc.to_dur(duration)

    date = floor(unix() + duration) #Calculate expiry date

    reason = reason.split("-duration ")[0] #Remove duration from reason message
    case = idgen.new(6) #Create case number

    #Update and close logs database
    cursor.execute(f"INSERT INTO logs VALUES ('TMO-{case}', {member.id}, {ctx.author.id}, '{reason}', {floor(unix())}, {date})")
    logs.commit()
    logs.close()
    
    try:
        await member.send(f">>> You have been timed out in the server **{ctx.guild.name}** for **{reason}** with case ID `TMO-{case}`.\n:warning: This time out **{durmessage}**.")
        await member.timeout(todur, reason = f"Timed out by {ctx.author.name}#{ctx.author.discriminator} (ID {ctx.author.id}) for reason {reason} with case ID `TMO-{case}`. This time out {durmessage}.")
        await ctx.send(f">>> Successfully timed out <@!{member.id}> for **{reason}** with case ID `TMO-{case}`. This time out **{durmessage}**.")
    except:
        await member.timeout(todur, reason = f"Timed out by {ctx.author.name}#{ctx.author.discriminator} (ID {ctx.author.id}) for reason {reason} with case ID `TMO-{case}`. This time out {durmessage}.")
        await ctx.send(f">>> Successfully timed out <@!{member.id}> for **{reason}** with case ID `TMO-{case}`. This time out **{durmessage}**.\n:warning: I could not DM the user to inform of them of this time out, either due to their DMs being closed or them having blocked this bot.")

@client.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason: str):
    #Set up logs database
    logs = sql.connect(f"{ctx.guild.id}.db")
    cursor = logs.cursor()
    try:
        cursor.execute("""CREATE TABLE logs (
                        log_id text,
                        user_id integer,
                        mod_id integer,
                        reason text,
                        date integer,
                        expires integer
                        )""")
    except sql.OperationalError: #If db already exists
        pass

    case = idgen.new(6) #Create case number

    #Update and close logs database
    cursor.execute(f"INSERT INTO logs VALUES ('KCK-{case}', {member.id}, {ctx.author.id}, '{reason}', {floor(unix())}, 0)")
    logs.commit()
    logs.close()

    try:
        await member.send(f">>> You have been kicked from the server **{ctx.guild.name}** for **{reason}** with case ID `KCK-{case}`.\n:information_source: You may rejoin the server at any time.")
        await member.kick(reason=f"Kicked by {ctx.author.name}#{ctx.author.discriminator} (ID {ctx.author.id}) for reason {reason} with case ID `KCK-{case}`")
        await ctx.send(f">>> Successfully kicked <@!{member.id}> for **{reason}** with case ID `KCK-{case}`.")
    except:
        await member.kick(reason=f"Kicked by {ctx.author.name}#{ctx.author.discriminator} (ID {ctx.author.id}) for reason {reason} with case ID `KCK-{case}`")
        await ctx.send(f">>> Successfully kicked <@!{member.id}> for **{reason}** with case ID `KCK-{case}`.\n:warning: I could not DM the user to inform of them of this kick, either due to their DMs being closed or them having blocked this bot.")

@client.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, user: discord.User, *, reason: str):
    #Set up logs database
    logs = sql.connect(f"{ctx.guild.id}.db")
    cursor = logs.cursor()
    try:
        cursor.execute("""CREATE TABLE logs (
                        log_id text,
                        user_id integer,
                        mod_id integer,
                        reason text,
                        date integer,
                        expires integer
                        )""")
    except sql.OperationalError: #If db already exists
        pass

    durmessage, duration = durationcalc.dur(reason)

    if duration == 0:
        date = 0
    else:
        date = floor(unix() + duration) #Calculate expiry date

    reason = reason.split("-duration ")[0] #Remove duration from reason message
    case = idgen.new(6) #Create case number

    #Update and close logs database
    cursor.execute(f"INSERT INTO logs VALUES ('BAN-{case}', {user.id}, {ctx.author.id}, '{reason}', {floor(unix())}, {date})")
    logs.commit()
    logs.close()

    try:
        await user.send(f">>> You have been banned from the server **{ctx.guild.name}** for **{reason}** with case ID `BAN-{case}`.\n:warning: This ban **{durmessage}**.")
        await ctx.guild.ban(user, reason=f"Banned by {ctx.author.name}#{ctx.author.discriminator} (ID {ctx.author.id}) for reason {reason} with case ID `BAN-{case}`. This ban {durmessage}.")
        await ctx.send(f">>> Successfully banned <@!{user.id}> for **{reason}** with case ID `BAN-{case}`. This ban **{durmessage}**.")
    except:
        await ctx.guild.ban(user, reason=f"Banned by {ctx.author.name}#{ctx.author.discriminator} (ID {ctx.author.id}) for reason {reason} with case ID `BAN-{case}`. This ban {durmessage}.")
        await ctx.send(f">>> Successfully banned <@!{user.id}> for **{reason}** with case ID `BAN-{case}`. This ban **{durmessage}**.\n:warning: I could not DM the user to inform of them of this ban, either due to their DMs being closed or them having blocked this bot.")

@client.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, user: discord.User, case = None):
    #Set up logs database
    logs = sql.connect(f"{ctx.guild.id}.db")
    cursor = logs.cursor()
    try:
        cursor.execute("""CREATE TABLE logs (
                        log_id text,
                        user_id integer,
                        mod_id integer,
                        reason text,
                        date integer,
                        expires integer
                        )""")
    except sql.OperationalError: #If db already exists
        pass

    date = floor(unix())

    #Update and close logs database
    cursor.execute(f"SELECT * FROM logs WHERE log_id = '{case}'") #Test if log ID is valid
    if case == None or cursor.fetchone() == None:
        case = f"BAN-{idgen.new(6)}"
        cursor.execute(f"INSERT INTO logs VALUES ('{case}', {user.id}, 0, 'UNKNOWN', 0, {floor(unix())})")
    else:
        cursor.execute(f"UPDATE logs SET expires = {date} WHERE log_id = '{case}' AND user_id = {user.id}")

    logs.commit()
    logs.close()

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
    #Set up logs database
    logs = sql.connect(f"{ctx.guild.id}.db")
    cursor = logs.cursor()
    try:
        cursor.execute("""CREATE TABLE logs (
                        log_id text,
                        user_id integer,
                        mod_id integer,
                        reason text,
                        date integer,
                        expires integer
                        )""")
    except sql.OperationalError: #If db already exists
        pass

    if member != None: #If member specified
        if case == None: #If no specific case
            cursor.execute(f"DELETE FROM logs WHERE user_id = {member.id}")
            await ctx.send(f"Successfully removed all logs for user <@!{member.id}>")

        else: #If case specified
            try:
                cursor.execute(f"DELETE FROM logs WHERE user_id = {member.id} AND log_id = '{case}'")
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
                cursor.execute(f"DROP TABLE logs")
                await checkmsg.edit(content="All server logs deleted.")
            except: #If there is no logs file
                await checkmsg.edit(content=":x: There aren't any logs for this server!")

    #Update and close logs database
    logs.commit()
    logs.close()

token = open("token.txt", "r").read()
client.run(token, log_handler=None)

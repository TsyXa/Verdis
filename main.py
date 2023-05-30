import discord
from discord import app_commands
from discord.ext import commands
import idgen
import durationcalc
from time import time as unix
import asyncio
import sqlite3 as sql
from math import floor
from json import loads

client = commands.Bot(intents = discord.Intents.all(), command_prefix = "!", allowed_mentions=discord.AllowedMentions(roles=False, users=False, everyone=False))

#SQL Setup
def sql_setup(ctx, table):
    if table == "logs":
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
        return logs, cursor
        
@client.event
async def on_ready():
    print("Client Ready")
    try: #Sync slash commands
        await client.tree.sync()
        print("Command tree synced successfully")
    except Exception as error:
        print("Error syncing command tree:\n" + error)

@client.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, commands.MissingPermissions):
        await interaction.response.send_message(f"> :x: You cannot do that! Required permissions: `{error.missing_permissions}`")
    elif isinstance(error, commands.BotMissingPermissions):
        await interaction.response.send_message(f">>> :x: I cannot do that! I require the following permissions: `{error.missing_permissions}`\n:bulb: Try moving my role above all others, or toggling `Administrator` permissions to True.")
    elif isinstance(error, commands.MemberNotFound):
        await interaction.response.send_message(f">>> :x: I could not find the user `{error.argument}`.\n:bulb: Try tagging the user, or using their User ID.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await interaction.response.send_message(f"> :x: You forgot to input the following arguments: `{error.param}`")
    elif isinstance(error, commands.MemberNotFound):
        await interaction.response.send_message(f">>> :x: I could not find the user `{error.argument}`.\n:bulb: Try tagging the user, or using their User ID.")
    elif isinstance(error, commands.UserNotFound):
        await interaction.response.send_message(f">>> :x: I could not find the user `{error.argument}`.\n:bulb: Try tagging the user, or using their User ID.")
    elif isinstance(error, commands.ChannelNotFound):
        await interaction.response.send_message(f">>> :x: I could not find the channel `{error.argument}`.\n:bulb: Try tagging the channel, or using its Channel ID.")
    elif isinstance(error, commands.CommandNotFound):
        return
    else:
        await interaction.response.send_message(f">>> :x: **Unexpected Error**\nAn error occurred. Please report this message to <@!476457324609929226> along with the original command you entered.```\n{error}\n```")

@client.tree.command(name="help", description="Provides a list of commands or info about a specific command")
@app_commands.describe(cmd="Info about a specific command")
async def help(interaction: discord.Interaction, cmd: str = None):
    with open("commandlist.json") as clist: #Open commands list
            clist = clist.read()
            clist = loads(clist)

    if cmd == None: #If no command specified
        cstring = ">>> :tools: **Command List**"
        for i in clist:
            cstring += f"\n`/{i}` - {clist[i][0]}" #Add each command to the string
        cstring += "\n\n:bulb: For more information on a specific command, use `/help (command)`"
        await interaction.response.send_message(cstring, ephemeral = True) #Show all commands

    else:
        cmd = cmd.replace("/", "").lower()

        try:
            await interaction.response.send_message(f">>> :tools: `/{cmd}` **Command Help**\n\n`{clist[cmd][1]}` - {clist[cmd][0]}", ephemeral = True)
        except:
            await interaction.response.send_message(f">>> :x: Sorry, I could not find the command `{cmd}`.\n:bulb: Have you spelt the command correctly? Use `/help` to check the command list and try again.", ephemeral = True)

@client.tree.command(name="warn", description="Warn a user")
@app_commands.describe(member="The member to warn", reason = "The reason for the warning", duration = "How long the warning should last")
@commands.has_permissions(manage_messages=True)
async def warn(interaction: discord.Interaction, member: discord.Member, reason: str, duration: str = None):
    #Set up logs database
    logs, cursor = sql_setup(interaction, "logs")

    durmessage, duration = durationcalc.dur(duration)

    if duration == 0:
        date = 0
    else:
        date = floor(unix() + duration) #Calculate expiry date

    case = idgen.new(6) #Create case number

    #Update and close logs database
    cursor.execute(f"INSERT INTO logs VALUES ('WRN-{case}', {member.id}, {interaction.user.id}, '{reason}', {floor(unix())}, {date})")
    logs.commit()
    logs.close()

    try:
        await member.send(f">>> You have been warned in the server **{interaction.guild.name}** for **{reason}** with case ID `WRN-{case}`.\n:warning: This warning **{durmessage}**.")
        await interaction.response.send_message(f">>> Successfully warned <@!{member.id}> for **{reason}** with case ID `WRN-{case}`. This warning **{durmessage}**.")
    except:
        await interaction.response.send_message(f">>> Successfully warned <@!{member.id}> for **{reason}** with case ID `WRN-{case}`. This warning **{durmessage}**.\n:warning: I could not DM the user to inform of them of this warning, either due to their DMs being closed or them having blocked this bot.")

@client.tree.command(name="logs", description="View all logs for the server or an individual user")
@app_commands.describe(member="The member to view")
@commands.has_permissions(manage_messages=True)
async def logs(interaction: discord.Interaction, member: discord.Member = None):
    #Set up logs database
    logs, cursor = sql_setup(interaction, "logs")

    logstring = ">>> "

    if member == None: #If member not inputted present ALL logs
        cursor.execute(f"SELECT * FROM logs")
    else:
        cursor.execute(f"SELECT * FROM logs WHERE user_id = {member.id}")

    loglist = cursor.fetchall()

    if len(loglist) == 0: #If list is empty
        if member == None:
            await interaction.response.send_message("> :x: There are no logs for this server!")
        else:
            await interaction.response.send_message("> :x: There are no logs for this user!")
        return

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
        mod, date, expiry = i[2], i[4], i[5]
        if date == 0: 
            date = "Unknown"
        else:
            date = f"<t:{date}:f>"

        if mod == 0:
            mod = "Unknown"
        else:
            mod = f"<@!{mod}>"

        if expiry == 0:
            expiry = "Never"
        else:
            expiry = f"<t:{expiry}:f>"

        #Adds the warning to the string and repeats
        logstring += f"**Case ID** - `{i[0]}` ({_type})\nUser: <@!{i[1]}>\nModerator: {mod}\nReason: {i[3]}\nDate: {date}\nExpires: {expiry}\n\n"
    
    await interaction.response.send_message(logstring)
            
    logs.close()
    
@client.tree.command(name="timeout", description="Time out a user for a specified period of time")
@app_commands.describe(member="The member to timeout", reason="The reason for the timeout", duration="How long the timeout should last for (max 28d)")
@commands.has_permissions(moderate_members=True)
async def timeout(interaction: discord.Interaction, member: discord.Member, reason: str, duration: str):
    #Set up logs database
    logs, cursor = sql_setup(interaction, "logs")

    durmessage, duration, todur = durationcalc.to_dur(duration)

    date = floor(unix() + duration) #Calculate expiry date

    case = idgen.new(6) #Create case number

    #Update and close logs database
    cursor.execute(f"INSERT INTO logs VALUES ('TMO-{case}', {member.id}, {interaction.user.id}, '{reason}', {floor(unix())}, {date})")
    logs.commit()
    logs.close()
    
    try:
        await member.send(f">>> You have been timed out in the server **{interaction.guild.name}** for **{reason}** with case ID `TMO-{case}`.\n:warning: This time out **{durmessage}**.")
        await member.timeout(todur, reason = f"Timed out by {interaction.user.name}#{interaction.user.discriminator} (ID {interaction.user.id}) for reason {reason} with case ID `TMO-{case}`. This time out {durmessage}.")
        await interaction.response.send_message(f">>> Successfully timed out <@!{member.id}> for **{reason}** with case ID `TMO-{case}`. This time out **{durmessage}**.")
    except:
        await member.timeout(todur, reason = f"Timed out by {interaction.user.name}#{interaction.user.discriminator} (ID {interaction.user.id}) for reason {reason} with case ID `TMO-{case}`. This time out {durmessage}.")
        await interaction.response.send_message(f">>> Successfully timed out <@!{member.id}> for **{reason}** with case ID `TMO-{case}`. This time out **{durmessage}**.\n:warning: I could not DM the user to inform of them of this time out, either due to their DMs being closed or them having blocked this bot.")

@client.tree.command(name="untimeout", description="Untime out a user")
@app_commands.describe(member="The member to target", case="The Verdis Case ID of the original ban")
@commands.has_permissions(moderate_members=True)
async def untimeout(interaction: discord.Interaction, member: discord.Member, case: str = None):
    #Set up logs database
    logs, cursor = sql_setup(interaction, "logs")

    date = floor(unix())

    #Update and close logs database
    cursor.execute(f"SELECT * FROM logs WHERE log_id = '{case}' AND user_id = {member.id}") #Test if log ID is valid
    if case == None or cursor.fetchone() == []:
        case = f"TMO-{idgen.new(6)}"
        cursor.execute(f"INSERT INTO logs VALUES ('{case}', {member.id}, 0, 'Unknown', 0, {floor(unix())})")
    else:
        cursor.execute(f"UPDATE logs SET expires = {date} WHERE log_id = '{case}' AND user_id = {member.id}")

    logs.commit()
    logs.close()
    
    await member.timeout(None, reason=f"Time out removed by {interaction.user.name}#{interaction.user.discriminator} (ID {interaction.user.id}) (case ID `{case}`).")
    await interaction.response.send_message(f">>> Successfully removed timeout for <@!{member.id}> (case ID `{case}`).")
    
@client.tree.command(name="kick", description="Kick a user")
@app_commands.describe(member="The member to kick", reason="The reason for the kick")
@commands.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str):
    #Set up logs database
    logs, cursor = sql_setup(interaction, "logs")

    case = idgen.new(6) #Create case number

    #Update and close logs database
    cursor.execute(f"INSERT INTO logs VALUES ('KCK-{case}', {member.id}, {interaction.user.id}, '{reason}', {floor(unix())}, 0)")
    logs.commit()
    logs.close()

    try:
        await member.send(f">>> You have been kicked from the server **{interaction.guild.name}** for **{reason}** with case ID `KCK-{case}`.\n:information_source: You may rejoin the server at any time.")
        await member.kick(reason=f"Kicked by {interaction.user.name}#{interaction.user.discriminator} (ID {interaction.user.id}) for reason {reason} with case ID `KCK-{case}`")
        await interaction.response.send_message(f">>> Successfully kicked <@!{member.id}> for **{reason}** with case ID `KCK-{case}`.")
    except:
        await member.kick(reason=f"Kicked by {interaction.user.name}#{interaction.user.discriminator} (ID {interaction.user.id}) for reason {reason} with case ID `KCK-{case}`")
        await interaction.response.send_message(f">>> Successfully kicked <@!{member.id}> for **{reason}** with case ID `KCK-{case}`.\n:warning: I could not DM the user to inform of them of this kick, either due to their DMs being closed or them having blocked this bot.")

@client.tree.command(name="ban", description="Ban a user")
@app_commands.describe(user="The user to ban", reason="The reason for the ban", duration="How long the ban should last for")
@commands.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, user: discord.User, reason: str, duration: str = None):
    #Set up logs database
    logs, cursor = sql_setup(interaction, "logs")

    durmessage, duration = durationcalc.dur(duration)

    if duration == 0:
        date = 0
    else:
        date = floor(unix() + duration) #Calculate expiry date

    case = idgen.new(6) #Create case number

    #Update and close logs database
    cursor.execute(f"INSERT INTO logs VALUES ('BAN-{case}', {user.id}, {interaction.user.id}, '{reason}', {floor(unix())}, {date})")
    logs.commit()
    logs.close()

    try:
        await user.send(f">>> You have been banned from the server **{interaction.guild.name}** for **{reason}** with case ID `BAN-{case}`.\n:warning: This ban **{durmessage}**.")
        await interaction.guild.ban(user, reason=f"Banned by {interaction.user.name}#{interaction.user.discriminator} (ID {interaction.user.id}) for reason {reason} with case ID `BAN-{case}`. This ban {durmessage}.")
        await interaction.response.send_message(f">>> Successfully banned <@!{user.id}> for **{reason}** with case ID `BAN-{case}`. This ban **{durmessage}**.")
    except:
        await interaction.guild.ban(user, reason=f"Banned by {interaction.user.name}#{interaction.user.discriminator} (ID {interaction.user.id}) for reason {reason} with case ID `BAN-{case}`. This ban {durmessage}.")
        await interaction.response.send_message(f">>> Successfully banned <@!{user.id}> for **{reason}** with case ID `BAN-{case}`. This ban **{durmessage}**.\n:warning: I could not DM the user to inform of them of this ban, either due to their DMs being closed or them having blocked this bot.")

@client.tree.command(name="unban", description="Unban a user")
@app_commands.describe(user="The user to unban", case="The Verdis Case ID of the original ban")
@commands.has_permissions(ban_members=True)
async def unban(interaction: discord.Interaction, user: discord.User, case: str = None):
    #Set up logs database
    logs, cursor = sql_setup(interaction, "logs")

    date = floor(unix())

    #Update and close logs database
    cursor.execute(f"SELECT * FROM logs WHERE log_id = '{case}' AND user_id = '{user.id}'") #Test if log ID is valid
    if case == None or cursor.fetchone() == []:
        case = f"BAN-{idgen.new(6)}"
        cursor.execute(f"INSERT INTO logs VALUES ('{case}', {user.id}, 0, 'Unknown', 0, {floor(unix())})")
    else:
        cursor.execute(f"UPDATE logs SET expires = {date} WHERE log_id = '{case}' AND user_id = {user.id}")

    logs.commit()
    logs.close()

    try:
        await user.send(f">>> You have been unbanned from the server **{interaction.guild.name}** (case ID `{case}`). You may rejoin at any time.")
        await interaction.guild.unban(user, reason = f"Unbanned by {interaction.user.name}#{interaction.user.discriminator} (ID {interaction.user.id})  (case ID {case})")
        await interaction.response.send_message(f">>> Successfully unbanned <@!{user.id}> (case ID `{case}`).")
    except:
        await interaction.guild.unban(user, reason=f"=Unbanned by {interaction.user.name}#{interaction.user.discriminator} (ID {interaction.user.id}) (case ID `{case}`).")
        await interaction.response.send_message(f">>> Successfully unbanned <@!{user.id}> (case ID `{case}`).\n:warning: I could not DM the user to inform of them of this unban, either due to their DMs being closed or them having blocked this bot.")

@client.tree.command(name="clearlogs", description="Clear a specific log, logs for a specific user or all logs for the server")
@app_commands.describe(user="The member to target", case="The Verdis Case ID of the original log")
@commands.has_permissions(kick_members=True)
async def clearlogs(interaction: discord.Interaction, user: discord.User = None, case: str = None):
    #Set up logs database
    logs, cursor = sql_setup(interaction, "logs")
    
    if case != None: #If case specified
        try:
            cursor.execute(f"SELECT user_id FROM logs WHERE log_id = '{case}'")
            userid = cursor.fetchone()[0]
            cursor.execute(f"DELETE FROM logs WHERE log_id = '{case}'")
            await interaction.response.send_message(f"> :wastebasket: Successfully removed case `{case}` from user <@!{userid}>.")
        except:
            await interaction.response.send_message(f">>> :x: Sorry, I could not find case `{case}` for this server.\n:bulb: Case IDs are case-sensitive. Make sure you used capital letters where necessary.")

    elif user != None: #If member specified but no case
        cursor.execute(f"DELETE FROM logs WHERE user_id = {user.id}")
        await interaction.response.send_message(f"> :wastebasket: Successfully removed all logs for user <@!{user.id}>")

    else: #If no member OR case specified 
        await interaction.response.send_message(">>> :information_source: Are you sure you want to remove **all** logs for this server? This action is **irreversible**.\nReact with :white_check_mark: to continue (auto cancel in 5s).")
        checkmsg = await interaction.original_response()
        await checkmsg.add_reaction("✅")

        def claimCheck(reaction, ruser): #Check to confirm delete all logs
            return reaction.message.id == checkmsg.id and reaction.emoji == "✅" and ruser.id == interaction.user.id and not ruser.bot
        
        try:
            reaction, ruser = await client.wait_for("reaction_add", check=claimCheck, timeout=5)
        except asyncio.TimeoutError: #If no reaction within 5s
            await checkmsg.edit(content="> :x: Clear all server logs cancelled")
        else:
            try:
                cursor.execute(f"DROP TABLE logs")
                await checkmsg.edit(content="> :wastebasket: All server logs deleted.")
            except: #If there is no logs file
                await checkmsg.edit(content="> :x: There aren't any logs for this server!")

    #Update and close logs database
    logs.commit()
    logs.close()

token = open("token.txt", "r").read()
client.run(token, log_handler=None)

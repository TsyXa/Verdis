import sqlite3 as sql

#Connect to a server's database
def setup(ctx, table):
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
    
#Sanitise Case ID inputs
def caseID(cursor, case, cmd = None):
    if case[:3] not in ["WRN", "TMO", "KCK", "BAN"] or len(case) != 10: #Format + length check
        return False
    
    #Look up table checks
    if cmd != None: 
        if case[:3] != cmd:
            return False
        
    cursor.execute("SELECT 'log_id' FROM logs")
    loglist = cursor.fetchall()

    if case not in loglist:
        return False
    
    return True

async def invalid_id(client, interaction, cmd):
    devlogs = client.get_channel(1097947670070427818)
    await devlogs.send(f"## SQL Error Detected ##\nUser: <@!{interaction.user.id}> (`{interaction.user.id}`)\nCommand: `{interaction.command.name}`\nMessage: `{cmd}`\nGuild ID: `{interaction.guild.id}`")
    await interaction.response.send_message("> :x: **Invalid case ID**, I am unable to execute this command.")

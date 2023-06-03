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

#Sanitise reason inputs
def reason(reason):
    if reason.find("DROP TABLE") != -1:
        return False
    if reason.find("UNION SELECT") != -1:
        return False
    if reason.find(".txt") != -1:
        return False
    if reason.find(".py") != -1:
        return False
    if reason.find(".json") != -1:
        return False
    if reason.find(".js") != -1:
        return False
    if reason.find(".exe") != -1:
        return False
    if reason.find(";") != -1:
        return False
    
    return True

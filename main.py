import discord
import json
from discord.ext import commands
from datetime import datetime
import random
import idgen

client = commands.Bot(intents = discord.Intents.all(), command_prefix = "!", allowed_mentions=discord.AllowedMentions(roles=False, users=False, everyone=False))

@client.event
async def on_ready():
    print("Client Ready")

@client.command()
async def warn(ctx, member: discord.Member, *, reason: str):
    with open(f"{ctx.guild.id}logs.json", "a"): #Check if file exists, if not create it
        pass

    with open(f"{ctx.guild.id}logs.json") as logsf: #Open file
        logs = logsf.read()

        try: #Json -> Dict
            logs = json.loads(logs)
        except:
            logs = {}

    try: #Logs the warning in server logs
        logs[str(member.id)][f"WRN-{idgen.new(6)}"] = {"reason": reason, "mod": ctx.author.id, "date": str(datetime.now()), "expires": None}
    except:
        logs[str(member.id)] = {}
        logs[str(member.id)][f"WRN-{idgen.new(6)}"] = {"reason": reason, "mod": ctx.author.id, "date":str(datetime.now()), "expires": None}
        
    with open(f"{ctx.guild.id}logs.json", "w") as logsf: #Dump back into json
        logs = json.dumps(logs, indent=4)
        logsf.write(logs)
    
    try:
        await member.send(f">>> You have been warned in the server **{ctx.guild.name}** for **{reason}**.\n:warning: This warning is **permanent**.")
        await ctx.send(f">>> Successfully warned <@!{member.id}> for **{reason}**.")
    except:
        await ctx.send(f">>> Successfully warned <@!{member.id}> for **{reason}**.\n:warning: I could not DM the user to inform of them of this warning, either due to their DMs being closed or them having blocked this bot.")

@warn.error
async def warn_error(ctx, error):
    await ctx.send(error)

token = open("token.txt", "r").read()

client.run(token, log_handler=None)

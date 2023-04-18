import discord
from discord.ext import commands
import logging

client = commands.Bot(intents = discord.Intents.all(), command_prefix = "!", allowed_mentions=discord.AllowedMentions(roles=False, users=False, everyone=False))
@client.event
async def on_connect():
    print("Client Connected")

@client.command()
async def test(ctx, *, inp):
    await ctx.send(inp)

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
token = open("token.txt", "r").read()

client.run(token, log_handler=None)

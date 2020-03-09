import discord
from discord.ext import commands
import random

client = commands.Bot(command_prefix='//')
client.run("Njg2Mzk1ODU0NjU5MTI1MzQ1.XmWoXA.mzQOJaPytBGPMmu8x77PREFViOQ")


@client.event
async def on_ready():
    # console message to confirm bot has logged in
    print('We have logged in as {0.user}'.format(client))

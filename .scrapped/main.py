import discord
import discord.ext.commands as commands

from os import getenv
from json import load, dump
from dotenv import load_dotenv
from simplejson.errors import JSONDecodeError

from disquestion import Bot

load_dotenv(".env")
with open("config.json", "r") as c: config = load(c)

global debug
global dq_threshold

debug = False
dq_threshold = config["threshold"]

class Disquestion(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        super().__init__(command_prefix=[], intents=intents, activity=discord.Game("Starting Disquestion..."))
        
    async def on_message(self, message: discord.Message):
        if message.author == bot.user: return
        if message.author.bot: return

        with open("config.json", "r") as c: config = load(c)


        if message.channel.id == config["stable_channel"]:
            async with message.channel.typing():
                res = Bot.ask(message.content, threshold=dq_threshold, corpus_tries=100, dataset_file="./dataset/stable.json")
            
            if debug == False: await message.reply(f"{res[0]}")
            else: await message.reply(f"{res[0]}\n```CATEGORY: {res[1]} | TOPIC: {res[2]} | SCORE: {res[3]} | THRESHOLD: {dq_threshold}% | TYPE: {res[4]}```")

        if message.channel.id == config["experimental_channel"]:
            async with message.channel.typing():
                res = Bot.ask(message.content, threshold=dq_threshold, corpus_tries=100, dataset_file="./dataset/experimental.json")
            
            await message.reply(f"{res[0]}\n```CATEGORY: {res[1]} | TOPIC: {res[2]} | SCORE: {round(res[3], 2)} | THRESHOLD: {dq_threshold}% | TYPE: {res[4]}```")

    async def on_ready(self):
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=f"Powered by Disquestion"))
        await bot.tree.sync()
        print(f"Disquestion Ready! Logged in as {bot.user}")

bot = Disquestion()

@bot.tree.command(name="setchannel", description="Changes the Chat Channel for Disquestion")
async def setchannel(interaction: discord.Interaction, stable: discord.TextChannel, experimental: discord.TextChannel = None):
    with open("config.json", "r+") as c: config = load(c)
    if not interaction.user.id in config["managers"]: return await interaction.response.send_message("You need to be a manager to be able to configure Disquestion!")

    config["stable_channel"] = stable.id
    if experimental != None: config["experimental_channel"] = experimental.id
    else: config["experimental_channel"] = 0

    with open("config.json", "r+") as c:
        dump(config, c, indent=4)
    await interaction.response.send_message(f"Successfully set channels!\n> Stable Channel: {stable}\n> Experimental Channel: {experimental}")

@bot.tree.command(name="setthreshold", description="Changes the Threshold of Disquestion.")
async def setchannel(interaction: discord.Interaction, threshold: int):
    global dq_threshold
    with open("config.json", "r+") as c: config = load(c)
    if not interaction.user.id in config["managers"]: return await interaction.response.send_message("You need to be a manager to be able to configure Disquestion!")

    config["threshold"] = threshold
    dq_threshold = threshold

    with open("config.json", "r+") as c:
        dump(config, c, indent=4)
    await interaction.response.send_message(f"Successfully set Disquestion threshold to **{threshold}**!")

@bot.tree.command(name="getdatasets", description="Gives the STABLE and EXPERIMENTAL dataset of the Disquestion bot.")
async def getdatasets(interaction: discord.Interaction):
    if not interaction.user.id in config["managers"]: return await interaction.response.send_message("You need to be a manager to be able to get the Datasets!")

@bot.tree.command(name="toggledebug", description="Toggles debugging on the STABLE dataset.")
async def getdatasets(interaction: discord.Interaction):
    global debug
    if not interaction.user.id in config["managers"]: return await interaction.response.send_message("You need to be a manager to be able to get the Datasets!")

    debug = not debug
    await interaction.response.send_message(f"Successfully set Debugging to **{debug}**! (this is temporary)")


token = getenv("token")
bot.run(token)

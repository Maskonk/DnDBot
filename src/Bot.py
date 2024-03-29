from discord.ext.commands import Bot
from discord import Game
from discord.ext import commands
from Cogs.Campaign import Campaign
from Cogs.Dnd import Dnd

bot_prefix = "."
with open('token.txt', 'r') as f:
    token = f.read()

client = Bot(command_prefix=bot_prefix)


@client.event
async def on_ready():
    await client.change_presence(activity=Game(name='D&D'))
    print("Online")


@client.event
async def on_command_error(ctx, error):
    """
    Error handler for the bot.
    :param error: The error that occured.
    """
    if hasattr(ctx.command, 'on_error'):
        return
    if isinstance(error, commands.CheckFailure):
        await ctx.send("You are not authorized to use this command. This command is restricted to Seb and Punky only.")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("That is not a valid command. Please use **.help** for a list of all commands.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"You have missed {error.param} from the command. Use .help <command_name> for exactly "
                       f"what is required.")
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send("The bot does not currently have permissions to perform this action, please report this to "
                       "Punky.")
    else:
        print(error)
        await ctx.send("An error has occurred with this command, please try again, if this persists please report it "
                       "to Punky.")


@client.command(aliases=["Suggestions", "Suggest", "suggest", "suggestion", "Suggestion"])
async def suggestions(ctx):
    """Message pertaining to suggestions for the bot."""
    await ctx.send("If you have any suggestions for new features or an existing feature that could be made better feel "
                   "free to message Punky with your idea. (No promises it will be implemented though)")


@client.command()
async def git(ctx):
    """Alternate command for those trying to get the github link."""
    await ctx.send("git commit -m \"Did you mean .github command?\". (A git joke)")


@client.command(aliases=["code", "Code"])
async def github(ctx):
    """Link to the github repo for this bot."""
    await ctx.send("The code for this bot is at: https://github.com/Maskonk/DnDBot")


client.add_cog(Dnd(client))
client.add_cog(Campaign(client))
client.run(token)

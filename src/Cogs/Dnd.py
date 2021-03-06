from discord.ext.commands import Cog, context
from discord.ext import commands
from random import randint
from src.util import db_call, is_authorized, bot_channel
from random import choice


class Dnd(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def stat(self, ctx: context) -> None:
        """
        Simulates rolling 4d6 and dropping the lowest for a single character statistic.
        """
        message = f"{ctx.author.mention} you rolled: \n-----------\n"
        stat = []
        for y in range(4):
            num = randint(1, 6)
            stat.append(num)
        message += f"{stat[0]} + {stat[1]} + {stat[2]} + {stat[3]} - **{sum(stat) - min(stat)}**\n"
        await ctx.send(message)

    @commands.command(aliases=["roll", "Roll", "Stats"])
    async def stats(self, ctx: context) -> None:
        """
        Simulates rolling 4d6 and dropping the lowest six times for a characters statistics array.
        """
        message = f"{ctx.author.mention} your stats are: \n-----------\n"
        full_stats = []
        for x in range(6):
            stat = []
            for y in range(4):
                num = randint(1, 6)
                stat.append(num)
            message += f"{stat[0]} + {stat[1]} + {stat[2]} + {stat[3]} - **{sum(stat) - min(stat)}**\n"
            full_stats.append(sum(stat) - min(stat))
        full_stats.sort()
        message += f"\n{full_stats[0]}, {full_stats[1]}, {full_stats[2]}, {full_stats[3]}, {full_stats[4]}, {full_stats[5]}"
        await ctx.send(message)

    @commands.command()
    async def characters(self, ctx: context, status: str = "all") -> None:
        """
        Lists all characters registered for a given status.
        :param status: All characters of the given status from Alive, Retired or Dead. All can be used to see very
        character.
        """
        status = status.lower()
        if status not in ["alive", "retired", "dead", "all"]:
            await ctx.send("That is not a valid status, Please use alive, retired, dead or all.")
            return

        characters = await db_call(ctx, "select characters.name, characters.level, characters.class, status.status"
                                        " from characters join status on characters.status = status.id "
                                        "order by characters.status, characters.name")

        alive = list(filter(lambda character: character[3] == "alive", characters))
        retired = list(filter(lambda character: character[3] == "retired", characters))
        dead = list(filter(lambda character: character[3] == "dead", characters))

        msg = "The current characters I have registered are:\n"
        if status == "alive" or status == "all":
            msg += f"\nAlive - {len(alive)}:\n"
            msg += "```\n"
            if alive:
                for character in alive:
                    msg += f"{character[0]} - {character[2]}\n"
            else:
                msg += "None\n"
            msg += "```"
        if status == "retired" or status == "all":
            msg += f"\nRetired - {len(retired)}:\n"
            msg += "```\n"
            if retired:
                for character in retired:
                    msg += f"{character[0]} - {character[2]}\n"
            else:
                msg += "None\n"
            msg += "```"
        if status == "dead" or status == "all":
            msg += f"\nDead - {len(dead)}:\n"
            msg += "```\n"
            if dead:
                for character in dead:
                    msg += f"{character[0]} - {character[2]}\n"
            else:
                msg += "None\n"
            msg += "```"
        await ctx.send(msg)

    @commands.group(name="character", invoke_without_command=True)
    async def character(self, ctx: context):
        """
        Shows detailed info for a given character name.
        :param name: The character name to look up."""
        if ctx.invoked_subcommand is None:
            if ctx.subcommand_passed:
                name = ctx.subcommand_passed.capitalize()
                character = await db_call(ctx, "select characters.name, characters.level, characters.class, characters.race,"
                                               " characters.owner, status.status, characters.notes from characters "
                                               "join status on status.id = characters.status where name=?",
                                               [name])
                if character:
                    character = character[0]
                    owner = self.bot.get_user(character[4])
                    await ctx.send(f"```Name: {character[0]}:\nLevel: {character[1]}\nClass: {character[2]}"
                                   f"\nRace: {character[3]}\nStatus: {character[5].capitalize()}"
                                   f"\nOwner: {owner.display_name}\nNotes:\n{character[6]}```")
                else:
                    await ctx.send("No character found by that name. Use .characters to see a list of all characters.")
            else:
                await ctx.send("Please specify a name to search for.")

    @character.command(name="add")
    async def add_character(self, ctx: context, name: str, level: int, dclass: str, race: str, notes: str = "") -> None:
        """
        Add a character to the list. Assumes the character starts alive.
        :param name: The characters name.
        :param level: The characters level.
        :param dclass: The characters D&D class.
        :param race: The characters D&D race.
        :param notes: Any public notes for the character.
        """
        name = name.capitalize()
        dclass = dclass.capitalize()
        race = race.capitalize()
        character = [name, level, dclass, race, ctx.author.id, 1, notes]
        await db_call(ctx, "insert into characters (name, level, class, race, owner, status, notes) "
                           "values (?,?,?,?,?,?,?)", character)
        await ctx.send("Character has been added. Use .character <name> to see it.")

    @character.command(name="retire")
    async def retire_character(self, ctx: context, name: str) -> None:
        """
        Set the status of a given character to retired. Restricted to the characters owner or an admin."
        :param name: Name of the character to retire.
        """""
        name = name.capitalize()
        character = await db_call(ctx, "select owner from characters where name=?", [name])
        if character:
            if character[0][0] == ctx.author.id or await is_authorized(ctx):
                await db_call(ctx, "update characters set status = (2) where name=?", [name])
                await ctx.send("Character has been retired.")
            else:
                await ctx.send("You are not the owner of this character to update it.")
        else:
            await ctx.send("No character found by that name.")

    @character.command(name="kill")
    async def kill_character(self, ctx: context, name: str) -> None:
        """
        Set the status of a given character to dead. Restricted to the characters owner or an admin.
        :param name: Name of the character to kill.
        """
        name = name.capitalize()
        character = await db_call(ctx, "select owner from characters where name=?", [name])
        if character:
            if character[0][0] == ctx.author.id or await is_authorized(ctx):
                await db_call(ctx, "update characters set status = (3) where name=?", [name])
                await ctx.send("Character has been killed.")
            else:
                await ctx.send("You are not the owner of this character to update it.")
        else:
            await ctx.send("No character found by that name.")

    @commands.command()
    async def excuse(self, ctx: context) -> None:
        """
        Provides an silly excuse for not attending a session.
        """
        excuses = ["my sister's boyfriend's neighbour's best friend's duck died, they are giving it a Viking funeral.",
                   "my electricity provider decided to be greener so cut all power it gets from "
                   "fossil fuels. Unfortunately this means they can't power as many homes including mine.",
                   "a goose stole my PCs power cable.",
                   "I am pretty sure assassins are after me so I have to go into hiding.",
                   "my brother joined a cult that worships Seb as their deity, I have to go shock him to his senses.",
                   "my religion believes that the world ends next week and it is my duty to make as much chaos and "
                   "mayhem as I can, so that even if it doesn't it looks like it has.",
                   "Zombie told me Seb is planning on killing my PC so I need to think of a new character concept."]
        await ctx.send(f"I can't make it {choice(excuses)}")

    @commands.command()
    @commands.check(bot_channel)
    async def apples(self, ctx: context) -> None:
        """
        Command for providing a random command or message. Used for debugging or silliness.
        """
        options = ["That is not a valid command. Please use **.help** for a list of all commands.",
                   "New phone, who dis?", "Go away! I'm sleeping.", "Who are you again?",
                   "The bot does not currently have permissions to perform this action, please report this to Punky.",
                   "You have missed *password* from the command. Use .help <command_name> for exactly what is required.",
                   "You are not authorized to use this command. This command is restricted to Seb and Punky only.",
                   "next", "excuse", "stats", "This bot is currently busy. Please try again later.",
                   "I told my secretary I was not to be disturbed, please tell her shes fired.",
                   "HAVE YOU HEARD OF SOCIAL DISTANCING! GET AWAY FROM ME!",
                   "This is a pandemic what are you doing talking to me?"]
        msg = choice(options)
        if msg in ["next", "excuse", "stats"]:
            command = self.bot.get_command(msg)
            await ctx.invoke(command)
        else:
            await ctx.send(msg)

    @commands.command()
    async def mark(self, ctx: context) -> None:
        """
        Marks a voice channel as in session to warn others against joining, channel is determined by what channel the
        user is in.
        """
        channels = ctx.guild.voice_channels
        for channel in channels:
            if ctx.author in channel.members:
                if "(In Session)" not in channel.name:
                    name = f"{channel.name} (In Session)"
                    await channel.edit(name=name)
                    break
                else:
                    await ctx.send("This channel has already been marked.")
                    break
        else:
            await ctx.send("You must be in a voice channel to use this.")

    @commands.command()
    async def unmark(self, ctx: context) -> None:
        """
        Removes the in session mark from a voice channel, channel is determined by what channel the user is in.
        """
        channels = ctx.guild.voice_channels
        for channel in channels:
            if ctx.author in channel.members:
                if "(In Session)" in channel.name:
                    name = channel.name.replace(" (In Session)", "")
                    await channel.edit(name=name)
                    break
                else:
                    await ctx.send("This channel is not marked.")
                    break
        else:
            await ctx.send("You must be in a voice channel to use this.")

    @apples.error
    async def apples_handler(self, ctx: context, error: commands.CheckFailure) -> None:
        """
        Error handler for the apples command, Ignores any errors that happen with the command.
        :param error:
        """
        pass

    @commands.command()
    async def ask(self, ctx: context, *question: list) -> None:
        """
        8-ball style command. Ask a question and it will gives a response.
        :param question:  The question asked.
        """
        responses = ["Don't count on it.", "The gods have decreed so.", "Only if you want it bad enough.",
                     "My sources say no.", "Very doubtful.", "Outlook not so good.", "Ask again later.",
                     "Try asking your DM.", "Better not tell you now.", "Reply hazy try again.", "Outlook good.",
                     "You are not supposed to know that yet. Stop trying to metagame!", "Most likely",
                     "Of the 14,000,605 possible futures I saw only one it occurred.",
                     "You are more likely to win the lottery", "The answers lies inside of yourself.",
                     "The answer to that question is the same as the answer to Will people ever stop bugging me "
                     "with question? All times of day and night I get these random ass question, Who the fuck wants to "
                     "know if they will have toast for breakfast at four in the bloody morning!",
                     "New phone who's this?", "The answer guys on the shitter at the moment can I take a message?",
                     "Only if Punky says yes.", "How much are you willing to pay for an answer?",
                     "You have reached the wrong number please hang up and try again."]
        await ctx.send(f"Oh magic ball {' '.join(question)}\nThe magic ball says:\n{choice(responses)}")

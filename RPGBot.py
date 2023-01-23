# Copyright 2017 Sage Callon

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
# Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import dice
import json
import re

import discord
from discord import app_commands
from discord.ext import commands

config_data = open('configs/config.json').read()
config = json.loads(config_data)

# TODO:
''' 
    o Add loot generation
'''
# =========================================================================== #

bot_intents = discord.Intents().all()
bot_prefix = config['bot_prefix']
bot_token = config['bot_token']
max_dice = config['max_dice']
max_sides = config['max_sides']
client = commands.Bot(command_prefix=bot_prefix, intents=bot_intents)

roll_description = "Roll the dice! You can also provide a comment, which will be placed after your roll."
dice_syntax_text = "What would you like to roll?"
comment_text = "Descriptive text that goes after your result."

# =========================================================================== #


@client.event
async def on_ready():
    """
    The output of this function signals that Fox-Bot is up and running.
    """
    await client.change_presence(activity=discord.Game(name='Pathfinder'))
    msg0 = "Syncing commands...\n"
    try:
        synced = await client.tree.sync()
        msg1 = "RPG-Bot is running as {}.\n".format(client.user.name)
        msg2 = "Our id is {}. Synced {} command(s).\n".format(client.user.id, len(synced))
        msg3 = "Invite link: https://discordapp.com/oauth2/authorize?client_id={}&scope=bot&scope=applications.commands%20bot".format(client.user.id)
        make_border(len(msg3))
        print(msg0 + msg1 + msg2 + msg3)
        make_border(len(msg3))
    except Exception as e:
        print(e)


def make_border(length):
    """
    A function that creates a line of dashes length long.

    :param length: The length of the longest line in a block of text.
    :return: None
    """
    str = ''
    for num in range(length):
        str += '-'
    print(str)

# =========================================================================== #


@client.tree.command(name="roll", description=roll_description)
@app_commands.describe(dice_syntax=dice_syntax_text, comment=comment_text)
async def roll(interaction: discord.Interaction, dice_syntax: str, comment: str = ''):
    await roll_dice(interaction, dice_syntax, comment)


@client.tree.command(name="r", description=roll_description)
@app_commands.describe(dice_syntax=dice_syntax_text, comment=comment_text)
async def r(interaction: discord.Interaction, dice_syntax: str, comment: str = ''):
    await roll_dice(interaction, dice_syntax, comment)


async def roll_dice(interaction: discord.Interaction, dice_syntax: str, comment:  str):
    """
    Roll the dice!

    This expression can handle basic multiplication, division, addition, and subtraction.
    It can also handle exponentiation, if for some reason you need that.

    To add a comment to the roll, add a # and then some words to the end of the line.

    Examples:
        /r 1d6
        /r 1d20+12
        /r 1d6x4+3d6
        /r 7d6 #Archimedes launches a fireball!
    """
    await interaction.response.defer()
    orig_arg = dice_syntax.replace(dice_syntax.split()[0] + " ", '')
    # This string will be used to display individual dice rolls we get.
    if len(comment) > 1:
        # This will parse off a comment for appending later.
        comment = "# " + comment
    dicestring = orig_arg
    # This one will be evaluated by eval().
    arg = orig_arg
    # Replace commonly used operands by humans so equations behave how they are expected to.
    arg = arg.replace('x', '*')
    arg = arg.replace('^', '**')
    diceexpr = '[0-9]*d[0-9]+'
    # Check return value of re.search in documentation
    dicearr = re.findall(diceexpr, arg)
    # Parse the dice roll passed in for exceptionally large numbers.
    for diceroll in dicearr:
        dicebase = diceroll.split("d")
        if int(dicebase[0]) > max_dice:
            await interaction.followup.send("I refuse to roll more than {} dice!".format(max_dice))
            return
        if int(dicebase[1]) > max_sides:
            await interaction.followup.send("I refuse to roll marbles! Dice have a maximum of {} sides.".format(max_sides))
            return
        if int(dicebase[1]) < 1:
            await interaction.followup.send("Dice have at least one side.")
            return
        nums = dice.roll(diceroll)
        if len(nums) > 1:
            temp = ""
            iter = 0
            for num in nums:
                if iter > 0:
                    temp += ", "
                temp += str(num)
                iter += 1
            dicestring = dicestring.replace(diceroll, "(" + temp + ")")
        else:
            dicestring = dicestring.replace(diceroll, "(" + str(nums[0]) + ")")
        arg = arg.replace(diceroll, "(" + str(dice.roll(diceroll + "t")) + ")", 1)
    # We have a single term in this whitelist, but I'm keeping the code extensible.
    whitelist = "d".split()
    try:
        for word in re.findall(r'[a-zA-Z_]\w+', arg):
            if word not in whitelist:
                raise Exception("Evil input!")
        # We've filtered our input so this will only include harmless mathematical expressions.
        result = "`{}` —> `{} = {} {}`".format(orig_arg, arg, int(eval(arg)), comment)
    except Exception:
        result = "Invalid input: `{}`".format(orig_arg)
    try:
        await interaction.followup.send(result)
        return
    except discord.errors.HTTPException:
        await interaction.followup.send("Why are you making me post such obscenely long numbers?")


# =========================================================================== #
# The final command here starts the bot.


client.run(bot_token)

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
from discord.ext import commands

config_data = open('configs/config.json').read()
config = json.loads(config_data)

# TODO:
''' 
    o Tidy up roll function
    o Add loot generation
'''

# =========================================================================== #

bot_prefix = config['bot_prefix']
bot_token = config['bot_token']
max_dice = config['max_dice']
max_sides = config['max_sides']
client = commands.Bot(command_prefix=bot_prefix, description="A GM helping bot.")

# =========================================================================== #

# Helper functions in this section


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


@client.event
async def on_ready():
    """
    The output of this function signals that Fox-Bot is up and running.
    """
    await client.change_presence(game=discord.Game(name='Pathfinder'))
    msg1 = "RPG-Bot is running as {}.\n".format(client.user.name)
    msg2 = "Our id is {}.\n".format(client.user.id)
    msg3 = "Invite link: https://discordapp.com/oauth2/authorize?client_id={}&scope=bot".format(client.user.id)
    make_border(len(msg3))
    print(msg1 + msg2 + msg3)
    make_border(len(msg3))


# =========================================================================== #
# Follows are the commands the bot accepts.


@client.command(pass_context=True)
async def r(ctx):
    """
    Roll the dice

    Help documentation TBD.
    """
    orig_arg = ctx.message.content.replace(ctx.message.content.split()[0] + " ", '')
    # This string will be used to display individual dice rolls we get.
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
            await client.say("I refuse to roll more than {} dice!".format(max_dice))
            return
        if int(dicebase[1]) > max_sides:
            await client.say("I refuse to roll marbles with more than {} sides!".format(max_sides))
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
                break
        # We've filtered our input so this will only include harmless mathematical expressions.
        result = "`{}` —> `{} = {}`".format(orig_arg, dicestring, int(eval(arg)))
    except Exception:
        result = "Invalid input: `{}`".format(orig_arg)
    try:
        await client.say(result)
    except discord.errors.HTTPException:
        await client.say("Why are you making me post such obscenely long numbers?")


# =========================================================================== #
# The final command here starts the bot. Nice and simple!


client.run(bot_token)
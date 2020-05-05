import discord
import os
from discord.ext import commands
from typing import Any, List, Optional
import random

client = commands.Bot(command_prefix='//')
# Is used to launch the bot, DO NOT SHARE IT
TOKEN = "Njg2Mzk1ODU0NjU5MTI1MzQ1.XmWoXA.mzQOJaPytBGPMmu8x77PREFViOQ"

PLAYERS = []
GAME_STATE = [False]
CURRENT_PLAYER = []
CARD_PICS = {"captain": "Captain.jpg", "duke": "Duke.jpg",
             "ambassador": "Ambassador.jpg", "assassin": "Assassin.png",
             "contessa": "Contessa.png"}


@client.event
async def on_ready():
    # console message to confirm bot has logged in
    print('We have logged in as {0.user}'.format(client))


class Stack:
    """A last-in-first-out (LIFO) stack of items.

    Stores data in a last-in, first-out order. When removing an item from the
    stack, the most recently-added item is the one that is removed.
    """
    # === Private Attributes ===
    # _items:
    #     The items stored in this stack. The end of the list represents
    #     the top of the stack.
    _items: List

    def __init__(self) -> None:
        """Initialize a new empty stack."""
        self._items = []

    def is_empty(self) -> bool:
        """Return whether this stack contains no items.

        >>> s = Stack()
        >>> s.is_empty()
        True
        >>> s.push('hello')
        >>> s.is_empty()
        False
        """
        return self._items == []

    def push(self, item: Any) -> None:
        """Add a new element to the top of this stack."""
        self._items.append(item)

    def push_bottom(self, item: Any) -> None:
        """
        Adds a element to the bottom of this stack
        """
        self._items.insert(0, item)

    def pop(self) -> Any:
        """Remove and return the element at the top of this stack.

        Raise an EmptyStackError if this stack is empty.

        >>> s = Stack()
        >>> s.push('hello')
        >>> s.push('goodbye')
        >>> s.pop()
        'goodbye'
        """
        if self.is_empty():
            raise EmptyStackError
        else:
            return self._items.pop()

    def pop2(self) -> Any:
        """
        Remove and return the element at the top of this stack.
        Raise an EmptyStackError if this stack is empty.
        """
        if self.is_empty():
            raise EmptyStackError
        else:
            return [self._items.pop(), self._items.pop()]


class EmptyStackError(Exception):
    """Exception raised when an error occurs."""
    pass


class Player:
    """
    Allows the player to command actions
    """
    user: discord.member
    name: str
    id: int
    coin: int
    cards: List[str]
    choice: bool

    def __init__(self, user: discord.member) -> None:
        # If the user has a nickname
        if user.nick is None:
            self.name = user.name
        else:
            self.name = user.nick
        self.user = user
        self.id = user.id
        self.coin = 2
        self.cards = []


def generate_deck() -> Stack:
    """
    Shuffles the deck of cards and returns said deck
    """
    deck = Stack()
    cards = ["captain", "duke", "ambassador", "assassin", "contessa", "captain", "duke", "ambassador", "assassin",
             "contessa", "captain", "duke", "ambassador", "assassin", "contessa"]
    random.shuffle(cards)
    length_cards = len(cards)
    while length_cards != 0:
        deck.push(cards.pop(-1))
        length_cards -= 1
    return deck


@client.command()
async def game(ctx, *players):
    """
    To add players to a game of coup, you must mention up to 1-5 users.
    The user who initializes it, is a player in the game
    Total of 2-6 players can play the game
    Any additional players are ignored
    """
    # Resets the players for each game
    if GAME_STATE[0]:
        await ctx.send("Game is in progress, wait until it finishes")
    else:
        if len(players) >= 2:
            deck = generate_deck()
            await ctx.send("Now creating coup game with: ")
            # Total represents the total number of players in the game
            total = 0
            for player in players[0:4]:
                user = ctx.guild.get_member(int(player[2:-1]))
                await ctx.send(user.name)
                play = Player(user)
                play.cards = deck.pop2()
                await show_cards(play)
                PLAYERS.append(play)
                total += 1

            CURRENT_PLAYER[0] = 0, total
            await ctx.send("It is {} turn".format(PLAYERS[CURRENT_PLAYER[0][0]].name))
            await ctx.send(embed=command_list())

        else:
            await ctx.send("Not enough players")


def command_list():
    """
    Returns an embed of all the commands
    """
    embed = discord.Embed()
    embed.add_field(name='Action', value="Command")
    embed.add_field(name='Income:', value="//income")
    embed.add_field(name='Foreign Aid:', value="//aid")
    embed.add_field(name='Tax:', value="//tax")
    embed.add_field(name='Coup:', value="//coup")
    embed.add_field(name='Assassinate:', value="//assassinate")
    embed.add_field(name='Steal:', value="//steal")
    embed.add_field(name='Exchange:', value="//exchange")
    return embed


async def show_cards(player: Player):
    """
    Shows the players cards
    """
    await player.user.create_dm()
    await player.user.dm_channel.send("{}'s cards\n{} coins".format(player.name, player.coin))
    for card in player.cards:
        path = "Images"
        await player.user.dm_channel.send(file=discord.File(f'{path}\{CARD_PICS[card]}'))


# Launches the bot on discord
client.run(TOKEN)

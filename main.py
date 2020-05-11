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
CURRENT_PLAYER = [None]
CARD_PICS = {"captain": "Captain.jpg", "duke": "Duke.jpg",
             "ambassador": "Ambassador.jpg", "assassin": "Assassin.png",
             "contessa": "Contessa.png"}
PATH = "Images"
# Checks if all the players agree to allow the current player to commit an action
CONDITION = [False]
C_INDEX = [0]
BLOCK = [False]
C_ACTION = [None]
C_PLAYERS = []


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
                C_PLAYERS.append(play)
                PLAYERS.append(play)
                total += 1

            # The current player is the player first in PLAYERS
            # This keeps track on how many players are left, and current index for PLAYERS
            CURRENT_PLAYER[0] = [PLAYERS[0], total, 0]
            await ctx.send("It is {} turn".format(CURRENT_PLAYER[0][0].name))
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
    embed.add_field(name='Coup:', value="//coup @user")
    embed.add_field(name='Assassinate:', value="//assassinate @user")
    embed.add_field(name='Steal:', value="//steal @user")
    embed.add_field(name='Exchange:', value="//exchange @user")
    return embed


async def show_cards(player: Player):
    """
    Shows the players cards
    """
    await player.user.create_dm()
    await player.user.dm_channel.send("{}'s cards\n{} coins".format(player.name, player.coin))
    index = 0
    for card in player.cards:
        await player.user.dm_channel.send("{}. {}".format(index, card))
        await player.user.dm_channel.send(file=discord.File(f'{PATH}\{CARD_PICS[card]}'))
        index += 1


@client.command()
async def income(ctx) -> None:
    """
    Player takes 1 coin
    """
    if ctx.author == CURRENT_PLAYER[0][0].user:
        CURRENT_PLAYER[0][0].coin += 1
        await ctx.send("{} now has {} coins".format(CURRENT_PLAYER[0][0].name, CURRENT_PLAYER[0][0].coin))
        await ctx.send(next_player())

    else:
        await ctx.send("Oi, wait your turn")


@client.command()
async def aid(ctx) -> None:
    """
    Player takes 2 coins, can be blocked with a duke
    """
    C_ACTION[0] = "aid"
    await ctx.send(player_check())


def next_player():
    """
    The next player in PLAYERS, goes next
    Unless it reaches the end, where it starts back to the first player
    Returns a string, telling the next persons turn
    If there is only one player left, that person wins
    """
    # If there is one player left, declare victory, and set game_state to false
    if CURRENT_PLAYER[0][1] == 1:
        GAME_STATE[0] = True
        return "{} has asserted dominance and won".format(CURRENT_PLAYER[0][0].name)
    else:
        if CURRENT_PLAYER[0][2] + 1 == CURRENT_PLAYER[0][1]:
            CURRENT_PLAYER[0][0], CURRENT_PLAYER[0][2] = PLAYERS[0], 0
        else:
            CURRENT_PLAYER[0][2] += 1
            CURRENT_PLAYER[0][0] = PLAYERS[CURRENT_PLAYER[0][2]]
        return "It is now {} turn".format(CURRENT_PLAYER[0][0].name)


def player_check() -> str:
    """
    Allow opposing players to call a bluff or block the current player committing an action
    True means they believe, the current player
    Otherwise false the player is either calling a bluff or blocking
    """
    # Skips asking the current player
    if PLAYERS[C_INDEX[0]].user == CURRENT_PLAYER[0][0].user:
        C_INDEX[0] += 1
    whose_turn = "{} do you want to bluff or block?\n//allow means you believe them\n" \
                 "//block means you'll block and action with one of your influences\n" \
                 "//bluff means you believe that the current player does not have that " \
                 "influence".format(C_PLAYERS[C_INDEX[0]].name)
    return whose_turn


def lose():
    """
    If a player is out of the cards, they are kicked from the game
    """
    PLAYERS.pop(CURRENT_PLAYER[0][2])
    if CURRENT_PLAYER[0][1] - 1 == CURRENT_PLAYER[0][2]:
        CURRENT_PLAYER[0][2] = 0
    CURRENT_PLAYER[0][1] -= 1
    CURRENT_PLAYER[0][0] = PLAYERS[CURRENT_PLAYER[0][2]]


@client.command()
async def allow(ctx):
    """
    Player allows the current player to commit an action
    """
    if ctx.author == C_PLAYERS[C_INDEX[0]].user:
        C_INDEX[0] += 1
        if len(PLAYERS) <= C_INDEX[0]:
            text = action()
            await ctx.send(text)
            text = next_player()
            await ctx.send(text)
        else:
            await ctx.send(player_check())
    else:
        await ctx.send("Wait ya turn {}".format(ctx.author.nick))


@client.command()
async def bluff(ctx):
    """
    PLayer believes that the current player is lying about having an influence
    Thus the current player must show what card they have
    If they do have it, the player who called the bluff must discard one of their cards
    Otherwise, the current player does not have it, therefore must discard it
    """
    if ctx.author == C_PLAYERS[C_INDEX[0]].user:
        await ctx.send("{} you must show your cards using //show_card!".format(CURRENT_PLAYER[0].name))
    else:
        await ctx.send("Wait ya turn")


@client.command()
async def block(ctx):
    """
    PLayer believes that the current player is lying about having an influence
    Thus the current player must show what card they have
    If they do have it, the player who called the bluff must discard one of their cards
    Otherwise, the current player does not have it, therefore must discard it
    """
    if ctx.author == C_PLAYERS[C_INDEX[0]].user:
        await ctx.send("{} you must show your cards using //show_card!".format(C_PLAYERS[C_INDEX[0]].name))
    else:
        await ctx.send("Wait ya turn")


@client.command()
async def show_card(ctx, index: int):
    """
    PLayer must show one of their cards, if that card is the same as C_ACTION
    the other player must discard one of their cards
    """
    if ctx.author == C_PLAYERS[C_INDEX[0]].user:
        card = C_PLAYERS[C_INDEX[0]].cards[index]
        ctx.send(file=discord.File(f'{PATH}\{CARD_PICS[card]}'))
        if card == C_ACTION:
            # If the current player only has one card left, it is immediately discarded and they are out of the game
            if len(CURRENT_PLAYER[0][0].cards) == 1:
                discarded_card = CURRENT_PLAYER[0][0].cards.pop(0)
                await ctx.send("{} discarded {} and is out of the game".format(CURRENT_PLAYER[0].name, discarded_card))
                lose()
            else:
                await ctx.send("{} discard a card!\n Use //discard index".format(CURRENT_PLAYER[0].name))
        else:
            discarded_card = C_PLAYERS[C_INDEX[0]].cards.pop(0)
            # If the player has no cards left
            if len(C_PLAYERS[C_INDEX[0]].cards) == 0:
                await ctx.send(
                    "{} discarded {} and is out of the game".format(C_PLAYERS[C_INDEX[0]].name, discarded_card))
                lose()
            else:
                await ctx.send("{} discarded {}".format(C_PLAYERS[C_INDEX[0]].name, discarded_card))

    elif ctx.author == CURRENT_PLAYER[0].user:
        card = CURRENT_PLAYER[0].cards[index]
        ctx.send(file=discord.File(f'{PATH}\{CARD_PICS[card]}'))
        if card == C_ACTION:
            # If the current player only has one card left, it is immediately discarded and they are out of the game
            if len(C_PLAYERS[C_INDEX[0]].cards) == 1:
                discarded_card = C_PLAYERS[C_INDEX[0]].cards.pop(0)
                await ctx.send("{} discarded {} and is out of the game".format(C_PLAYERS[C_INDEX[0]].name,
                                                                               discarded_card))
                lose()
            else:
                await ctx.send("{} discard a card!\n Use //discard index".format(C_PLAYERS[C_INDEX[0]].name))
        else:
            discarded_card = C_PLAYERS[C_INDEX[0]].cards.pop(0)
            # If the player has no cards left
            if len(C_PLAYERS[C_INDEX[0]].cards) == 0:
                await ctx.send(
                    "{} discarded {} and is out of the game".format(C_PLAYERS[C_INDEX[0]].name, discarded_card))
                lose()
            else:
                await ctx.send("{} discarded {}".format(C_PLAYERS[C_INDEX[0]].name, discarded_card))

    else:
        await ctx.send("Do you want everyone to know your cards?")


def action() -> str:
    """
    If the player action is allowed, they get to use their influence
    """
    C_INDEX[0] = 0
    if C_ACTION[0] == "aid":
        CURRENT_PLAYER[0][0].coin += 2
        text = "{} now has {} coins".format(CURRENT_PLAYER[0][0].name, CURRENT_PLAYER[0][0].coin)
    elif C_ACTION[0] == "duke":
        CURRENT_PLAYER[0].coin += 3
    elif C_ACTION[0] == "captain":
        print("Oh lord this is dumb")
    return text


# Launches the bot on discord
client.run(TOKEN)

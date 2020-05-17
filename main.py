import discord
import os
from discord.ext import commands
from typing import Any, List, Optional, Tuple
import random

client = commands.Bot(command_prefix='//')
# Is used to launch the bot, DO NOT SHARE IT
TOKEN = "Njg2Mzk1ODU0NjU5MTI1MzQ1.XmWoXA.mzQOJaPytBGPMmu8x77PREFViOQ"

# How many coins are given at the beginning of a game
# Used for debugging
COINS = 20
PLAYERS = []
GAME_STATE = [False]
CURRENT_PLAYER = [None]
DECK = [None]
CARD_PICS = {"captain": "Captain.jpg", "duke": "Duke.jpg",
             "ambassador": "Ambassador.jpg", "assassin": "Assassin.png",
             "contessa": "Contessa.png"}
PATH = "Images"
C_INDEX = [0]
BLOCK = [False]
C_ACTION = [None]
# Key is an action and the values are the influences that can block it
BLOCKS = {"aid": ["duke"], "captain": ["captain", "ambassador"], "assassin": ["contessa"], "duke": ["duke"]}
# The card index that the current player wants to exchange
# Index 1 contains 2 cards from the top of the deck
EX_CARDS = [None, None]


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

    def pop2(self) -> List[Any]:
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
        self.coin = COINS
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
    embed.add_field(name='Exchange:', value="// <index>")
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


def find_player(player) -> Optional[Tuple[Player, int]]:
    """
    Finds the player in PLAYERS and returns their player class and index
    """
    index = 0
    while index < len(PLAYERS):
        if index != CURRENT_PLAYER[0][2]:
            print(player[2:-1], PLAYERS[index].id, type(PLAYERS[index].id))
            if int(player[2:-1]) == PLAYERS[index].id:
                return PLAYERS[index].user, index
        index += 1
    return None


def next_player():
    """
    The next player in PLAYERS, goes next
    Unless it reaches the end, where it starts back to the first player
    Returns a string, telling the next persons turn
    If there is only one player left, that person wins
    """
    # If there is one player left, declare victory, and set game_state to false
    if CURRENT_PLAYER[0][1] == 1:
        GAME_STATE[0] = False
        PLAYERS.pop(0)
        return "{} has asserted dominance and won".format(CURRENT_PLAYER[0][0].name)
    else:
        # If the index reaches the last player on the list, start from 0
        C_INDEX[0] = 0
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
    print(C_INDEX[0])
    # Skips asking the current player
    if PLAYERS[C_INDEX[0]].user == CURRENT_PLAYER[0][0].user:
        # If the current player is last in PLAYERS
        if C_INDEX[0] + 1 > CURRENT_PLAYER[0][1]:
            C_INDEX[0] = 0
        else:
            C_INDEX[0] += 1
    # Makes sure there isn't an IndexError
    if C_INDEX[0] < len(PLAYERS):
        whose_turn = "{} do you want to bluff or block?\n//allow means you believe them\n" \
                     "//block means you'll block and action with one of your influences\n" \
                     "//bluff means you believe that the current player does not have that " \
                     "influence".format(PLAYERS[C_INDEX[0]].name)
    # If the C_INDEX is greater the amount of players, then go to the next player and commit action for current
    else:
        whose_turn = "{}\n{}".format(action(), next_player())
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


def action() -> Optional[str]:
    """
    If the player action is allowed, they get to use their influence
    """
    text = None
    if C_ACTION[0] == "aid":
        CURRENT_PLAYER[0][0].coin += 2
        text = "{} now has {} coins".format(CURRENT_PLAYER[0][0].name, CURRENT_PLAYER[0][0].coin)
    elif C_ACTION[0] == "duke":
        C_INDEX[0] = 0
        CURRENT_PLAYER[0][0].coin += 3
        text = "{} now has {} coins".format(CURRENT_PLAYER[0][0].name, CURRENT_PLAYER[0][0].coin)
    elif C_ACTION[0] == "assassin" or C_ACTION[0] == "coup":
        print(C_INDEX[0])
        if len(PLAYERS[C_INDEX[0]].cards) == 1:
            text = "{} discarded {} and is out of the game".format(PLAYERS[C_INDEX[0]].name,
                                                                   PLAYERS[C_INDEX[0]].cards.pop(0))
            lose()
            text = next_player()
        else:
            C_ACTION[0] = "coup"
            text = "{} use //discard <index> to discard one of your cards".format(PLAYERS[C_INDEX[0]].name)
    elif C_ACTION[0] == "captain":
        if PLAYERS[C_INDEX[0]].coin >= 2:
            PLAYERS[C_INDEX[0]].coin -= 2
            text = "{} now has {} coins\n{} now has {}" \
                .format(PLAYERS[C_INDEX[0]].name, PLAYERS[C_INDEX[0]].coin,
                        CURRENT_PLAYER[0][0].name, CURRENT_PLAYER[0][0].coin)
        elif PLAYERS[C_INDEX[0]].coin == 1:
            PLAYERS[C_INDEX[0]].coin -= 1
            text = "{} now has 0 coins\n{} now has {}" \
                .format(PLAYERS[C_INDEX[0]].name, CURRENT_PLAYER[0][0].name, CURRENT_PLAYER[0][0].coin)
        else:
            text = "LOOOOOOOOOOOOOOOOOOL you just took 0 coins cause they had 0 coins\nWhat a meme"
        C_INDEX[0] = 0
    # Ambassador
    else:
        text = "{} select ur card by using //choice <index>".format(CURRENT_PLAYER[0][0].name)
        C_INDEX[0] = 0

    return text


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
            GAME_STATE[0] = True
            DECK[0] = generate_deck()
            await ctx.send("Now creating coup game with: ")
            # Total represents the total number of players in the game
            total = 0
            for player in players[0:4]:
                user = ctx.guild.get_member(int(player[2:-1]))
                await ctx.send(user.name)
                play = Player(user)
                play.cards = DECK[0].pop2()
                await show_cards(play)
                PLAYERS.append(play)
                total += 1

            # The current player is the player first in PLAYERS
            # This keeps track on how many players are left, and current index for PLAYERS
            CURRENT_PLAYER[0] = [PLAYERS[0], total, 0]
            await ctx.send("It is {} turn".format(CURRENT_PLAYER[0][0].name))
            await ctx.send(embed=command_list())

        else:
            await ctx.send("Not enough players")


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


@client.command()
async def tax(ctx) -> None:
    """
    Player takes 3 coins, is used by the duke
    """
    C_ACTION[0] = "duke"
    await ctx.send(player_check())


@client.command()
async def coup(ctx, player: str) -> None:
    """
    Player uses 7 coins, to immediately take away a players influence
    """
    if ctx.author == CURRENT_PLAYER[0][0].user:
        print(CURRENT_PLAYER[0][0].coin)
        if CURRENT_PLAYER[0][0].coin >= 7:
            CURRENT_PLAYER[0][0].coin -= 7
            challenger = find_player(player)
            if challenger is None:
                await ctx.send("Oi you dont exist")
                return
            C_INDEX[0] = challenger[1]
            if len(PLAYERS[challenger[1]].cards) == 1:
                await ctx.send("{} discarded {} and is out of the game".format(PLAYERS[challenger[1]].name,
                                                                               PLAYERS[challenger[1]].cards.pop(0)))
                lose()
                await ctx.send(next_player())
            else:
                C_ACTION[0] = "coup"
                await ctx.send("{} use //discard <index> to discard one of your cards"
                               .format(PLAYERS[challenger[1]].name))
        else:
            await ctx.send("You require more coin")
    else:
        ctx.send("It may be the name of the game, but it doesn't mean you can be the game")


@client.command()
async def assassinate(ctx, player: str) -> None:
    """
    Player uses 3 coins, to immediately take away a players influence
    """
    if ctx.author == CURRENT_PLAYER[0][0].user:
        if CURRENT_PLAYER[0][0].coin >= 3:
            C_ACTION[0] = "assassin"
            CURRENT_PLAYER[0][0].coin -= 3
            challenger = find_player(player)
            if challenger is None:
                await ctx.send("Oi you dont exist")
                return
            C_INDEX[0] = challenger[1]
            await ctx.send("{} do you believe in lies, then use //bluff or //block. Otherwise //allow"
                           .format(challenger[0]))
        else:
            await ctx.send("You require more coin")
    else:
        await ctx.send(".......................................................")


@client.command()
async def steal(ctx, player: str) -> None:
    """
    Player steals 2 coins from another player, uses captain
    """
    if ctx.author == CURRENT_PLAYER[0][0].user:
        C_ACTION[0] = "captain"
        challenger = find_player(player)
        if challenger is None:
            await ctx.send("Oi you dont exist")
            return
        C_INDEX[0] = challenger[1]
        await ctx.send("{} do you allow this fool to steal your hard earn cash, then use //bluff or "
                       "//block. Otherwise //allow".format(challenger[0]))
        await ctx.send(player_check())
    else:
        await ctx.send("Patience is not your strong suit is it")


@client.command()
async def exchange(ctx, index: int) -> None:
    """
    Player exchanges one of their cards from the top 2 cards, uses ambassador
    """
    C_ACTION[0] = "ambassador"
    EX_CARDS[0] = index
    EX_CARDS[1] = DECK[0].pop2()
    await CURRENT_PLAYER[0][0].user.create_dm()
    index = 0
    for card in EX_CARDS[1]:
        await CURRENT_PLAYER[0][0].user.dm_channel.send("{}. {}".format(index, card))
        await CURRENT_PLAYER[0][0].user.dm_channel.send(file=discord.File(f'{PATH}\{CARD_PICS[card]}'))
        index += 1
    await ctx.send(player_check())


@client.command()
async def allow(ctx):
    """
    Player allows the current player to commit an action
    """
    # If the Current player allows the block or an attack is occur to a player by a captain or assassin
    if C_ACTION[0] in ["assassin", "captain"] and ctx.author == PLAYERS[C_INDEX[0]].user:
        await ctx.send(action())
    # If a block is initiated, go to the next player
    elif BLOCK[0] and ctx.author == CURRENT_PLAYER[0][0].user:
        C_INDEX[0] = 0
        await ctx.send(next_player())
        await ctx.send(embed=command_list())

    # If the player allows it iterates to the next player
    else:
        if ctx.author == PLAYERS[C_INDEX[0]].user:
            # If the next player is the current increment by one
            if PLAYERS[C_INDEX[0]].user == CURRENT_PLAYER[0][0].user:
                C_INDEX[0] += 1
            C_INDEX[0] += 1
        else:
            await ctx.send("Wait ya turn")

        # Once all the players are asked, the current player action will go through
        if len(PLAYERS) <= C_INDEX[0]:
            await ctx.send(action())
            if C_ACTION[0] in ["aid", "duke", "assassin"]:
                await ctx.send(next_player())
                await ctx.send(embed=command_list())
        else:
            await ctx.send(player_check())


@client.command()
async def bluff(ctx):
    """
    PLayer believes that the current player is lying about having an influence
    Thus the current player must show what card they have
    If they do have it, the player who called the bluff must discard one of their cards
    Otherwise, the current player does not have it, therefore must discard it
    """
    # If a block is initiated, the current player does not believe that the challenger does not have the influence
    if BLOCK[0] and ctx.author == CURRENT_PLAYER[0][0].user:
        await ctx.send("{} you must show your cards using //show_card!".format(PLAYERS[C_INDEX[0]].name))
    elif ctx.author == PLAYERS[C_INDEX[0]].user:
        await ctx.send("{} you must show your cards using //show_card!".format(CURRENT_PLAYER[0][0].name))
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

    if C_ACTION[0] in ["duke", "aid", "ambassador"]:
        await ctx.send("Come on silly you can't block that!")
    else:
        if ctx.author == PLAYERS[C_INDEX[0]].user:
            await ctx.send("{} do you believe in the heart of the cards, that {} is lying!"
                           "\nThen use //bluff\nOtherwise use //allow"
                           .format(CURRENT_PLAYER[0][0].name, PLAYERS[C_INDEX[0]].name))
            BLOCK[0] = True

        else:
            await ctx.send("Wait ya turn")


@client.command()
async def show_card(ctx, index: int):
    """
    PLayer must show one of their cards, if that card is the same as C_ACTION
    the other player must discard one of their cards
    """
    flag = False
    # If the challenger believes that the current player is lying
    if ctx.author == PLAYERS[C_INDEX[0]].user:
        challenger = PLAYERS[C_INDEX[0]]
        actionman = CURRENT_PLAYER[0][0]
        flag = True
    # If the current player believes that the challenger is lying
    elif ctx.author == CURRENT_PLAYER[0][0].user:
        challenger = CURRENT_PLAYER[0][0]
        actionman = PLAYERS[C_INDEX[0]]
        flag = True
    else:
        await ctx.send("Do you want everyone to know your cards?")

    print(actionman.name, challenger.name)
    # If a block was used to initialize this state, set block to false
    if BLOCK[0]:
        BLOCK[0] = False
    # Only happens if a player is legitimately showing a card
    if flag:
        card = challenger.cards[index]
        await ctx.send(file=discord.File(f'{PATH}\{CARD_PICS[card]}'))
        # If the challenger correctly has the card, actionman must lose one
        if card == C_ACTION[0]:
            # If the current player only has one card left, it is immediately discarded and they are out of the game
            if len(actionman.cards) == 1:
                discarded_card = actionman.cards.pop(0)
                await ctx.send("{} discarded {} and is out of the game".format(actionman.name,
                                                                               discarded_card))
                lose()
                await ctx.send(next_player())
            else:
                await ctx.send("{} discard a card!\n Use //discard index".format(actionman.name))
            await show_cards(actionman)
        # Otherwise challenger loses said card
        else:
            discarded_card = challenger.cards.pop(0)
            # If the player has no cards left
            if len(challenger.cards) == 0:
                await ctx.send(
                    "{} discarded {} and is out of the game".format(challenger.name, discarded_card))
                lose()
                await ctx.send(next_player())
            else:
                await ctx.send("{} discarded {}".format(challenger.name, discarded_card))
            if C_ACTION == "ambassador":
                for index in range(0, 2):
                    DECK[1].push_bottom(EX_CARDS[1].pop(0))
            await show_cards(challenger)
            await ctx.send(action())
            await ctx.send(next_player())
            await ctx.send(embed=command_list())


@client.command()
async def discard(ctx, index: int):
    """
    If current player used a coup or an assassin, the challenger must discard one of their cards
    """
    if ctx.author == PLAYERS[C_INDEX[0]].user:
        if 0 <= index < len(PLAYERS[C_INDEX[0]].cards):
            discarded_card = PLAYERS[C_INDEX[0]].cards.pop(index)
            await ctx.send("{} discarded {}".format(PLAYERS[C_INDEX[0]].name, discarded_card))
            await ctx.send(next_player())
            await ctx.send(embed=command_list())

        else:
            await ctx.send("Invalid index, try again")
    else:
        await ctx.send("DO YOU WANT TO DISCARD!!!!!!")


@client.command()
async def choice(ctx, index: int):
    """
    After seeing what the top 2 cards are, the player can choose which one they want to exchange
    """
    if ctx.author == PLAYERS[C_INDEX[0]].user:
        if 0 <= index < 2:
            # Makes a list for the cards that must be put at the bottom of the deck
            DECK[0].push_bottom(CURRENT_PLAYER[0][0].cards.pop(EX_CARDS[0]))
            CURRENT_PLAYER[0][0].cards.append(EX_CARDS[1].pop(index))
            DECK[0].push_bottom(EX_CARDS[1].pop)
            await show_cards(CURRENT_PLAYER[0][0])
            await ctx.send(next_player())
            await ctx.send(embed=command_list())


# Launches the bot on discord
client.run(TOKEN)

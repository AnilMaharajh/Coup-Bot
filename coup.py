import discord
from discord.ext import commands
from typing import Any, List, Optional, Tuple
import random

# Global Variables
CARD_PICS = {"captain": "Captain.jpg", "duke": "Duke.jpg",
             "ambassador": "Ambassador.jpg", "assassin": "Assassin.png",
             "contessa": "Contessa.png"}
PATH = "Images"
BLOCKS = {"aid": ["duke"], "captain": ["captain", "ambassador"], "assassin": ["contessa"], "duke": ["duke"]}


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
        self.coin = 2
        self.cards = []


class Coup:
    """

    """
    coins: int
    players: List[Player]
    current_player: Player
    current_player_index: int
    total_players_left: int
    deck: Stack
    challenger: Player
    challenger_index: int
    current_action: str
    must_coup: bool
    block: bool
    # Swap is the card index the current player wants to replace
    swap: List
    exchange_cards: List[str]

    def __init__(self):
        self.coins = 2
        self.players = []
        self.current_player = None
        self.current_player_index = 0
        self.total_players_left = 2
        self.deck = generate_deck()
        self.challenger = None
        self.challenger_index = 0
        self.current_action = ""
        self.must_coup = False
        self.swap = []
        self.exchange_cards = []
        self.block = False

        # c_index = 0
        # block = False
        # c_action = None
        # # Key is an action and the values are the influences that can block it
        # # The card index that the current player wants to exchange
        # # Index 1 contains 2 cards from the top of the deck
        # ex_cards = [None, None]
        # # If the current player has more than 10 coins, they must immediately coup another player on their turn
        # must_coup = [False]
        # swap = [None, None]

    def next_player(self):
        """
        The next player in self.players, goes next
        Unless it reaches the end, where it starts back to the first player
        Returns a string, telling the next persons turn
        If there is only one player left, that person wins
        """
        # If there is one player left, declare victory, and set game_state to false
        if self.total_players_left == 1:
            self.players.pop(0)
            return "{} has asserted dominance and won".format(self.current_player.name)
        else:
            # If the index reaches the last player on the list, start from 0
            self.challenger_index = 0
            if self.current_player_index + 1 == self.total_players_left:
                self.current_player, self.current_player_index = self.players[0], 0
            else:
                self.current_player_index += 1
                self.current_player = self.players[self.current_player_index]
            if self.current_player.coin >= 10:
                self.must_coup = True
                return "{} you must coup another player!".format(self.current_player.name)
            return "It is now {} turn".format(self.current_player.name)

    def player_check(self) -> str:
        """
        Allow opposing players to call a bluff or block the current player committing an action
        True means they believe, the current player
        Otherwise false the player is either calling a bluff or blocking
        """
        print(self.challenger_index)
        # Skips asking the current player
        if self.players[self.challenger_index].user == self.current_player.user:
            # If the current player is last in self.players
            if self.challenger_index + 1 > self.total_players_left:
                self.challenger_index = 0
            else:
                self.challenger_index += 1
        # Makes sure there isn't an IndexError
        if self.challenger_index < len(self.players):
            whose_turn = "{} do you want to bluff or block?\n//allow means you believe them\n" \
                         "//block means you'll block the action with one of your influences\n" \
                         "//bluff means you believe that the current player does not have that " \
                         "influence".format(self.players[self.challenger_index].name)
        # If the C_INDEX is greater the amount of players, then go to the next player and commit action for current
        else:
            # Once everyone allows the ambassador action
            if self.current_action == "ambassador":
                whose_turn = self.allow_ambassador()
            else:
                whose_turn = "{}\n{}".format(self.action(), self.next_player())
        return whose_turn

    def allow_ambassador(self) -> str:
        """
        If the ambassador action is not contested, the first two cards at the top of the deck is shown to the top player
        """
        self.exchange_cards = self.deck.pop2()
        return ""

    def find_player(self, userid: str) -> Optional[str]:
        """
        Finds the player using the id given by the mention by looking through the players list
        """
        index = 0
        while index < len(self.players):
            if self.players[index].id != self.current_player.id:
                if self.players[index].id == userid:
                    self.challenger = self.players[index]
                    self.challenger_index = index
                    return None
            index += 1
        return "Did not find player, try inputting a valid userid using a mention"

    def discard(self) -> str:
        """
        Used by the assassin and coup
        Takes away one card from the opposing player, if they only have one card left, they lose the game
        """
        if len(self.challenger.cards) == 1:
            self.lose()
            return "{} discarded {} and is out of the game".format(self.challenger.name,
                                                                   self.challenger.cards.pop(0))
        else:
            self.current_action = "coup"
            return "{} use //discard <index> to discard one of your cards".format(self.challenger.name)

    def lose(self):
        """
        If a player is out of the cards, they are kicked from the game
        """
        self.players.pop(self.challenger_index)
        if self.total_players_left - 1 == self.current_player_index:
            self.current_player_index = 0
        self.total_players_left -= 1
        self.current_player = self.players[self.current_player_index]

    def action(self) -> Optional[str]:
        """
        If the player action is allowed, they get to use their influence
        """
        text = None
        if self.current_action == "aid":
            text = self.aid()
        elif self.current_action == "duke":
            text = self.tax()
        elif self.current_action == "assassin" or self.current_action == "coup":
            text = self.discard()
        elif self.current_action == "captain":
            text = self.steal()
        # Ambassador
        else:
            return "{} select ur card by using //choice <index>".format(self.current_player.name)

        return "{}\n{}".format(text, self.next_player())

    def income(self) -> str:
        """
        Current player takes 1 coin
        """
        self.current_player.coin += 1
        return "{} now has {} coins".format(self.current_player.name, self.current_player.coin)

    def aid(self) -> str:
        """
        Current player takes 2 coins
        """
        self.current_player.coin += 2
        return "{} now has {} coins".format(self.current_player.name, self.current_player.coin)

    def tax(self) -> str:
        """
        Current player uses the duke and gets 3 coins
        """
        self.current_player.coin += 3
        return "{} now has {} coins".format(self.current_player.name, self.current_player.coin)

    def steal(self) -> str:
        """
        Current player uses duke to steal 2 coins from another player
        """
        if self.challenger.coin >= 2:
            self.challenger.coin -= 2
        elif self.challenger == 1:
            self.challenger.coin -= 1
        else:
            return "LOOOOOOOOOOOOOOOOOOL you just took 0 coins cause they had 0 coins\nWhat a bunch of jokers"
        return "{} now has {} coins\n{} now has {}".format(self.challenger.name, self.challenger.coin,
                                                           self.current_player.name, self.current_player.coin)

    def exchange(self) -> str:
        """
        The current player uses the ambassador to switch of their cards with the the top 2 cards from the deck
        """
        return "Oui"


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
    embed.add_field(name='Exchange:', value="// exchange <index>")
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

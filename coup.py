import discord
from discord.ext import commands
from typing import Any, List, Optional, Tuple, Dict
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
    users: List[str]  # discord.member gets error
    players: List[Player]
    current_player: Player
    current_player_index: int
    total_players_left: int
    deck: Stack
    challenger: Player
    challenger_index: int
    current_action: str
    allow_check: Dict[str, bool]  # discord.member, bool
    allow_check_number: int
    must_coup: bool
    block: bool
    bluff: bool
    discard = Tuple[bool, Player]
    # Swap is the card index the current player wants to replace
    swap: List
    exchange_cards: List[str]
    play_again: bool

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
        self.allow_check = {}
        self.allow_check_number = 0
        self.swap = []
        self.exchange_cards = []
        self.block = False
        self.bluff = False
        self.discard = (False, None)
        self.play_again = False

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
            self.play_again = True
            return "{} has asserted dominance and won\nIf you want to play with the same players, use //play_again".format(
                self.current_player.name)
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
                return "It is now {} turn. You must coup another player!".format(self.current_player.name)

            return "It is now {} turn".format(self.current_player.name)

    def player_check(self) -> str:
        """
        Allow opposing players to call a bluff or block the current player committing an action
        True means they believe, the current player
        Otherwise false the player is either calling a bluff or blocking
        """
        # Skips asking the current player
        if self.players[self.challenger_index].user == self.current_player.user:
            # If the current player is last in self.players
            if self.challenger_index + 1 > self.total_players_left:
                self.challenger_index = 0
                self.challenger = self.players[self.challenger_index]
            else:
                self.challenger_index += 1
                self.challenger = self.players[self.challenger_index]
        # Makes sure there isn't an IndexError
        if self.challenger_index < len(self.players):
            whose_turn = "//allow means you believe them\n" \
                         "//block means you'll block the action with one of your influences\n" \
                         "//bluff means you believe that the current player does not have that " \
                         "influence"
        # If the C_INDEX is greater than the amount of players, then go to the next player and commit action for current
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
        # If the userid is a nickname
        if userid[2] == "!":
            userid = int(userid[3:-1])
        else:
            userid = int(userid[2:-1])
        index = 0
        while index < len(self.players):
            if self.players[index].id != self.current_player.id:
                if self.players[index].id == userid:
                    self.challenger = self.players[index]
                    self.challenger_index = index
                    print(self.challenger)
                    return None
            index += 1
        return "Did not find player, try inputting a valid userid using a mention"

    def lose(self, index):
        """
        If a player is out of the cards, they are kicked from the game
        """
        self.players.pop(index)
        if self.total_players_left - 1 == self.current_player_index:
            self.current_player_index = 0
        self.total_players_left -= 1
        self.current_player = self.players[self.current_player_index]

    def allow(self, player: discord.member):
        if self.allow_check[player]:
            return "{}, you already allowed".format(player.name)
        # If a block is initialized and checks that if its the current player
        elif self.block and player == self.current_player:
            return self.next_player()
        else:
            self.allow_check[player] = True
            self.allow_check_number += 1
            if self.allow_check_number == len(self.players) - 1:
                self.allow_check_number = 0
                # Resets allow_check back to false
                for user in self.allow_check:
                    self.allow_check[user] = False
                return "{} allows {} action\n{}".format(player.name, self.current_player.name, self.action())
            return "{} allows {} action".format(player.name, self.current_player.name)

    def block(self, player: discord.member):
        # If a block has already been initialized
        if self.block:
            return "{} has already blocked {}.\n Check yourself, {}.\n" \
                   "{} do you believe in the heart of the cards, that {} is lying!\n" \
                   "Then use //bluff\nOtherwise use //allow".format(player.name, self.current_player.name, player.name,
                                                                    self.current_player.name, self.challenger.name)
        else:
            self.block = True
            print(player)
            self.challenger = player
            # Resets allow_check back to false
            for user in self.allow_check:
                self.allow_check[user] = False
            return "{} has blocked {}!".format(player.name, self.current_player.name)

    def action(self) -> Optional[str]:
        """
        If the player action is allowed, they get to use their influence
        """
        if self.current_action == "aid":
            text = self.aid()
        elif self.current_action == "duke":
            text = self.tax()
        elif self.current_action == "assassin" or self.current_action == "coup":
            text = self.lose_influence()
            self.discard = (True, self.challenger)
        elif self.current_action == "captain":
            text = self.steal()
        # Ambassador
        else:
            self.exchange_cards = self.deck.pop2()
            return "{} select ur card by using //swap <index of the card you want to give up> <index of the card " \
                   "you want in the channel>".format(self.current_player.name)

        return text

    def income(self) -> str:
        """
        Current player takes 1 coin
        """
        self.current_player.coin += 1
        return "{} now has {} coins\n{}".format(self.current_player.name, self.current_player.coin, self.next_player())

    def aid(self) -> str:
        """
        Current player takes 2 coins
        """
        self.current_player.coin += 2
        return "{} now has {} coins\n{}".format(self.current_player.name, self.current_player.coin, self.next_player())

    def tax(self) -> str:
        """
        Current player uses the duke and gets 3 coins
        """
        self.current_player.coin += 3
        return "{} now has {} coins\n{}".format(self.current_player.name, self.current_player.coin, self.next_player())

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
        return "{} now has {} coins\n{} now has {}\n{}".format(self.challenger.name, self.challenger.coin,
                                                               self.current_player.name, self.current_player.coin,
                                                               self.next_player())

    def assassin(self, challenger: discord.member) -> str:
        """
        Takes away 3 coins from the current player and sets the challenger to whom the current player chooses
        """
        if self.current_player.coin >= 3:
            challenger = self.find_player(challenger)
            # If the player does not exist
            if challenger is not None:
                return challenger
            self.current_action = "assassin"
            self.current_player.coin -= 3
            return "{} do you believe in lies, then use //bluff or //block. Otherwise //allow".format(
                self.challenger.name)
        else:
            return "You require more coin"

    def lose_influence(self) -> str:
        """
        Used by the assassin and coup
        Takes away one card from the opposing player, if they only have one card left, they lose the game
        """
        if len(self.challenger.cards) == 1:
            self.lose(self.challenger_index)
            return "{} discarded {} and is out of the game!\n{}".format(self.challenger.name,
                                                                        self.challenger.cards.pop(0),
                                                                        self.next_player())
        else:
            self.current_action = "coup"
            return "{} use //discard <index> to discard one of your cards".format(self.challenger.name)

    def exchange(self, card_away: int, card_want: int) -> str:
        """
        The current player uses the ambassador to switch of their cards with the the top 2 cards from the deck
        """
        # Pushes the card that the current player wants to swap to the bottom of the deck
        self.deck.push_bottom(self.current_player.cards.pop(card_away))
        # Appends the card the current player wants to their cards list
        self.current_player.cards.append(self.exchange_cards.pop(card_want))
        # Pushes the last card in self.exchange_cards to the bottom
        self.deck.push_bottom(self.exchange_cards.pop(0))
        return "Successfully exchanged cards\n".format(self.next_player())

    def show_card(self, index: int):
        # The challenger needs to prove that they have the card
        if self.bluff and self.block:
            actionman = self.challenger
            actionman_index = self.challenger_index
            challenger = self.current_player
            challenger_index = self.current_player_index
        # The current player needs to prove that they have the card
        else:
            actionman = self.current_player
            actionman_index = self.current_player_index
            challenger = self.challenger
            challenger_index = self.challenger_index

        # If the actionman has the actual card, and their action goes through
        if actionman.cards[index] == self.current_action:
            self.discard_card(challenger, index)
            if len(challenger.cards) == 1:
                statement = "{} And is out of the game!".format(self.discard_card(challenger, 0))
                self.lose(challenger_index)
            else:
                self.discard = (True, challenger)
                # Challenger must discard to continue the game
                return "{} discard a card!\n Use //discard index".format(actionman.name)

            # If the current action is an assassin and the challenger has no cards because their bluff was incorrect
            # The action does not happen
            if self.current_action == "assassin" and len(challenger.cards) == 0:
                return "{}\n{} puts {} to the bottom of the deck and receives a new card" \
                    .format(statement, self.current_player.name, self.current_action)
            else:
                return "{}\n{} puts {} to the bottom of the deck and receives a new card\n{}" \
                    .format(statement, self.current_player.name, self.current_action, self.action())

        # Otherwise they lose the card
        else:
            if len(actionman.cards) == 1:
                statement = "{} and is out of the game!".format(actionman.name,
                                                                self.discard_card(actionman, 0))
                self.lose(actionman_index)
            else:
                statement = self.discard_card(actionman, index)
            return statement

    def discard_card(self, player: Player, index: int):
        """
        Pushes the specified card to the bottom of the deck
        """
        discarded_card = player.cards.pop(index)
        self.deck.push_bottom(discarded_card)
        return "{} discarded {}.\n{}".format(player.name, discarded_card, self.next_player())


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

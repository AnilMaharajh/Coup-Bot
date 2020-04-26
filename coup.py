from typing import Any, List, Optional, Tuple
import random


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
    coin = int
    cards = List[str]

    def __init__(self) -> None:
        self.coin = 2
        self.cards = []


def generate_deck() -> Stack:
    """
    Shuffles the deck of cards and put them in self.card_stack
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


class Coup:
    """
    Creates a game of coup with up to 2-6 players
    There must be at least 2 players
    """
    players: List[Player]
    card_stack: Stack
    total_coins: int

    def __init__(self, player1: Player = None, player2: Player = None, player3: Player = None, player4: Player = None,
                 player5: Player = None, player6: Player = None):
        """
        Creates environment for the game to be played
        Players are generated and given two influence
        Play order is set
        """
        if player2 is None:
            print("Cannot generate game, need one other person")

        self.card_stack = generate_deck()
        players = []

        player1.cards = self.card_stack.pop2()
        players.append(player1)
        player2.cards = self.card_stack.pop2()
        players.append(player2)
        self.total_coins = 46
        self.remaining_players = 2

        if player3 is not None:
            player3.cards = self.card_stack.pop2()
            players.append(player3)
            self.total_coins -= 2
            self.remaining_players += 1
        if player4 is not None:
            player4.cards = self.card_stack.pop2()
            players.append(player4)
            self.total_coins -= 2
            self.remaining_players += 1
        if player5 is not None:
            player5.cards = self.card_stack.pop2()
            players.append(player5)
            self.total_coins -= 2
            self.remaining_players += 1
        if player6 is not None:
            player6.cards = self.card_stack.pop2()
            players.append(player6)
            self.total_coins -= 2
            self.remaining_players += 1

    def income(self, player: Player) -> None:
        """
        Player takes 1 coin
        """
        player.coin += 1

    def foreign_aid(self, player: Player) -> None:
        """
        Player takes 2 coins, can be blocked with a duke
        """
        condition = self.player_check(player)
        if condition is None:
            player.coin += 2
        else:
            self.challenge(player, condition, "foreign")

    def assassinate(self, player, b_player):
        player.coin -= 3
        condition = self.player_check(player)
        if condition is None:


    def player_check(self, player: Player) -> Optional[Player]:
        """
        Allow opposing players to block or bluff the player committing an action
        If nobody responds after 30 seconds, player action goes through
        """
        # All the other players can bypass the 30 seconds by responding N
        # If one player responds with Y, they challenge the player
        return None

    def challenge(self, player: Player, b_player: Player, action: str):
        """
        b_player the one who is challenging player to show their card if they are lying
        Player can show their card, and prove that they have it. Thus, b_player must put away one of their influence
        Player can show their card regardless of its influence and put it in the deck, or put it in the deck
        """

        # if player decides to show their correct card
        #   Can either keep it, or put in the deck to exchange for the first card
        #   b_player must give up one of their cards
        #   checks if b_player has 0 cards, if so they are popped out of the list, eliminating them from the game

        # or player decides to discard one of their cards
        # checks if player has 0 cards, if so they are popped out of the list, eliminating them from the game



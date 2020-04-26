from typing import Any, List
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

    def income(self) -> None:
        """
        Player takes 1 coin
        """
        self.coin += 1

    def foreign_aid(self) -> None:
        """
        Player takes 2 coins, can be blocked with a duke
        """

    def bluff(self, action: str) -> bool:
        """
        In a 30 second period, asks all players if they allow the player to do an action
        """
        # Players allow the action
        # if player1 and player2 ...... all true

        # else:
        # if action == foreign_aid
        #   block_aid(player commit action, player_block)


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
        Players are generated
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

        if player3 is not None:
            player3.cards = self.card_stack.pop2()
            players.append(player3)
            self.total_coins -= 2
        if player4 is not None:
            player4.cards = self.card_stack.pop2()
            players.append(player4)
            self.total_coins -= 2
        if player5 is not None:
            player5.cards = self.card_stack.pop2()
            players.append(player5)
            self.total_coins -= 2
        if player6 is not None:
            player6.cards = self.card_stack.pop2()
            players.append(player6)
            self.total_coins -= 2

        random.shuffle(self.players)

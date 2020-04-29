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
    name: str
    coin: int
    cards: List[str]
    choice: bool

    def __init__(self, name: str) -> None:
        self.name = name
        self.coin = 2
        self.cards = []


def play():
    """
    Sets up a game of coup inside the python terminal
    """
    total_coins = 50
    deck = generate_deck()
    condition = True
    players = []
    while condition:
        try:
            number = int(input("How many players? (2-6)"))
            if 2 <= number <= 6:
                while number != 0:
                    name = input("What is their name?")
                    player = Player(name)
                    player.cards = deck.pop2()
                    total_coins -= 2
                    players.append(player)
                    number -= 1
                condition = False
            else:
                print("Invalid number of players")
        except TypeError:
            print("Invalid value")

    index = 0
    while len(players) != 1:
        action(players[index], deck, players)
        if index == len(players) - 1:
            index = 0
        else:
            index += 1
    print("{} wins the game".format(players[0].name))


def action(player: Player, deck: Stack, players: List[Player]):
    """
    PLayer chooses an action from the list
    """
    show_cards(player)
    print("Coins: {}".format(player.coin))
    if player.coin >= 10:
        b_player = select_opponent("coup", player, players)
        player.coin -= 7
        lose_card(b_player, deck, players)

    print("0. Income")
    print("1. Foreign Aid")
    print("2. Tax")
    print("3. Coup")
    print("4. Assassinate")
    print("5. Steal")
    print("6. Exchange")

    condition = True
    while condition:
        try:
            choice = int(input("{}, what action do you commit?".format(player.name)))
            if 0 <= choice <= 6:
                condition = False
            else:
                print("Invalid index")
        except TypeError:
            print("Invalid type")

    if choice == 0:
        income(player)
    elif choice == 1:
        foreign_aid(player, deck, players)
    elif choice == 2:
        tax(player, players, deck)
    elif choice == 3:
        if player.coin >= 7:
            b_player = select_opponent("coup", player, players)
            player.coin -= 7
            lose_card(b_player, deck, players)
        else:
            print("Don't have enough coin")
            action(player, deck, players)
    elif choice == 4:
        if player.coin >= 3:
            b_player = select_opponent("assassinate", player, players)
            assassinate(player, b_player, deck, players)
        else:
            print("Don't have enough coin")
            action(player, deck, players)
    elif choice == 5:
        steal(player, select_opponent("steal", player, players), deck, players)
    else:
        exchange(player, deck, players)


def select_opponent(act: str, player: Player, players: List[Player]) -> Player:
    """
    Player selects another player to attack
    """
    index = 0
    for opponent in players:
        if player != opponent:
            print("{}. {}".format(index, opponent))
        else:
            player_index = index
        index += 1

    condition = True
    while condition:
        try:
            index = int(input("Which player do you want to {}?".format(act)))
            if index == player_index:
                print("You can't {} from yourself silly".format(act))
            elif 0 <= index < len(players):
                return players[index]
            else:
                print("Invalid index")
        except TypeError:
            print("Invalid type")


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


def income(player: Player) -> None:
    """
    Player takes 1 coin
    """
    player.coin += 1


def foreign_aid(player: Player, deck: Stack, players: List[Player]) -> None:
    """
    Player takes 2 coins, can be blocked with a duke
    """
    condition = player_check(player, players)
    if condition is None:
        player.coin += 2
    else:
        challenge(player, condition, deck, players, "duke")


def assassinate(player: Player, b_player: Player, deck: Stack, players: List[Player]):
    """
    Player uses assassin to take away another player influence
    Uses 3 coins
    Contessa can block
    """
    player.coin -= 3
    condition = player_check(player, players)
    if condition is None:
        lose_card(b_player, deck, players)
    else:
        challenge(player, b_player, deck, players, "assassin")


def steal(player: Player, b_player: Player, deck: Stack, players: List[Player]):
    """
    Player uses captain to take 2 coins from another player
    If the player only has one coin, take that coin
    Ambassador or captain can block steals
    """
    condition = player_check(player, [b_player])
    if condition is None:
        if b_player.coin == 1:
            b_player.coin -= 1
            player.coin = 1
        elif b_player == 0:
            print("What a waste of a turn")
        else:
            b_player.coin -= 2
            player.coin += 2
    else:
        challenge(player, b_player, deck, players, "captain")


def tax(player: Player, players: List[Player], deck: Stack):
    """
    Player use the duke to get 3 coins
    """
    condition = player_check(player, players)
    if condition is None:
        player.coin += 3
    else:
        challenge(player, condition, deck, players, "duke")


def exchange(player: Player, deck: Stack, players: List[Player]):
    """
    Player uses the ambassador to change one of their influences by taking the top 2 cards of the deck, and choosing one
    The remaining cards go to the bottom
    """
    condition = player_check(player, players)
    if condition is None:
        # Asks the player for the card they want gone
        show_cards(player)
        condition = True
        while condition:
            try:
                choice = int(input("What card do you want to exchange?"))
                if 0 <= choice <= len(player.cards):
                    deck.push_bottom(player.cards.pop(choice))
                    condition = False
                else:
                    print("Invalid index number!")
            except TypeError:
                print("Invalid type")
        # Player selects the card they want
        selection = deck.pop2()
        for card in selection:
            print("0. {}".format(card[0]))
            print("1. {}".format(card[1]))
            condition = True
            while condition:
                try:
                    choice = int(input("Which card do you want?"))
                    if 0 <= choice <= 1:
                        player.cards.append(selection[choice])
                    else:
                        print("Invalid index number!")
                except TypeError:
                    print("Invalid type")
    else:
        challenge(player, condition, deck, players, "ambassador")


def show_cards(player: Player):
    """
    Shows the players cards
    """
    index = 0
    print("{}'s cards".format(player.name))
    for card in player.cards:
        print("{}. {}".format(index, card))
        index += 1
    print("")


def player_check(player: Player, players: List[Player]) -> Optional[Player]:
    """
    Allow opposing players to block or bluff the player committing an action
    """
    index = 0
    while index < len(players):
        if players[index] != player:
            choice = input("{}, do you calleth the bluff (Y/N)".format(players[index].name))
            if choice in ["y", "Y"]:
                return players[index]
        index += 1
    return None


def challenge(player: Player, b_player: Player, deck: Stack, players: List[Player], influence: str):
    """
    b_player the one who is challenging player to show their card if they are lying
    Player can show their card, and prove that they have it. Thus, b_player must put away one of their influence
    Player can show their card regardless of its influence and put it in the deck, or put it in the deck
    """
    show_cards(player)
    choice = int(input("What card to show?"))
    if player.cards[choice] == influence:
        lose_card(b_player, deck, players)
    else:
        lose_card(player, deck, players)


def lose_card(player: Player, deck: Stack, players: List[Player]):
    """
    Player chosen must lose one of their influence
    If they no longer have any cards, they are out of the game
    """
    index = 0
    for card in player.cards:
        print("{}. {}".format(index, card))
        index += 1
    condition = True
    while condition:
        try:
            choice = int(input("Which card to discard?"))
            if 0 <= choice <= index - 1:
                card = player.cards.pop(choice)
                print("{} loses {}".format(player.name, card))
                deck.push_bottom(card)
                condition = False
        except TypeError:
            print("Invalid value")

    # If the player has no cards left
    if len(player.cards) == 0:
        players.pop(players.index(player))


if __name__ == "__main__":
    play()

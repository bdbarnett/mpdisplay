# SPDX-FileCopyrightText: 2024 Brad Barnett
#
# SPDX-License-Identifier: MIT
"""
playing_cards.py - A simple playing card library for PyDevices.
Cards can be rendered to any pygraphics canvas: a displaybuf DisplayBuffer,
a pygraphics FrameBuffer, or a display driver.
"""

import random

import pygraphics


HEARTS = "Hearts"
DIAMONDS = "Diamonds"
CLUBS = "Clubs"
SPADES = "Spades"
SUITS = [HEARTS, DIAMONDS, CLUBS, SPADES]

ACE, TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE, TEN, JACK, QUEEN, KING = (
    "Ace",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "10",
    "Jack",
    "Queen",
    "King",
)
RANKS = [ACE, TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE, TEN, JACK, QUEEN, KING]


def sign(x):
    if x < 0:
        return -1
    if x > 0:
        return 1
    return 0


class Card:
    def __init__(self, suit, rank, deck=None):
        self._suit = suit
        self._rank = rank
        self._deck = deck
        self._hidden = False
        self._position = None
        self._target = None

    def __str__(self):
        return f"{self.rank} of {self.suit}"

    def __repr__(self):
        return f"{self.rank} of {self.suit}"

    # def __gt__(self, other_card):
    #     self._deck.compare(self, other_card, 1)

    # def __lt__(self, other_card):
    #     self._deck.compare(self, other_card, -1)

    # def __eq__(self, other_card):
    #     self._deck.compare(self, other_card, 0)

    # def __hash__(self):
    #     return hash((self.suit, self.rank))

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, value):
        self._target = value

    @property
    def value(self):
        return self.rank if len(self.rank) < 3 else self.rank[0]

    @property
    def suit(self):
        return self._suit

    @property
    def rank(self):
        return self._rank

    @property
    def hidden(self):
        return self._hidden

    def update(self):
        return self.render(self._target, self.position[0], self.position[1], self._hidden)

    def hide(self):
        self._hidden = True
        return self.update()

    def reveal(self):
        self._hidden = False
        return self.update()

    def flip(self):
        self._hidden = not self._hidden
        return self.update()

    def discard(self):
        self._deck.discard(self)

    def erase(self):
        return self._deck.erase(self._target, self.position[0], self.position[1])

    def hit_test(self, x, y):
        if self.position is None:
            return False
        return (
            self.position[0] <= x < self.position[0] + self._deck.width
            and self.position[1] <= y < self.position[1] + self._deck.height
        )

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self._position = value

    def render(self, target, x, y, hidden=True):
        return self._deck.render(self, target, x, y, hidden=hidden)

    def save_state(self, target, x, y, hidden):
        self._target = target
        self._position = (x, y)
        self._hidden = hidden


class Pile:
    def __init__(
        self,
        target,
        start_x=0,
        start_y=0,
        top_card_hidden=True,
        other_cards_hidden=True,
        layout_horizontal=True,
        layout_direction=0,
        layout_offset=0,
    ):
        self._target = target
        self._start_x = self._next_x = start_x
        self._start_y = self._next_y = start_y
        self._top_card_hidden = top_card_hidden
        self._other_cards_hidden = other_cards_hidden
        self._layout_horizontal = (
            layout_horizontal  # True = horizontal, False = vertical
        )
        self._layout_direction = layout_direction  # +1 = left-to-right / top-to-bottom, -1 = right-to-left / bottom-to-top, 0 = no offset
        self._layout_offset = layout_offset  # Amount of space to shift each card (stacking_offset_x, stacking_offset_y, Cards.width, Cards.height or 0)
        self._in_pile = []

    def clear(self):  # Remove all cards from the pile
        self._in_pile.clear()
        self._next_x = self._start_x
        self._next_y = self._start_y

    def place(self, card, top_card=False):  # Place a card on the pile
        self._in_pile.append(card)

        if top_card:
            hidden = self._top_card_hidden
        else:
            hidden = self._other_cards_hidden

        dirty = card.render(self._target, self._next_x, self._next_y, hidden=hidden)
        if self._layout_horizontal == True:
            self._next_x += self._layout_direction * self._layout_offset
        else:
            self._next_y += self._layout_direction * self._layout_offset
        return dirty

    def pull(self, card):  # Remove a card from the pile
        pass

    def shuffle(self):  # Shuffle the pile
        pass

    def sort(self):  # Sort the pile
        pass

    @property
    def in_pile(self):
        return list(self._in_pile)


class Hand(Pile):
    def __init__(self, is_dealer=False, **kwargs):
        self._is_dealer = is_dealer
        super().__init__(**kwargs)


class Cards(Pile):

    _positions = {
        "Ace": [(2, 3)],
        "2": [(2, 0), (2, 6)],
        "3": [(2, 0), (2, 3), (2, 6)],
        "4": [(1, 0), (3, 0), (1, 6), (3, 6)],
        "5": [(1, 0), (3, 0), (2, 3), (1, 6), (3, 6)],
        "6": [(1, 0), (3, 0), (1, 3), (3, 3), (1, 6), (3, 6)],
        "7": [(1, 0), (3, 0), (1, 3), (2, 1), (3, 3), (1, 6), (3, 6)],
        "8": [(1, 0), (3, 0), (1, 3), (2, 1), (2, 5), (3, 3), (1, 6), (3, 6)],
        "9": [(1, 0), (3, 0), (1, 2), (3, 2), (2, 3), (1, 4), (3, 4), (1, 6), (3, 6)],
        "10": [
            (1, 0),
            (3, 0),
            (1, 2),
            (3, 2),
            (2, 1),
            (2, 5),
            (1, 4),
            (3, 4),
            (1, 6),
            (3, 6),
        ],
        "Jack": [],
        "Queen": [],
        "King": [],
    }

    _suit_glyphs = {
        HEARTS: chr(0x03),  # '♥'
        DIAMONDS: chr(0x04),  # '♦'
        CLUBS: chr(0x05),  # '♣'
        SPADES: chr(0x06),  # '♠'
    }

    _cmp_colors_must_match = False
    _cmp_suits_must_match = False
    _cmp_rank_order = [ACE, TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE, TEN, JACK, QUEEN, KING]
    # if empty, all are equal; if len()=1, that suit is trump; if len()=4, they are ordered
    _cmp_suit_order = []

    def __init__(
        self,
        width,
        height,
        palette,
        num_decks=1,
        table_color=None,
        suits=SUITS,
        ranks=RANKS,
    ):
        self.set_dimensions(width, height)
        self._palette = palette
        self._num_decks = num_decks
        self._table_color = table_color if table_color is not None else palette.GREEN
        self._suits = suits
        self._ranks = ranks
        self._back_color = palette.BLUE
        self._border_color = palette.BLACK
        self._bg_color = palette.WHITE

        self._suit_colors = {
            HEARTS: palette.RED,
            DIAMONDS: palette.RED,
            CLUBS: palette.BLACK,
            SPADES: palette.BLACK,
        }

        self._all_cards = [
            Card(suit, rank, self)
            for suit in self._suits
            for rank in self._ranks
            for _ in range(num_decks)
        ]
        self._in_deck = []
        self._in_play = []
        self._in_discard = []
        self.shuffle()

    def set_dimensions(self, width, height):
        self._sfw = 8  # Small font width
        self._sfh = 16  # Small font height
        self._lfs = 2  # Large font scale
        self._lfw = 8  # Large font width
        self._lfh = 16  # Large font height
        self._fcs = 6  # Face card scale
        self._width = width  # Width of card including padding
        self._height = height  # Height of card including padding
        self._is_small = height < 90
        self._stack_offset_x = (
            width // 5
        )  # Amount of space to leave between cards stacked horizontally
        self._stack_offset_y = (
            height // 4
        )  # Amount of space to leave between cards stacked vertically
        self._draw_width = width * 9 // 10  # Width of card excluding padding
        self._draw_height = height * 9 // 10  # Height of card excluding padding
        self._x_offset = width // 20  # Offset from left edge of card to start drawing
        self._y_offset = height // 20  # Offset from top edge of card to start drawing
        self._radius = width // 10  # Radius of rounded corners

        # These are the positions of the suit glyphs and card values on the card
        self._x_positions = [i * self._draw_width // 10 for i in range(1, 10, 2)]
        self._y_positions = [i * self._draw_height // 10 for i in range(1, 10, 2)]
        self._y_positions.extend(
            [
                self._y_positions[0]
                + i * ((self._y_positions[4] - self._y_positions[0]) // 3)
                for i in range(1, 3)
            ]
        )
        self._y_positions.sort()

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def stack_offset_x(self):
        return self._stack_offset_x

    @property
    def stack_offset_y(self):
        return self._stack_offset_y

    @property
    def in_deck(self):
        return self._in_deck

    @property
    def in_play(self):
        return self._in_play

    @property
    def in_discard(self):
        return self._in_discard

    @property
    def all_cards(self):
        return self._all_cards

    def __len__(self):
        return len(self._in_deck)

    def shuffle(self):
        # Move all cards back into the deck
        self._in_deck = [card for card in self._all_cards]
        self._in_play.clear()
        self._in_discard.clear()

    def discard(self, card):
        self._in_play.remove(card)
        self._in_discard.append(card)

    def draw_one(self):
        if self._in_deck:
            card = random.choice(self._in_deck)
            self._in_deck.remove(card)
            self._in_play.append(card)
            return card
        else:
            raise ValueError("No cards left in the deck")

    def draw(self, quantity=1):
        return [self.draw_one() for _ in range(quantity)]

    def erase(self, target, x, y):
        draw_x = x + self._x_offset
        draw_y = y + self._y_offset

        return target.fill_rect(
            draw_x,
            draw_y,
            self._draw_width + 1,
            self._draw_height + 1,
            self._table_color,
        )

    def render(self, card, target, x, y, hidden=True):
        draw_x = x + self._x_offset
        draw_y = y + self._y_offset

        # Save the state of the card
        card.save_state(target, x, y, hidden)

        # Draw the card background
        dirty = pygraphics.round_rect(
            target,
            draw_x,
            draw_y,
            self._draw_width,
            self._draw_height,
            self._radius,
            self._bg_color,
            True,
        )

        # Draw the card border
        pygraphics.round_rect(
            target,
            draw_x,
            draw_y,
            self._draw_width,
            self._draw_height,
            self._radius,
            self._border_color,
            False,
        )

        if hidden:
            # Draw the card back
            pygraphics.round_rect(
                target,
                draw_x + 2,
                draw_y + 2,
                self._draw_width - 4,
                self._draw_height - 4,
                self._radius,
                self._back_color,
                True,
            )
            return

        # Draw the card value in the top left corner
        pygraphics.text16(
            target,
            card.value,
            draw_x + self._x_positions[0] - len(card.value) * self._lfw // 2,
            draw_y + self._y_positions[0] - self._lfh // 2,
            self._suit_colors[card.suit],
        )

        # Draw the card value in the bottom right corner
        pygraphics.text16(
            target,
            card.value,
            draw_x + self._x_positions[4] - len(card.value) * self._lfw // 2,
            draw_y + self._y_positions[6] - self._lfh // 2,
            self._suit_colors[card.suit],
            inverted=True,
        )

        # Draw the suit glyph in the top left corner
        pygraphics.text16(
            target,
            self._suit_glyphs[card.suit],
            draw_x + self._x_positions[0] - self._sfw // 2,
            draw_y + self._y_positions[0] + self._lfh // 2,
            self._suit_colors[card.suit],
        )

        # Draw the suit glyph in the bottom right corner
        pygraphics.text16(
            target,
            self._suit_glyphs[card.suit],
            draw_x + self._x_positions[4] - self._sfw // 2,
            draw_y + self._y_positions[6] - self._lfh - self._sfh // 2,
            self._suit_colors[card.suit],
            inverted=True,
        )

        # Skip drawing the suit glyph if the cards are small
        if self._is_small:
            return

        # Draw the suit glyph on the grid (on Ace through 10)
        for x_pos, y_pos in self._positions[card.rank]:
            pygraphics.text16(
                target,
                self._suit_glyphs[card.suit],
                draw_x + self._x_positions[x_pos] - self._lfs * self._lfw // 2,
                draw_y + self._y_positions[y_pos] - self._lfs * self._lfh // 2,
                self._suit_colors[card.suit],
                scale=self._lfs,
                inverted=y_pos > 3,
            )

        # Draw a large letter on face cards instead of a graphic
        if card.rank in ["Jack", "Queen", "King"]:
            pygraphics.text16(
                target,
                card.value[0],
                draw_x + self._x_positions[2] - self._fcs * self._lfw // 2,
                draw_y + self._y_positions[3] - self._fcs * self._lfh // 2,
                self._suit_colors[card.suit],
                scale=self._fcs,
            )

        return dirty

    def compare(self, card1, card2, comparison=0):
        if self._cmp_suit_order:
            if suit1_score := self._cmp_suit_order.count(card1.suit):
                suit1_score = 4 - self._cmp_suit_order.index(card1.suit)
            if suit2_score := self._cmp_suit_order.count(card2.suit):
                suit2_score = 4 - self._cmp_suit_order.index(card1.suit)
            if (suit_comparison := sign(suit1_score - suit2_score)) != 0:
                return suit_comparison == comparison
        return (
            sign(
                self._cmp_rank_order.index(card1.rank)
                - self._cmp_rank_order.index(card2.rank)
            )
            == comparison
        )


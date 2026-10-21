# gallery: skip
# deps: palettes, pygraphics
# utils: displaybuf
"""
Blackjack with the playing_cards classes: tap Play to deal, Hit or Stand to
play your hand against the dealer, and Exit (or close the window) to quit.

The cards draw into a displaybuf DisplayBuffer, which pushes only the changed
area to the display.

It waits for clicks in a loop that never yields, so it runs from a desktop or a
board but not in the browser gallery.
"""

from board_config import display_drv
import board_config
import appdev

app = appdev.App(board_config)
from displaybuf import DisplayBuffer
from palettes import get_palette
from playing_cards import Cards, Hand
from time import sleep


display_drv.rotation = 90
ssd = DisplayBuffer(display_drv)

palette = get_palette(color_depth=16)
ssd.color_palette = palette


# fmt: off
VALUES = { "Ace": 11, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "10": 10, "Jack": 10, "Queen": 10, "King": 10}
# fmt: on


class Game(Cards):
    # override compare_rules and/or compare method if desired
    def __init__(self, target, palette):

        card_width = display_drv.width // 5
        card_height = int(card_width * 7 / 5)
        super().__init__(card_width, card_height, palette)
        self.show = target.show if hasattr(target, "show") else lambda *_: None
        self.dealer = Hand(
            True,
            target=target,
            start_x=0,
            start_y=0,
            top_card_hidden=True,
            other_cards_hidden=False,
            layout_horizontal=True,
            layout_direction=1,
            layout_offset=self.width,
        )
        self.player1 = Hand(
            False,
            target=target,
            start_x=0,
            start_y=target.height - self.height,
            top_card_hidden=False,
            other_cards_hidden=False,
            layout_horizontal=True,
            layout_direction=1,
            layout_offset=self.width,
        )
        self._target = target
        target.fill(self._table_color)
        button_height = int(target.height - self.height * 2) - 10
        button_y = int((target.height - button_height) // 2)
        self.button1 = Button(
            10,
            button_y,
            50,
            button_height,
            palette.BLUE,
            "Play",
            palette.WHITE,
            target,
        )
        self.button2 = Button(
            target.width - 60,
            button_y,
            50,
            button_height,
            palette.BLUE,
            "Exit",
            palette.WHITE,
            target,
        )
        self.show()
        self.loop()

    def reset(self, area=None):
        if area:
            self.show(self._target.fill_rect(*area, self._table_color))
        for card in self.in_play:
            self.show(card.erase())
        self.player1.clear()
        self.dealer.clear()
        self.shuffle()

    # Function to calculate the total value of a hand
    @staticmethod
    def calculate_hand_value(hand):
        value = 0
        num_aces = 0
        for card in hand:
            value += VALUES[card.rank]
            if card.rank == "Ace":
                num_aces += 1
        while value > 21 and num_aces > 0:
            value -= 10
            num_aces -= 1
        return value

    def poll(self):
        ret = None
        for event in app.poll():
            if event.type == app.events.QUIT:
                raise SystemExit
            if event.type == app.events.MOUSEBUTTONDOWN and event.button == 1:
                x, y = event.pos
                for button in [self.button1, self.button2]:
                    if button.hit_test(x, y):
                        ret = button.text().lower()
        return ret

    def loop(self):
        last_message_area = None
        while True:
            for event in app.poll():
                if event.type == app.events.QUIT:
                    return
                if event.type == app.events.MOUSEBUTTONDOWN and event.button == 1:
                    x, y = event.pos
                    if self.button1.hit_test(x, y):
                        last_message_area = self.play_hand(last_message_area)
                        self.show(self.button1.text("Play"))
                        self.show(self.button2.text("Exit"))
                    elif self.button2.hit_test(x, y):
                        return

    def play_hand(self, last_message_area):
        self.reset(last_message_area)
        self.show(self.button1.text("Hit"))
        self.show(self.button2.text("Stand"))

        self.show(self.player1.place(self.draw_one()))
        self.show(self.dealer.place(self.draw_one()))
        self.show(self.player1.place(self.draw_one()))
        self.show(self.dealer.place(self.draw_one(), top_card=True))

        # Player's turn
        while True:
            if choice := self.poll():
                if choice == "hit":
                    self.show(self.player1.place(self.draw_one()))
                    if self.calculate_hand_value(self.player1.in_pile) > 21:
                        self.show(self.dealer.in_pile[1].reveal())
                        text = "Player busts!\nDealer wins."
                        return self.print_message(text, self._palette.RED)
                elif choice == "stand":
                    break

        # Dealer's turn

        self.show(self.dealer.in_pile[1].reveal())
        while self.calculate_hand_value(self.dealer.in_pile) < 17:
            self.show(self.dealer.place(self.draw_one()))

        # Determine the winner
        player_value = self.calculate_hand_value(self.player1.in_pile)
        dealer_value = self.calculate_hand_value(self.dealer.in_pile)
        # print("Player's total hand:", self.player1.in_pile)
        # print("Dealer's hand:", self.dealer.in_pile)
        # print(f"{player_value=}, {dealer_value=}")
        if player_value > 21:
            text = "Player busts!\nDealer wins."
        elif dealer_value > 21:
            text = "Dealer busts!\nPlayer wins."
        elif player_value > dealer_value:
            text = "Player wins!"
        elif player_value < dealer_value:
            text = "Dealer wins!"
        else:
            text = "It's a tie!"
        # print(text, "\n")
        return self.print_message(text, self._palette.RED)

    def print_message(self, text, color):
        dirty = self._target.text16(
            text,
            (self._target.width - 8 * len(text.split("\n")[0])) // 2,
            (self._target.height // 2) - 16,
            color,
        )
        self.show(dirty)
        return dirty


class Button:
    def __init__(self, x, y, width, height, color, text, text_color, target):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.radius = min(width, height) // 4
        self.color = color
        self.text_color = text_color
        self.target = target
        self._text = ""
        self.text(text)

    def draw(self, pressed=False):
        self.target.text16(
            " ", 0, 0, 0x0
        )  # Initialize the font so we can get the width and height
        color = self.color if not pressed else ~self.color & 0xFFFF
        dirty = self.target.round_rect(
            self.x, self.y, self.width, self.height, self.radius, color, True
        )
        dirty += self.target.text16(
            self._text,
            self.x + (self.width - 8 * len(self._text)) // 2,
            self.y + (self.height - 16) // 2,
            self.text_color,
        )
        return dirty

    def hit_test(self, x, y):
        pressed = (
            self.x <= x < self.x + self.width and self.y <= y < self.y + self.height
        )
        if pressed:  # Show the button as pressed
            self.target.show(self.draw(True))
            # sleep(0.25)
            self.target.show(self.draw())
        return pressed

    def text(self, value=None):
        if value is None:
            return self._text
        self._text = value
        return self.draw()


game = Game(ssd, palette)

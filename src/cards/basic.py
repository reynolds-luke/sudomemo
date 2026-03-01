from textual.widgets import Markdown

from cards.base import Card


class CardBasic(Card):
    def __init__(self, card_front, card_back):
        super().__init__()
        self.card_front = card_front
        self.card_back = card_back

    def mount_front(self, c):
        c.mount(Markdown(self.card_front))

    def mount_back(self, c):
        c.mount(Markdown(self.card_back))

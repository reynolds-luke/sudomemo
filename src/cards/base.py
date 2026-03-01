from textual.containers import Container
from textual.app import ComposeResult
from textual.widgets import Rule, Label
from textual.widget import Widget

from messages import CardFlipped


class CardBackSep(Widget):
        DEFAULT_CLASSES = "card"

        def compose(self) -> ComposeResult:
                yield Rule()
                yield Label("↓↓↓ CARD BACK ↓↓↓", id="card_info_sep")
                yield Rule()


class Card(Widget):
    def compose(self):
        self.container = Container(id="card_info")
        yield self.container

    def on_mount(self):
        self.mount_front(self.container)

    def on_card_flipped(self, message: CardFlipped) -> None:
        self.container.mount(CardBackSep())
        self.mount_back(self.container)

        self.container.children[-1].scroll_visible()

    def mount_front(self, c):
        """Subclass must implement."""
        raise NotImplementedError

    def mount_back(self, c):
        """Subclass must implement"""
        raise NotImplementedError

    def force_flip(self):
        self.app.screen.action_flip()

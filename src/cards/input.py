from difflib import SequenceMatcher

from textual.containers import Container, HorizontalGroup
from textual.widgets import Input, Label, Markdown

from cards.base import Card


class Redline(Container):
    DEFAULT_CSS = """
    Redline .redline {
        width: 1fr;
        text-align: center;
        align-horizontal: center;
    }

    Redline .diff_delete {
        color: $error;
        background: $error 20%;
    }

    Redline .diff_add {
        color: $success;
        background: $success 20%;
    }
    """
    def __init__(self, src, tgt):
        super().__init__()
        self.src = src
        self.tgt = tgt

    def create_redline(self):
        matcher = SequenceMatcher(a=self.src, b=self.tgt)

        for code, a1, a2, b1, b2 in matcher.get_opcodes():
            if code == "equal":
                self.src_cont.mount(Label(self.src[a1:a2]))
                self.tgt_cont.mount(Label(self.tgt[b1:b2]))
            if code == "delete":
                self.src_cont.mount(Label(self.src[a1:a2], classes="diff_delete"))
            if code == "insert":
                self.tgt_cont.mount(Label(self.tgt[b1:b2], classes="diff_add"))
                self.src_cont.mount(Label("-"*(b2-b1), classes="diff_add"))
            if code == "replace":
                self.src_cont.mount(Label(self.src[a1:a2], classes="diff_delete"))
                self.tgt_cont.mount(Label(self.tgt[b1:b2], classes="diff_add"))

    def compose(self):
        self.src_cont = HorizontalGroup(classes="redline")
        self.tgt_cont = HorizontalGroup(classes="redline")

        yield self.src_cont

    def on_mount(self):
        if self.src == self.tgt:
            self.src_cont.mount(Label(f"✓  {self.src}  ✓"))
        else:
            self.mount(Label("↓", classes="redline"))
            self.mount(self.tgt_cont)

            self.create_redline()


class CardBasicInput(Card):
    def __init__(self, card_front, answer, card_back=None):
        super().__init__()
        self.card_front = card_front
        self.answer     = answer

        self.card_back = card_back
        if self.card_back:
            if len(self.card_back) == 0:
                self.card_back = None

    def mount_front(self, c):
        c.mount(Markdown(self.card_front))
        text_input = Input(placeholder="Type Here.", id="card_input")

        c.mount(text_input)
        text_input.focus()

    def mount_back(self, c):
        c.mount(Redline(self.query_one(Input).value, self.answer))
        if self.card_back:
            c.mount(Markdown(self.card_back))
        self.query_one("#card_input").disabled = True

    def on_input_submitted(self, value):
        self.force_flip()

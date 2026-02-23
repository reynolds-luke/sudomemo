from textual.containers import Container, HorizontalGroup
from textual.app import ComposeResult
from textual.widgets import Rule, Label, Markdown, Input
from textual.widget import Widget

from difflib import SequenceMatcher

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

	def on_card_flipped(self):
		self.container.mount(CardBackSep())
		self.mount_back(self.container)

		self.container.children[-1].scroll_visible()

	def mount_front(self, c):
		"""Subclass must implement."""
		raise NotImplementedError

	def mount_back(self, c):
		"""Subclass must implement"""
		raise NotImplimentedError


class CardBasic(Card):
	def __init__(self, card_front, card_back):
		super().__init__()
		self.card_front = card_front
		self.card_back = card_back

	def mount_front(self, c):
		c.mount(Markdown(self.card_front))

	def mount_back(self, c):
		c.mount(Markdown(self.card_back))


class Redline(Container):
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
	def __init__(self, card_front, answer, card_back):
		super().__init__()
		self.card_front = card_front
		self.answer 	= answer
		self.card_back 	= card_back

	def mount_front(self, c):
		c.mount(Markdown(self.card_front))
		text_input = Input(placeholder="Type Here.")

		c.mount(text_input)
		text_input.focus()

	def mount_back(self, c):
		c.mount(Redline(self.query_one(Input).value, self.answer))
		c.mount(Markdown(self.card_back))

from textual.app import ComposeResult
from textual.containers import Container, HorizontalGroup
from textual.widgets import Markdown, Label, Input, Static, Rule
from textual.widget import Widget
from difflib import SequenceMatcher

from messages import CardFlipped

front = "example_front"
back = "example_back"

class CardBackSep(Widget):
	DEFAULT_CLASSES = "card"

	def compose(self) -> ComposeResult:
		self.add_class("card_back")
		yield Rule()
		yield Label("↓↓↓ CARD BACK ↓↓↓", id="card_info_sep")
		yield Rule()


class CardBasic(Widget):
	DEFAULT_CLASSES = "card"

	def compose(self) -> ComposeResult:
		with Container(id="card_info"):
			yield Markdown(front)
			yield CardBackSep()
			yield Markdown(back, id="card_back_text", classes="card_back")

	def on_card_flipped(self, message: CardFlipped):
		self.query_one("#card_back_text").scroll_visible()

class CardBasicInput(Widget):
	def char_redline(self, src: str, tgt: str, src_cont, tgt_cont) -> None:
		matcher = SequenceMatcher(a=src, b=tgt)

		for code, a1, a2, b1, b2 in matcher.get_opcodes():
			if code == "equal":
				src_cont.mount(Label(src[a1:a2]))
				tgt_cont.mount(Label(tgt[b1:b2]))
			if code == "delete":
				src_cont.mount(Label(src[a1:a2], classes="diff_delete"))
			if code == "insert":
				tgt_cont.mount(Label(tgt[b1:b2], classes="diff_add"))
				src_cont.mount(Label("-"*(b2-b1), classes="diff_add"))
			if code == "replace":
				src_cont.mount(Label(src[a1:a2], classes="diff_delete"))
				tgt_cont.mount(Label(tgt[b1:b2], classes="diff_add"))

	def compose(self) -> ComposeResult:
		with Container(id="card_info"):
			yield Markdown("example front")
			yield Input(placeholder="your input here")
			yield CardBackSep()
			yield HorizontalGroup(id="redline_src", classes="redline card_back")
			yield Label("↓",id="redline_arrow", classes="redline card_back")
			yield HorizontalGroup(id="redline_tgt", classes="redline card_back")
			yield Markdown("optional back extra.", id="card_back_text", classes="card_back")

	def on_mount(self):
		self.query_one(Input).focus()

	def on_card_flipped(self, message: CardFlipped):
		self.query_one("#redline_tgt").scroll_visible()
		input_widget = self.query_one(Input)
		input_widget.disabled = True
		src_cont = self.query_one("#redline_src")
		tgt_cont = self.query_one("#redline_tgt")
		self.char_redline(input_widget.value, "hello world", src_cont, tgt_cont)

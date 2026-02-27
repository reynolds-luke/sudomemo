from textual.screen import Screen
from textual.containers import Container, HorizontalGroup
from textual.app import ComposeResult
from textual.widgets import Rule, Label, Markdown, Input, RadioButton, RadioSet
from textual.widget import Widget

import random
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

	def on_card_flipped(self, message: CardFlipped) -> None:
		self.container.mount(CardBackSep())
		self.mount_back(self.container)

		self.container.children[-1].scroll_visible()

	def mount_front(self, c):
		"""Subclass must implement."""
		raise NotImplementedError

	def mount_back(self, c):
		"""Subclass must implement"""
		raise NotImplimentedError

	def force_flip(self):
		self.app.screen.action_flip()


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
	def __init__(self, card_front, answer, card_back=None):
		super().__init__()
		self.card_front = card_front
		self.answer 	= answer

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

class CardChoices(Card):
	DEFAULT_CSS = """
	CardChoices #answer_cont {
		width: 1fr;
		align-horizontal: center;
	}

	CardChoices HorizontalGroup {
		width: auto;
	}

	CardChoices .incorrect {
		color: $error;
		background: $error 20%;
	}

	CardChoices .correct {
		color: $success;
		background: $success 20%;
	}
	"""

	BINDINGS = [("j", "next_button", "Next option"),
		    ("k", "previous_button", "Previous option")]

	def __init__(self, card_front, options, card_back=None):
		super().__init__()
		self.card_front = card_front
		self.correct = options[0] # assume correct answer always provided as correct answer.
		self.options = options
		random.shuffle(self.options)


		self.card_back = card_back
		if self.card_back:
			if len(self.card_back) == 0:
				self.card_back = None

	def mount_front(self, c):
		c.mount(Markdown(self.card_front))

		radioset = RadioSet(id="card_radio")
		c.mount(radioset)

		for n, option in enumerate(self.options):
			radioset.mount(RadioButton(option, id=f"radio_opt_{n}"))

		radioset.focus()

	def mount_back(self, c):
		pressed_id = self.query_one("#card_radio").pressed_index
		if pressed_id >= 0:
			selected_answer = self.options[pressed_id]
		else:
			selected_answer = "None"

		answer_cont = Container(id="answer_cont")
		c.mount(answer_cont)

		if selected_answer == self.correct:
			answer_cont.mount(Label(f"✓  {self.correct}  ✓"))
		else:
			answer_cont.mount(HorizontalGroup(	Label("You chose: "),
							  	Label(selected_answer, classes="incorrect")
							  ))
			answer_cont.mount(HorizontalGroup(	Label("Correct  : "),
						          	Label(self.correct, classes="correct")
							))

		if self.card_back:
			c.mount(Markdown(self.card_back))

		self.query_one("#card_radio").disabled = True

	def action_next_button(self) -> None:
		radioset = self.query_one("#card_radio")
		radioset.action_next_button()

	def action_previous_button(self) -> None:
		radioset = self.query_one("#card_radio")
		radioset.action_previous_button()

	def action_choose(self, index: int) -> None:
		radioset = self.query_one("#card_radio")
		buttons = radioset.query(RadioButton)

		if 0 <= index < len(buttons):
			buttons[index].value = True

	def on_radio_set_changed(self, event: RadioButton.Changed) -> None:
		self.force_flip()

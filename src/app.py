from textual.app import App, ComposeResult
from textual.containers import Container,  Horizontal, VerticalScroll
from textual.widgets import Footer, Button, Markdown, Rule, Label
from textual.widget import Widget

front = """Prove that sqrt(2) is irrational."""

back = """We prove by contradiction.

1. Assume sqrt(2) is rational.
   Then it can be written as a fraction a/b in lowest terms,
   where a and b are integers with no common factors.

2. Square both sides:
   2 = a^2 / b^2
   So a^2 = 2 b^2.

3. This shows a^2 is even, since it equals 2 times an integer.
   If a^2 is even, then a must also be even.
   So let a = 2k for some integer k.

4. Substitute back:
   a^2 = (2k)^2 = 4k^2
   So 4k^2 = 2 b^2
   Divide by 2:
   2k^2 = b^2.

5. Now b^2 is even, so b is even.

6. We have shown both a and b are even,
   meaning they share a factor of 2.
   This contradicts the assumption that a/b was in lowest terms.

7. Therefore our assumption was false,
   and sqrt(2) is irrational."""


class Flashcard(Widget):
	def compose(self) -> ComposeResult:
		yield VerticalScroll(
			Container(
				Markdown(front),
				Label("↓↓↓CARD BACK↓↓↓", id="card_info_sep", classes="card_back"),
				Markdown(back, id="card_back_text", classes="card_back"),
				id="card_info"
				),
			Horizontal(
				Button("Flip ⏎", id="flip"),
				Button("Fail (1)", id="feedback_fail", classes="feedback", variant="error"),
				Button("Hard (2)", id="feedback_hard", classes="feedback", variant="warning"),
				Button("Good (3)", id="feedback_good", classes="feedback", variant="primary"),
				Button("Easy (4)", id="feedback_easy", classes="feedback", variant="success"),
				id="button_row",
				),
			)

	def on_button_pressed(self, event: Button.Pressed) -> None:
		if event.button.has_class("feedback"):
			self.app.process_feedback(event.button.id)
		else:	#otherwise it is a reveal button
			self.flip_card()

		self.app.set_focus(None)

	def flip_card(self):
		self.app.add_class("revealed")
		self.query_one("#card_back_text").scroll_visible()
		self.refresh_bindings()


class MyApp(App):
	CSS_PATH = "style.css"
	BINDINGS = [
		("1", "feedback_fail", "Fail"),
		("2", "feedback_hard", "Hard"),
		("3", "feedback_good", "Good"),
		("4", "feedback_easy", "Easy"),
		("enter", "flip", "Flip Card")
	]
	def on_mount(self):
		self.theme = "rose-pine-moon"
		self.state = "review"

	def compose(self) -> ComposeResult:
		yield Flashcard()
		yield Footer()

	def process_feedback(self, id):
		self.query_one(Flashcard).remove()
		self.mount(Markdown(id))
		self.state = "display"
		self.refresh_bindings()

	def action_flip(self):
		self.query_one(Flashcard).flip_card()

	def action_feedback_fail(self):
		self.process_feedback("feedback_fail")

	def action_feedback_hard(self):
		self.process_feedback("feedback_hard")

	def action_feedback_good(self):
		self.process_feedback("feedback_good")

	def action_feedback_easy(self):
		self.process_feedback("feedback_easy")

	def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
		if "feedback" in action:
			return self.state == "review" and self.has_class("revealed")
		if action == "flip":
			return self.state == "review" and  not self.has_class("revealed")
		return True
MyApp().run()

from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.containers import Container,  Horizontal, VerticalScroll
from textual.widgets import Footer, Button, Markdown, Rule, Label, Input
from textual.widget import Widget

from enum import Enum

from messages import CardFlipped
# from cards.flashcards import CardBasic, CardBasicInput
from cards.base import CardBasicInput, Card

class ReviewScreen(Screen):
	CSS_PATH = "style.css"
	BINDINGS = [
		("1", "feedback_fail", "Fail"),
		("2", "feedback_hard", "Hard"),
		("3", "feedback_good", "Good"),
		("4", "feedback_easy", "Easy"),
		("enter", "flip", "Flip Card"),
		("n", "next", "Next Card")
	]

	class AppState(Enum):
		REVIEW   = "review"
		FEEDBACK = "feedback"


	def on_mount(self):
		self.app.theme = "rose-pine-moon"
		self.state = self.AppState.REVIEW

		self.mount_card()

	def compose(self) -> ComposeResult:
		yield Footer()

	def mount_card(self):
		self.mount(VerticalScroll(
				CardBasicInput("Good Morning", "buenos días", ""),
				Horizontal(
					Button("Flip ⏎", id="flip", variant="primary"),
					Button("Fail (1)", id="feedback_fail", classes="feedback", variant="error"),
					Button("Hard (2)", id="feedback_hard", classes="feedback", variant="warning"),
					Button("Good (3)", id="feedback_good", classes="feedback", variant="primary"),
					Button("Easy (4)", id="feedback_easy", classes="feedback", variant="success"),
					id="button_row",
					),
				id = "flashcard"
				)
			)

	def on_input_submitted(self, event: Input.Submitted):
		self.action_flip()

	def on_button_pressed(self, event: Button.Pressed) -> None:
		if event.button.has_class("feedback"):
			self.process_feedback(event.button.id)
		else: # otherwise, its the flip button.
			self.action_flip()

	def action_flip(self):
		self.app.set_focus(None)
		self.add_class("revealed")
		self.refresh_bindings()

		self.query_one(Card).post_message(CardFlipped())

	def process_feedback(self, id):
		self.remove_class("revealed")

		self.query_one("#flashcard").remove()
		self.mount(Markdown(id))
		self.state = self.AppState.FEEDBACK
		self.refresh_bindings()

	def action_feedback_fail(self):
		self.process_feedback("feedback_fail")

	def action_feedback_hard(self):
		self.process_feedback("feedback_hard")

	def action_feedback_good(self):
		self.process_feedback("feedback_good")

	def action_feedback_easy(self):
		self.process_feedback("feedback_easy")

	def action_next(self):
		self.query_one(Markdown).remove()
		self.mount_card()

		self.state = self.AppState.REVIEW
		self.refresh_bindings()
		self.set_focus(self)

	def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
		if "feedback" in action:
			return self.state == self.AppState.REVIEW and self.has_class("revealed")
		if action == "flip":
			return self.state == self.AppState.REVIEW and not self.has_class("revealed")
		if action == "next":
			return self.state == self.AppState.FEEDBACK
		return True

class MyApp(App):
        SCREENS = {"review": ReviewScreen}

        def on_mount(self):
                self.push_screen("review")

MyApp().run()

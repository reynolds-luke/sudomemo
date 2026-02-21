from textual.app import App, ComposeResult
from textual.widgets import Button, Static, Markdown, Footer, Rule


example_markdown ="""\
## Quick test

Here is a quick test.

- go to store
- buy milk
- die
```python
for i in range(10):
	print(i)

print("hello world")
```

**bold**, *italics*, `inline code`
"""


class Flashcard(Static):
	def compose(self) -> ComposeResult:
		yield Markdown(example_markdown, classes="card_front")
		yield Rule(line_style="double", classes="card_front")
		yield Markdown(example_markdown, classes="card_back")
		yield Rule(line_style="double", classes="card_back")
		yield ButtonRow()


class ButtonRow(Static):
	def compose(self) -> ComposeResult:
		yield Button("Reveal", classes="reveal", variant="primary")
		yield Button("Fail (1)", id="fail", classes="feedback", variant="error")
		yield Button("Hard (2)", id="hard", classes="feedback", variant="warning")
		yield Button("Good (3)", id="good", classes="feedback", variant="success")

	def on_button_pressed(self, event: Button.Pressed) -> None:
		if event.button.has_class("feedback"):
			self.app.show_next_card()
		else:	# otherwise it is a reveal card
			self.app.add_class("revealed")
			self.refresh_bindings()

		self.app.set_focus(None)

class myApp(App):
	CSS_PATH = "style.css"
	BINDINGS = [
		("1", "feedback_fail", "Fail"),
		("2", "feedback_hard", "Hard"),
		("3", "feedback_good", "Good")
	]
	AUTO_FOCUS = ""

	def on_mount(self):
		self.theme = "tokyo-night"

	def compose(self):
		yield Footer()
		yield Flashcard()

	def show_next_card(self):
		self.query_one(Flashcard).remove()

	def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
		if "feedback" in action:
			if self.has_class("revealed"):
				return True
			else:
				return False
		return True
if __name__ == "__main__":
	myApp().run()

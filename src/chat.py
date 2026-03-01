from textual.app import App, ComposeResult
from textual.widgets import TextArea, Button, Label, Markdown
from textual.widget import Widget
from textual.containers import Horizontal, VerticalScroll, Container
from textual import work
from textual.worker import Worker, get_current_worker

import os
from openai import OpenAI

API_KEY = os.environ["OPENAI_API_KEY"]

messages = []



class Message(Container):
    def __init__(self, text, user):
        super().__init__(classes=f"message user_{user}")
        self.label = Label(text)

    def compose(self) -> ComposeResult:
        yield self.label


class ChatWidget(Widget):
    CSS_PATH = "chat.tcss"
    DEFAULT_CSS = """
    #input_bar {
        height: 5;
        dock: bottom;
    }

    #input_bar Button {
        height: 1fr;
    }

    Message {
        height: auto;
        margin: 1;
    }

    .message Label {
        width: auto;
        max-width: 0.75fr;

        height: auto;
        min-height: 1;
        padding: 1;
        margin: 0;
    }


    Message.user_human {
        align: right top;
    }

    .message.user_human Label {
        background: $success 30%;
    }

    .message.user_ai Label {
        background: $boost;
    }

    """
    def __init__(self):
        super().__init__()
        self.app.theme = "rose-pine-moon"

        self.message_container = VerticalScroll(id="message_container")
        self.input_bar = Horizontal(    TextArea(id="input_text"),
                        Button("Submit", variant="primary"),
                        id = "input_bar")
    def compose(self) -> ComposeResult:
        yield self.message_container
        yield self.input_bar

    def on_button_pressed(self, event: Button.Pressed) -> None:
        user_message = self.input_bar.query_one(TextArea).text
        self.input_bar.query_one(TextArea).text = ""

        self.message_container.mount(Message(user_message, user="human"))
        response = Message("..", user="ai")
        self.message_container.mount(response)

        self.get_response(user_message, response.label)

    @work(exclusive=True, thread=True)
    def get_response(self, message, label):
        client = OpenAI(api_key = API_KEY)

        text = ""

        if message == "":
            message = " "

        with client.responses.stream(
            model="gpt-4.1-mini",
            input=message
        ) as stream:
            for event in stream:
                if event.type == "response.output_text.delta":
                    text += event.delta
                    self.app.call_from_thread(label.update, text)
class MyApp(App):
    def compose(self):
        yield ChatWidget()

app = MyApp()

if __name__ == "__main__":
    app.run()

from textual.app import App, ComposeResult
from textual.widgets import TextArea, Button, Label, Markdown
from textual.widget import Widget
from textual.containers import Horizontal, VerticalScroll, Container
from textual import work
from textual.worker import Worker, get_current_worker
from textual.reactive import reactive

import os
from openai import OpenAI

API_KEY = os.environ["OPENAI_API_KEY"]

messages = []



class Message(Container):
    text = reactive("")
    
    def __init__(self, text, user):
        super().__init__(classes=f"message user_{user}")
        self.label = Label()
        self.text = text

    def compose(self) -> ComposeResult:
        yield self.label

    def watch_text(self, new_text):
        self.label.update(new_text)

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

        self.message_container.scroll_end()
        
        response = Message("...", user="ai")
        self.message_container.mount(response)

        self.get_response(user_message, response)

    @work(exclusive=True, thread=True)
    def get_response(self, message, response_message):
        client = OpenAI(api_key = API_KEY)

        text = ""

        messages = []
        for message in self.message_container.query(Message)[:-1]:
            if message.has_class("user_human"):
                role = "user"
            elif message.has_class("user_ai"):
                role = "assistant"
            else:
                raise Exception("invalis message user detected")

            messages.append({"role": role, "content": str(message.text)})

        if message == "":
            message = " "


        with client.responses.stream(
            model="gpt-4.1-mini",
            input=messages
        ) as stream:
            text = ""
            for event in stream:
                if event.type == "response.output_text.delta":
                    text += event.delta
                    self.app.call_from_thread(setattr, response_message, "text", text)
                    self.app.call_from_thread(self.message_container.scroll_end)
class MyApp(App):
    def compose(self):
        yield ChatWidget()

app = MyApp()

if __name__ == "__main__":
    app.run()

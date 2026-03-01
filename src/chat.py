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


class Message(Container):
    text = reactive("")

    def __init__(self, text, sender):
        super().__init__(classes=f"message user_{sender}")
        self.label = Label()
        self.text = text

    def compose(self) -> ComposeResult:
        yield self.label

    def watch_text(self, new_text):
        self.label.update(new_text)

class ChatWidget(Widget):
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

        self.chat_log = VerticalScroll(id="message_container")
        self.input_bar = Horizontal(    TextArea(id="input_text"),
                        Button("Submit", variant="primary"),
                        id = "input_bar")
    def compose(self) -> ComposeResult:
        yield self.chat_log
        yield self.input_bar

    def on_button_pressed(self, event: Button.Pressed) -> None:
        user_input = self.input_bar.query_one(TextArea).text
        self.input_bar.query_one(TextArea).text = ""
        self.chat_log.mount(Message(user_input, sender="human"))

        self.chat_log.scroll_end()

        reply_widget = Message("...", sender="ai")
        self.chat_log.mount(reply_widget)

        self.get_response(user_input, reply_widget)

    @work(exclusive=True, thread=True)
    def get_response(self, user_input, reply_widget):
        client = OpenAI(api_key = API_KEY)

        history = []
        for bubble in self.chat_log.query(Message)[:-1]:
            if bubble.has_class("user_human"):
                role = "user"
            elif bubble.has_class("user_ai"):
                role = "assistant"
            else:
                raise Exception("invalid message sender detected")

            history.append({"role": role, "content": str(bubble.text)})

        if user_input == "":
            user_input = " "

        with client.responses.stream(
            model="gpt-4.1-mini",
            input=history
        ) as stream:
            reply_text = ""
            for stream_event in stream:
                if stream_event.type == "response.output_text.delta":
                    reply_text += stream_event.delta
                    self.app.call_from_thread(setattr, reply_widget, "text", reply_text)
                    self.app.call_from_thread(self.chat_log.scroll_end)

class MyApp(App):
    def compose(self):
        yield ChatWidget()

app = MyApp()

if __name__ == "__main__":
    app.run()

import streamlit as st
import openai

import datetime
from typing import Iterable, Any
import enum
import json
import pathlib

import coolname
import pytz


class Models(enum.Enum):
    O1_PREVIEW = "o1-preview"
    O1_MINI = "o1-mini"
    GPT_4O_MINI = "gpt-4o-mini"


class Defaults:
    MODEL = Models.GPT_4O_MINI

    # max_tokens -> output
    #
    # max context: 128,000
    # recommending at lest 25k reserved for reasoning at first
    # max_tokens: 32,768
    #
    MAX_TOKENS = 1024

    # max_completion_tokens -> total actually generated (output + reasoning)
    MAX_COMPLETION_TOKENS = 16000


type ConversationId = str
MessageParam = Any  # openai.types.
MessageContent = Any


def generate_conversation_id() -> ConversationId:
    """
    Generate a unique conversation id.
    """
    # Get the current time in PST
    pst_timezone = pytz.timezone("America/Los_Angeles")
    current_time = datetime.datetime.now(pst_timezone)

    # Format the time as ex: 10:06 AM
    timestamp_string = current_time.strftime("%Y-%m-%d_%I:%M_%p")
    unique_coolname = "_".join(coolname.generate())

    return f"{timestamp_string}__{unique_coolname}"


def read_json_file(filepath: pathlib.Path) -> list[MessageParam]:
    """
    Read and return the data from a JSON file.
    """
    with filepath.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json_file(filepath: pathlib.Path, data: list[MessageParam]) -> None:
    """Write data to a JSON file."""

    with filepath.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


class ConversationManager:
    """
    Handles getting and setting conversations and messages using JSON files in a subdirectory.

    Each conversation is stored as a separate JSON file named <conversation-id>.json
    within the 'conversations' directory.

    This approach replaces the use of Streamlit's session state with persistent storage.
    """

    _CONVERSATIONS_DIR = pathlib.Path("conversations")

    def __init__(self) -> None:

        # Create the conversations directory if it doesn't exist
        self._CONVERSATIONS_DIR.mkdir(exist_ok=True)

    def get_conversation_ids(self) -> list[ConversationId]:
        """
        Returns a list of all conversation IDs by listing JSON files in the conversations directory.
        """
        return [filepath.stem for filepath in self._CONVERSATIONS_DIR.glob("*.json")]

    def get_conversation_messages(self, conversation_id: ConversationId) -> list[MessageParam]:
        """
        Retrieves the list of messages for a given conversation ID by loading the corresponding JSON file.
        """
        filepath = self._CONVERSATIONS_DIR / f"{conversation_id}.json"

        st.write(f"Loading conversation from: {filepath.resolve()}")

        return read_json_file(filepath)

    def add_conversation_message(
        self,
        conversation_id: ConversationId,
        message: MessageParam,
    ) -> None:
        """
        Adds a new message to the specified conversation and saves it back to the JSON file.
        """
        filepath = self._CONVERSATIONS_DIR / f"{conversation_id}.json"
        messages = read_json_file(filepath)
        messages.append(message)
        write_json_file(filepath, messages)

    def create_new_conversation(self) -> ConversationId:
        """
        Creates a new conversation by generating a unique ID and initializing an empty JSON file.
        """
        conversation_id = generate_conversation_id()
        filepath = self._CONVERSATIONS_DIR / f"{conversation_id}.json"
        write_json_file(filepath, [])
        return conversation_id


def try_load_json_or_default_to_string(json_string: str) -> str:
    try:
        return json.loads(json_string)
    except json.JSONDecodeError:
        return json_string


def display_message_content(message_content: MessageContent) -> None:

    st.markdown(message_content)


def display_message(message: MessageParam) -> None:
    """

    Annoyingly, this operates on `MessageParam` instead of `Message`, since `UserMessage`s aren't actually a legitimate
    `Message` instance, at least we still have the type checking of `TypedDict`.

    """

    with st.chat_message(message["role"]):

        display_message_content(message["content"])


# TODO(bschoen): Should we make all tools read and write from files, like kubeflow?
def main() -> None:

    # Set Streamlit to wide mode by default
    st.set_page_config(layout="wide")

    # Inline comment explaining the motivation
    # This ensures a wider layout for better content display and user experience

    st.title("Claude UI at home")

    st.markdown(
        """
    Basically Claude UI but using the API internally to avoid low usage limits.

    Source code available at: https://github.com/b-schoen/local_claude
                
    Refresh to clear all conversations.
"""
    )

    # allow selecting model
    selected_model = st.sidebar.selectbox(
        "Model",
        options=[
            Models.GPT_4O_MINI.value,
            Models.O1_PREVIEW.value,
            Models.O1_MINI.value,
        ],
    )

    # initialize conversation manager to handle state
    conversation_manager = ConversationManager()

    # allow creating new conversations
    if st.sidebar.button("New Conversation"):
        conversation_manager.create_new_conversation()

    # select conversation id
    conversation_ids = conversation_manager.get_conversation_ids()

    # if there's no conversations yet, wait until the user creates one
    if not conversation_ids:
        st.info("Select `New Conversation` to create a new conversation")
        return None

    # otherwise, we have at least one conversation, and allow the user to select one
    # we show them in reverse order of creation, so if the user just created one, it's at the top
    selected_conversation_id = st.selectbox(
        "Select Conversation",
        conversation_ids[::-1],
    )

    assert selected_conversation_id

    # show the messages in the selected conversation
    for message in conversation_manager.get_conversation_messages(selected_conversation_id):
        display_message(message)

    # only run if new user input
    if user_message_content := st.chat_input("What is your message?"):

        # we only need to initialize the client when we actually make a call,
        # we're doing slow synchronous calls so this is fine, since user
        # interacts in between each one
        #
        # note: defaults to getting ANTHROPIC_API_KEY from environment
        client = openai.OpenAI()

        user_message: MessageParam = {
            "role": "user",
            "content": user_message_content,
        }

        # add user message to message history
        conversation_manager.add_conversation_message(
            selected_conversation_id,
            user_message,
        )

        # display user message
        display_message(user_message)

        # retrieve history to send to client
        messages = conversation_manager.get_conversation_messages(selected_conversation_id)

        # is_show_messages_between_tool_use_enabled = True

        # if is_show_messages_between_tool_use_enabled:
        #    st.write(messages)

        # TODO(bschoen): Cache subsequent messages instead of just the first
        # note: the full api is `create` and `stream`
        with st.spinner("Thinking..."):

            kwargs = {
                "messages": messages,
                "model": selected_model,
            }

            if selected_model.startswith("o1"):
                kwargs.update({"max_completion_tokens": Defaults.MAX_COMPLETION_TOKENS})
            else:
                kwargs.update({"max_tokens": Defaults.MAX_TOKENS})

            response = client.chat.completions.create(**kwargs)

        # TODO(bschoen): Show usage and potentially limit tokens

        print(f"Response: {response.model_dump_json(indent=2)}")

        # note: using dict representation for consistency with user_message + it's what API expects
        response_message = {
            "role": "assistant",
            "content": response.choices[0].message.content,
        }

        # add response to conversation
        conversation_manager.add_conversation_message(
            selected_conversation_id,
            response_message,
        )

        # display agent message
        display_message(response_message)

        # add response to message history
        messages.append(response_message)


if __name__ == "__main__":
    main()

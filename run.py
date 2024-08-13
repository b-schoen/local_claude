import streamlit as st
import anthropic

import datetime
from typing import Self
import enum

import coolname
import pytz


class Models(enum.Enum):
    CLAUDE_SONNET_3_5 = "claude-3-5-sonnet-20240620"


class Defaults:
    # sonnet 3.5 is smartest model
    MODEL = Models.CLAUDE_SONNET_3_5

    # note: 4096 is usual max
    MAX_TOKENS = 1024

    SYSTEM_PROMPT = """
    You are primarily helping the user on a 2.5 hour coding interview which will involve
    use of docker, python, model function calling / tool use, and likely AI evaluation libraries 
    for a position working on AI evaluations. The user is a software engineer with 8 years of python
    experience, using python 3.12. Note that the use of models is explicitly encouraged during this
    assessment and is in fact explicitly encouraged, as the position involves working closely with
    models.

    For any code you generate, ensure there are inline comments explaining the motivation and
    intuition for all of it, as well as appropriate docstrings and type annotations.

    When iterating on responses, you don't need to include code that hasn't changed since
    previous response.

    Whenever it would make a task easier, feel free to include existing 3rd party libraries.

    If there is an alternative approach that you believe is more promising in fufilling the user's
    overall goal, please feel free to suggest it at the end of your response, even if it is in a
    different direction than the current conversation. You do not need to mention an alternative
    approach if you believe the current one is the most promising.

    """


type ConversationId = str


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


class ConversationManager:
    """
    Handles getting / setting conversations and messages whenever they interact with the `st.session_state` singleton.

    This allows caller to not have to know anything about the singleton usage.

    We wrap messages in a singleton since streamlit reruns every time.

    Note:
      - `st.session_state` is just an arbitrary persistent key-value store, see https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state
      - this is the same pattern used in https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps

    """

    def __init__(self) -> None:

        # initialize if not present yet, this way all other functions
        # can assume there is an initialized `st.session_state.conversations``
        if "conversations" not in st.session_state:

            conversations: dict[ConversationId, list[anthropic.types.MessageParam]] = {}

            st.session_state.conversations = conversations

    def get_conversation_ids(self) -> list[ConversationId]:
        return list(st.session_state.conversations.keys())

    def get_conversation_messages(
        self,
        conversation_id: ConversationId,
    ) -> list[anthropic.types.MessageParam]:
        return st.session_state.conversations[conversation_id]

    def add_conversation_message(
        self,
        conversation_id: ConversationId,
        message: anthropic.types.MessageParam,
    ) -> None:
        st.session_state.conversations[conversation_id].append(message)

    def create_new_conversation(self) -> ConversationId:
        conversation_id = generate_conversation_id()

        st.session_state.conversations[conversation_id] = []

        return conversation_id


def display_message(message: anthropic.types.MessageParam) -> None:
    with st.chat_message(message["role"]):

        content = message["content"]

        # handle displaying just plain string
        if isinstance(content, str):
            st.markdown(content)
            return None

        # handle list from model, content is either string or one of these types:
        # - anthropic.types.TextBlockParam
        # - anthropic.types.ImageBlockParam
        # - anthropic.types.ToolUseBlockParam
        # - anthropic.types.ToolResultBlockParam
        # - anthropic.types.ContentBlock
        if isinstance(content, list):

            for item in content:

                # each item is
                # WOW match with copilot is crazy
                match item.type:
                    case "text":
                        st.markdown(item.text)
                    case "image":
                        st.image(item.source.data)
                    case "tool_use":
                        st.markdown(f"Tool use: {item.name}")
                    case "tool_result":
                        st.markdown(f"Tool result: {item.name}")
                    case "content":
                        st.markdown(f"Content: {item.name}")
                    case _:
                        raise ValueError(f"Unexpected item type: {item.type}")

            # return once we're done displaying all tiems
            return None

        # handle case where we got a dict back or something
        raise ValueError(f"Unexpected content type: {content}")


def main() -> None:

    st.title("Claude UI at home")

    st.markdown(
        """
    Basically Claude UI but using the API internally to avoid low usage limits.

    Source code available at: https://github.com/b-schoen/local_claude
                
    Refresh to clear all conversations.
"""
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

    # allow user to select / edit system prompt, and display it to the user
    st.markdown("### System Prompt")

    # put system prompt inside a collapasible container
    with st.expander("System Prompt - Expand To Edit"):

        selected_system_prompt = st.text_area(
            label="System Prompt",
            value=Defaults.SYSTEM_PROMPT,
            height=300,
        )

    # st.markdown(selected_system_prompt)
    st.markdown("---")

    # show the messages in the selected conversation
    for message in conversation_manager.get_conversation_messages(
        selected_conversation_id
    ):
        display_message(message)

    # only run if new user input
    if user_message_content := st.chat_input("What is your message?"):

        # we only need to initialize the client when we actually make a call,
        # we're doing slow synchronous calls so this is fine, since user
        # interacts in between each one
        #
        # note: defaults to getting ANTHROPIC_API_KEY from environment
        client = anthropic.Anthropic()

        user_message: anthropic.types.MessageParam = {
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
        messages = conversation_manager.get_conversation_messages(
            selected_conversation_id
        )

        # note: the full api is `create` and `stream`
        with st.spinner("Thinking..."):
            response: anthropic.types.Message = client.messages.create(
                messages=messages,
                max_tokens=Defaults.MAX_TOKENS,
                model=Defaults.MODEL.value,
                system=selected_system_prompt,
            )

        # parse message from response
        agent_message: anthropic.types.MessageParam = {
            "role": response.role,
            "content": response.content,
        }

        # add it to message history
        conversation_manager.add_conversation_message(
            selected_conversation_id,
            agent_message,
        )

        # display agent message
        display_message(agent_message)


if __name__ == "__main__":
    main()

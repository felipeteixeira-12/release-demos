import streamlit as st

def icon(emoji: str):
    """Shows an emoji as a Notion-style page icon."""
    st.write(
        f'<span style="font-size: 78px; line-height: 1">{emoji}</span>',
        unsafe_allow_html=True,
    )
    
st.set_page_config("Unit Testing Demo", "👩‍🔬", layout="wide")
icon("👩‍🔬")

st.title("Unit Testing Demo", anchor=False)
st.caption("A new API to write unit tests for Streamlit apps.")
st.write("Learn more about unit testing in [<PLACEHOLDER_OUR_DOCS>](https://docs.streamlit.io/).")
st.divider()

st.info("The GIF shows an OpenAI API-powered chatbot app, chatbot code, test code, and the tests passing after run.", icon="ℹ️")
st.image("1.28/pages/tests.gif")

tab1, tab2 = st.tabs(
    [
        "🧑‍💻 Main app code",
        "🧪 Test code",
    ]
)

with tab1:
    st.code(
        """
        import openai
        import streamlit as st

        with st.sidebar:
            openai_api_key = st.text_input(
                "OpenAI API Key", key="chatbot_api_key", type="password")
            st.session_state["openai_api_key"] = openai_api_key
            "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
            "[View the source code](https://github.com/streamlit/llm-examples/blob/main/Chatbot.py)"
            "[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/streamlit/llm-examples?quickstart=1)"

        st.title("💬 Chatbot")
        st.caption("🚀 A streamlit chatbot powered by OpenAI LLM")
        if "messages" not in st.session_state:
            st.session_state["messages"] = [
                {"role": "assistant", "content": "How can I help you?"}]

        for msg in st.session_state.messages:
            st.chat_message(msg["role"]).write(msg["content"])

        if prompt := st.chat_input():
            if not st.session_state["openai_api_key"]:
                st.info("Please add your OpenAI API key to continue.")
                st.stop()

            openai.api_key = st.session_state["openai_api_key"]
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.chat_message("user").write(prompt)
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", messages=st.session_state.messages
            )
            msg = response.choices[0].message
            st.session_state.messages.append(
                {"role": "assistant", "content": msg.content})
            st.chat_message("assistant").write(msg.content)
        """, language="python"
    )

with tab2:
    st.code(
        '''
        import unittest
        import openai
        from unittest.mock import patch
        from types import SimpleNamespace
        from streamlit.testing.v1 import AppTest


        class TestChatbotApp(unittest.TestCase):

            def test_smoke(self):
                """Test if the app runs without throwing an exception."""
                at = AppTest.from_file("app.py", default_timeout=10).run()
                assert not at.exception

            def test_sidebar(self):
                """Test if a single text input for the OpenAI API key exists in the sidebar."""
                at = AppTest.from_file("app.py").run()
                assert len(at.sidebar.text_input) == 1

            def test_session_state(self):
                """Test if the session state is initialized correctly."""
                at = AppTest.from_file("app.py").run()
                assert "messages" in at.session_state
                assert at.session_state["messages"][0]["role"] == "assistant"

            def test_messages_render(self):
                """Test if the initial assistant message is rendered."""
                at = AppTest.from_file("app.py").run()
                assert len(at.chat_message) == 1

            @patch("openai.ChatCompletion.create")
            def test_openai_api(self, mock_openai):
                """Test if the OpenAI API is correctly integrated and the chat updates."""
                mock_openai.return_value = SimpleNamespace(
                    choices=[SimpleNamespace(message=SimpleNamespace(
                        content='Sure, I can help!', role='assistant'))]
                )
                at = AppTest.from_file("app.py").run()
                at.text_input[0].set_value("test_api_key").run()
                assert at.session_state["openai_api_key"] == "test_api_key"
                at.chat_input[0].set_value("Hello").run()
                assert len(at.session_state["messages"]) == 3

            @patch("openai.ChatCompletion.create")
            def test_openai_401_error(self, mock_openai):
                """Test if the app correctly handles a 401 Authentication Error from OpenAI."""
                mock_openai.side_effect = openai.error.AuthenticationError(
                    "Invalid Authentication")
                at = AppTest.from_file("app.py").run()
                at.text_input[0].set_value("wrong_api_key").run()
                at.chat_input[0].set_value("Hello").run()
                if len(at.text_area) > 0:
                    assert "Invalid Authentication" in at.text_area[0].get_value()
                else:
                    print("text_area is empty! Something's wrong!")
        ''', language="python"
    )

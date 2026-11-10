"""Offline runtime check for the Streamlit interface (no API calls)."""
from pathlib import Path
import sys
from unittest.mock import patch
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from providers.base import ModelResponse, ToolCall

class FakeProvider:
    def complete(self, messages, tools=None, **kwargs):
        if messages[-1]["content"].startswith("TOOL_RESULTS_JSON:"):
            return ModelResponse(text="4 từ, 22 ký tự")
        return ModelResponse(tool_calls=[ToolCall("word_count", {"text": "AI tools help research"})])

def main():
    with patch("providers.make_provider", return_value=FakeProvider()), patch("chat.write_transcript") as saved:
        app = AppTest.from_file(str(ROOT / "app.py")).run(timeout=20)
        assert not app.exception, app.exception
        assert app.title[0].value == "🔎 Research Agent"
        app.chat_input[0].set_value("Đếm số từ trong đoạn: AI tools help research").run(timeout=20)
        assert not app.exception, app.exception
        assert len(app.session_state["history"]) == 2
        assert app.session_state["history"][-1]["content"] == "4 từ, 22 ký tự"
        assert saved.called
        print("PASS: UI renders, runs word_count, displays answer and saves transcript.")
    class SendingProvider:
        def complete(self, *args, **kwargs):
            return ModelResponse(tool_calls=[ToolCall("send", {"text": "test", "confirmed": True})])
    with patch("providers.make_provider", return_value=SendingProvider()), patch("chat.execute_tool_call") as execute:
        app = AppTest.from_file(str(ROOT / "app.py")).run(timeout=20)
        app.chat_input[0].set_value("Gửi test").run(timeout=20)
        assert not app.exception, app.exception
        assert len(app.error) == 1
        execute.assert_not_called()
        print("PASS: UI blocks a send call before tool execution.")

if __name__ == "__main__":
    main()


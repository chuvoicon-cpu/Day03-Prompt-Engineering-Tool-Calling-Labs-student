"""Run: streamlit run app.py"""
from pathlib import Path
import json
from datetime import datetime, timezone
import streamlit as st
from chat import run_model_tool_loop, write_transcript
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import build_artifact_version, artifact_version_dict

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title="Research Agent", page_icon="🔎")
st.title("🔎 Research Agent")
st.caption("Tìm nguồn, đọc tài liệu và đếm từ. Gửi Telegram được tắt trong UI.")
model = st.sidebar.selectbox("Model 9router", ["ag/gemini-3.8-flash-low", "ag/gemini-3.8-flash-high"])
if "history" not in st.session_state:
    st.session_state.history = []
    st.session_state.transcript = {"created_at": datetime.now(timezone.utc).isoformat(), "turns": []}
    st.session_state.transcript_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f")
for message in st.session_state.history:
    with st.chat_message(message["role"]):
        st.write(message["content"])
query = st.chat_input("Bạn muốn nghiên cứu gì?")
if query:
    prompt_path = ROOT / "artifacts/versions/v3/system_prompt.md"
    tools_path = ROOT / "artifacts/tools.yaml"
    # Restrict execution too: a model cannot bypass the action boundary by naming send.
    declarations = [item for item in load_tool_declarations(tools_path) if item["name"] != "send"]
    class ReadOnlyProvider:
        def complete(self, *args, **kwargs):
            response = make_provider("9router").complete(*args, **kwargs)
            if any(call.name == "send" for call in response.tool_calls):
                raise ValueError("Gửi Telegram được tắt trong UI.")
            return response
    with st.chat_message("user"):
        st.write(query)
    try:
        with st.spinner("Đang xử lý…"):
            result = run_model_tool_loop(
                provider=ReadOnlyProvider(),
                messages=[{"role": "system", "content": prompt_path.read_text(encoding="utf-8")},
                          *st.session_state.history[-10:], {"role": "user", "content": query}],
                tools=to_openai_tools(declarations), model=model, max_tool_rounds=4,
            )
        with st.chat_message("assistant"):
            st.write(result["assistant_text"])
            with st.expander("Tool calls và kết quả"):
                st.json(result["tool_events"])
        st.session_state.history.extend([{"role": "user", "content": query},
                                         {"role": "assistant", "content": result["assistant_text"]}])
        transcript = st.session_state.transcript
        transcript.update(artifact_version_dict(build_artifact_version("v3", prompt_path, tools_path)))
        transcript.update({"provider": "9router", "model": model, "disabled_tools": ["send"]})
        transcript["turns"].append({"user": query, **result})
        write_transcript(ROOT / "transcripts" / (st.session_state.transcript_id + ".ui.transcript.json"), transcript)
    except Exception as exc:
        st.error("Không hoàn tất request. Kiểm tra kết nối 9router và API key; xem log cục bộ.")
st.download_button("Tải transcript", json.dumps(st.session_state.get("transcript", {}), ensure_ascii=False, indent=2),
                   file_name="research-transcript.json", mime="application/json")


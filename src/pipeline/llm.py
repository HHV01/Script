"""Gọi LLM qua OpenCode Go (OpenAI-compatible) và đọc JSON trả về."""
import json
import os
import re
import uuid

from .common import load_env

# Endpoint OpenCode Go (OpenAI-compatible). Danh sách model: https://opencode.ai/inference/go/v1/models
GO_BASE_URL = "https://opencode.ai/inference/go/openai/v1"
# Session ID ổn định cho cả lần chạy (theo docs OpenCode Go, giúp tối ưu routing + prompt-cache).
_SESSION_ID = uuid.uuid4().hex


def _client():
    load_env()
    import openai  # import muộn để các bước không cần LLM vẫn chạy khi chưa cài
    key = os.environ.get("OPENCODE_API_KEY")
    if not key:
        raise SystemExit("Thiếu OPENCODE_API_KEY trong .env — lấy key tại https://opencode.ai/console (API keys)")
    return openai.OpenAI(
        base_url=GO_BASE_URL,
        api_key=key,
        default_headers={"x-opencode-session": _SESSION_ID},
    )


def complete(model, user, system="", max_tokens=16000):
    client = _client()
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": user})
    resp = client.chat.completions.create(
        model=model, messages=messages, max_tokens=max_tokens)
    return (resp.choices[0].message.content or "") if resp.choices else ""


def extract_json(text):
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.S)
    start = min([i for i in (text.find("["), text.find("{")) if i >= 0], default=-1)
    if start < 0:
        raise ValueError("LLM không trả về JSON:\n" + text[:200])
    need_end = "]" if text[start] == "[" else "}"
    end = text.rfind(need_end)
    if end <= start:
        raise ValueError("JSON thiếu dấu đóng:\n" + text[:200])
    return json.loads(text[start:end + 1])

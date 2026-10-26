"""Gọi LLM (Claude) và đọc JSON trả về."""
import json
import re

from .common import load_env


def complete(model, user, system="", max_tokens=16000):
    load_env()
    import anthropic  # import muộn để các bước không cần LLM vẫn chạy khi chưa cài
    client = anthropic.Anthropic()
    msg = client.messages.create(
        model=model, max_tokens=max_tokens, system=system,
        messages=[{"role": "user", "content": user}])
    return "".join(b.text for b in msg.content if b.type == "text")


def extract_json(text):
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.S)
    start = min([i for i in (text.find("["), text.find("{")) if i >= 0], default=-1)
    need_end = "]" if text[start] == "[" else "}"
    return json.loads(text[start: text.rfind(need_end) + 1])

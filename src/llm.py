"""OpenAI 兼容接口的大模型调用（DeepSeek / 通义千问 / 智谱 / Kimi / 硅基流动 / 本地 Ollama 都支持）。

通过环境变量配置：
  LLM_BASE_URL   例如 https://api.deepseek.com/v1  或  http://localhost:11434/v1 (Ollama)
  LLM_API_KEY    API Key（Ollama 随便填）
  LLM_MODEL      例如 deepseek-chat / qwen2.5-coder:7b
"""
from __future__ import annotations

import os
import re
import time

_client = None


def _load_dotenv() -> None:
    """自动读取项目根目录的 .env（若环境变量尚未设置）。"""
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    if not os.path.exists(env_path):
        return
    with open(env_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


_load_dotenv()


# 不走默认服务商的模型：模型名前缀 → (base_url 环境变量, api_key 环境变量)
PROVIDERS = {
    "u2-": ("UNISOUND_BASE_URL", "UNISOUND_API_KEY"),
    "minimax-": ("MINIMAX_BASE_URL", "MINIMAX_API_KEY"),
    "claude-": ("AMR_BASE_URL", "AMR_API_KEY"),
    "gpt-6": ("AMR_BASE_URL", "AMR_API_KEY"),
}
_other_clients: dict[str, object] = {}


def _new_client(base_env: str, key_env: str):
    from openai import OpenAI
    return OpenAI(
        base_url=os.environ.get(base_env, "https://api.deepseek.com/v1"),
        api_key=os.environ.get(key_env, "EMPTY"),
        timeout=float(os.environ.get("LLM_TIMEOUT", "240")),
        max_retries=0,  # 只用 chat() 自己的重试；SDK 默认再重试 2 次，会让一次卡住的调用耗时变成 15 倍超时
    )


def get_client(model: str | None = None):
    """按模型名前缀选服务商（见 PROVIDERS）；其余模型走 LLM_BASE_URL / LLM_API_KEY。"""
    global _client
    for prefix, (base_env, key_env) in PROVIDERS.items():
        if model and model.startswith(prefix):
            if prefix not in _other_clients:
                _other_clients[prefix] = _new_client(base_env, key_env)
            return _other_clients[prefix]
    if _client is None:
        _client = _new_client("LLM_BASE_URL", "LLM_API_KEY")
    return _client


def chat(messages: list[dict], model: str | None = None, temperature: float = 0.0,
         max_retries: int = 5) -> tuple[str, dict]:
    """返回 (回复文本, token 用量)。usage 中额外带上本次实际使用的 temperature，
    以及服务端返回的模型标识 served_model（响应中有 model 字段时）。"""
    model = model or os.environ.get("LLM_MODEL", "deepseek-chat")
    for attempt in range(max_retries):
        try:
            resp = get_client(model).chat.completions.create(
                model=model, messages=messages, temperature=temperature,
            )
            u = resp.usage
            usage = {"prompt_tokens": getattr(u, "prompt_tokens", 0) or 0,
                     "completion_tokens": getattr(u, "completion_tokens", 0) or 0,
                     "temperature": temperature}
            served = getattr(resp, "model", None)   # 服务端返回的模型标识（中转服务可能与请求的不同）
            if served:
                usage["served_model"] = served
            return resp.choices[0].message.content or "", usage
        except Exception as e:  # 限流/网络抖动时退避重试
            if "temperature" in str(e) and temperature != 1.0:
                print(f"[llm] {model} 拒绝 temperature={temperature}，回退到 1.0")
                temperature = 1.0
                if attempt < max_retries - 1:
                    continue
            if attempt == max_retries - 1:
                raise
            wait = 2 ** attempt
            print(f"[llm] {type(e).__name__}: {e}; retry in {wait}s")
            time.sleep(wait)
    raise RuntimeError("unreachable")


_CODE_RE = re.compile(r"```(?:cangjie|cj)?\s*\n(.*?)```", re.S | re.I)


def extract_code(text: str) -> str:
    """取回复中最后一个代码块；没有代码块就返回原文。"""
    blocks = _CODE_RE.findall(text)
    return (blocks[-1] if blocks else text).strip()


def strip_main(code: str) -> str:
    """去掉模型自己写的 main()，避免与测试代码中的 main 冲突（DUPLICATE_DEFINITION）。

    注意：这是一个可选的后处理，做消融实验时可以开关对比。
    """
    m = re.search(r"^\s*main\s*\([^)]*\)\s*(:\s*\w+\s*)?\{", code, re.M)
    if not m:
        return code
    depth, i = 0, m.end() - 1
    while i < len(code):
        if code[i] == "{":
            depth += 1
        elif code[i] == "}":
            depth -= 1
            if depth == 0:
                return (code[: m.start()] + code[i + 1:]).strip()
        i += 1
    return code

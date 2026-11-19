"""统一的模型单价与美元折算（论文全文的成本口径）。

口径：所有模型都取国内官方按量计费牌价（人民币，未命中缓存，在线推理常规档），按同一汇率折成美元。
实验实际在国内平台上运行（火山方舟 Coding Plan、云知声），因此以国内牌价为唯一价格来源。
- 分档计价的模型取实验请求所在档：Doubao-Seed-2.0-mini 取输入 ≤32K 档；DeepSeek 取高峰价（偏保守）。
- U2-Flash 取原价（官网另有限时折扣价 0.6 / 1.2 元）。
- 未计缓存命中折扣（偏高）；超时、中断而未写出 summary 的请求不计入（偏低）。
- 实验实际通过订阅调用，按此折算的是等价牌价成本，不是实际支出。
"""
from __future__ import annotations

FX_RATE = 6.67               # 人民币 / 美元
FX_DATE = "2026-11-17"
CNY_PRICE_DATE = "2026-11-19"

ARK = "火山方舟模型价格页（在线推理常规）"
# 模型 ID → (输入 元/百万 tokens, 输出 元/百万 tokens, 来源)
CNY_PRICES: dict[str, tuple[float, float, str]] = {
    "doubao-seed-2-0-mini-260428": (0.2, 2.0, ARK + "，输入长度 [0, 32K]"),
    "deepseek-v4-1-flash-261017": (2.0, 8.0, ARK + "，高峰时段"),
    "kimi-k3-1-pro-261024": (13.0, 68.0, ARK),
    "glm-5-3-flash-260828": (0.8, 2.8, ARK),
    "doubao-seed-2-1-lite-260915": (0.8, 2.7, ARK + "，输入长度 [0, 1024K]"),
    "u2-flash": (1.0, 2.0, "云知声 MaaS 模型价格页，原价"),
}
SOURCE_EN = {
    "doubao-seed-2-0-mini-260428": "Volcano Engine Ark list price, prompt length [0, 32K]",
    "deepseek-v4-1-flash-261017": "Volcano Engine Ark list price, peak hours",
    "kimi-k3-1-pro-261024": "Volcano Engine Ark list price",
    "glm-5-3-flash-260828": "Volcano Engine Ark list price",
    "doubao-seed-2-1-lite-260915": "Volcano Engine Ark list price, prompt length [0, 1024K]",
    "u2-flash": "Unisound MaaS list price (before promotional discount)",
}


def cny_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    a, b, _ = CNY_PRICES[model]
    return (prompt_tokens * a + completion_tokens * b) / 1e6


def usd_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    """按国内牌价折算的美元成本（未四舍五入）。model 为模型 ID（如 deepseek-v4-1-flash-261017）。"""
    return cny_cost(model, prompt_tokens, completion_tokens) / FX_RATE


def usd_prices(model: str) -> tuple[float, float]:
    """每百万 tokens 的美元单价（输入, 输出）。"""
    a, b, _ = CNY_PRICES[model]
    return a / FX_RATE, b / FX_RATE

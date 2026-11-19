"""全部实验的 token 消耗与美元成本核算（国际站官网标价），留档并供 check_numbers 核对。

用法：
  python src/token_cost.py            # 输出 results/stats/token_cost_stats.{md,json}

口径：
- 美元按各厂商国际站官网按量计费标价（见 USD_PRICES，查价日期 USD_PRICE_DATE），DeepSeek 取高峰价（偏保守）；
- 人民币列仅供参考，按 extra_stats.PRICES 的国内火山方舟牌价（与图 2、成本表同一口径），两者之间不做汇率换算；
- 未计缓存命中折扣（偏高）；超时、中断而未写出 summary 的请求未计入（偏低）；
- 实验实际通过 Coding Plan 订阅调用，以上均为等价折算，不是实际支出。
"""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extra_stats import PRICE_DATE, PRICES  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "stats")

# 美元 / 百万 tokens：(输入, 输出, 来源)，均为未命中缓存的按量计费标价。
USD_PRICE_DATE = "2026-11-19"
USD_PRICES = {
    "doubao-seed-2-0-mini-260428": (0.10, 0.40, "BytePlus ModelArk model pricing page, Standard tier, prompt length [0, 128K]"),
    "deepseek-v4-1-flash-261017": (0.30, 1.20, "DeepSeek API docs, Models & Pricing, peak rate (off-peak is half)"),
    "kimi-k3-1-pro-261024": (2.00, 10.00, "Kimi API platform pricing for kimi-k3.1-pro"),
    "glm-5-3-flash-260828": (0.15, 0.50, "BytePlus ModelArk model pricing page, Standard tier (one trial run only)"),
}
RMB_KEY = {"doubao-seed-2-0-mini-260428": "doubao", "deepseek-v4-1-flash-261017": "ds_v41f",
           "kimi-k3-1-pro-261024": "kimik31p"}          # GLM 不在国内牌价表中，人民币列不计
SHORT = {"doubao-seed-2-0-mini-260428": "Doubao", "deepseek-v4-1-flash-261017": "DeepSeek",
         "kimi-k3-1-pro-261024": "Kimi", "glm-5-3-flash-260828": "GLM"}
CATEGORIES = [("stage3", "第 3 阶段正式实验"), ("original30", "Original-30 正式实验"),
              ("rounds10", "10 轮扩展"), ("pilot", "预实验（pilot）"), ("early", "早期探索（exp / ablation / try）")]
FORMAL = ("stage3", "original30", "rounds10")


def category(rel_dir: str) -> str:
    """按 results/ 下的相对目录归类。"""
    d = rel_dir.replace(os.sep, "/")
    if "/pilot" in d:
        return "pilot"
    for c in FORMAL:
        if d.startswith(f"results/{c}"):
            return c
    return "early"


def load_usage(root: str = ROOT) -> list[dict]:
    """每个有 token 记录的 summary 一行；跳过自测与无 token 的记录（如只重新评测的 reeval）。"""
    rows = []
    for p in sorted(glob.glob(os.path.join(root, "results", "**", "*.summary.json"), recursive=True)):
        if "selftest" in p:
            continue
        with open(p, encoding="utf-8") as f:
            s = json.load(f)
        pin, pout = s.get("total_prompt_tokens") or 0, s.get("total_completion_tokens") or 0
        if pin + pout == 0:
            continue
        model = s.get("model_resolved") or s.get("config", {}).get("model")
        if model not in USD_PRICES:
            raise SystemExit(f"{p}：模型 {model} 没有美元单价，请先补进 USD_PRICES")
        rows.append({"path": os.path.relpath(p, root).replace(os.sep, "/"), "model": model,
                     "category": category(os.path.relpath(os.path.dirname(p), root)),
                     "prompt_tokens": pin, "completion_tokens": pout})
    return rows


def usd_cost(model: str, pin: int, pout: int) -> float:
    a, b, _ = USD_PRICES[model]
    return (pin * a + pout * b) / 1e6


def rmb_cost(model: str, pin: int, pout: int) -> float:
    """国内方舟牌价；多档时取最高档（DeepSeek 高峰价），与成本表一致。不在牌价表中的模型记 0。"""
    key = RMB_KEY.get(model)
    if key is None:
        return 0.0
    a, b = max(PRICES[key].values())
    return (pin * a + pout * b) / 1e6


def _line(cat: str, model: str, items: list[dict]) -> dict:
    return {"category": cat, "model": model, "runs": len(items),
            "prompt_tokens": sum(r["prompt_tokens"] for r in items),
            "completion_tokens": sum(r["completion_tokens"] for r in items),
            "usd": round(sum(usd_cost(r["model"], r["prompt_tokens"], r["completion_tokens"]) for r in items), 2),
            "rmb": round(sum(rmb_cost(r["model"], r["prompt_tokens"], r["completion_tokens"]) for r in items), 2)}


def aggregate(rows: list[dict]) -> list[dict]:
    """按 类别 × 模型、类别小计、正式实验小计、各模型合计、总计 汇总（先求和再四舍五入）。"""
    out = []
    for c, _ in CATEGORIES:
        items = [r for r in rows if r["category"] == c]
        if not items:
            continue
        out += [_line(c, m, [r for r in items if r["model"] == m])
                for m in USD_PRICES if any(r["model"] == m for r in items)]
        out.append(_line(c, "all", items))
    out.append(_line("formal", "all", [r for r in rows if r["category"] in FORMAL]))
    out += [_line("total", m, [r for r in rows if r["model"] == m])
            for m in USD_PRICES if any(r["model"] == m for r in rows)]
    out.append(_line("total", "all", rows))
    return out


def write_markdown(lines: list[dict], path: str) -> None:
    names = dict(CATEGORIES, formal="**正式实验小计**", total="**合计**")
    md = ["# Token 消耗与美元成本核算", "",
          f"美元按各厂商国际站官网按量计费标价（查价 {USD_PRICE_DATE}），DeepSeek 取高峰价；"
          f"人民币列为国内火山方舟牌价（{PRICE_DATE}，与图 2、成本表同一口径），仅供参考，GLM 无国内牌价未计入人民币列。",
          "**两列来自不同价目表，不能用汇率互相换算**（例如 Doubao 输出单价国内 ¥2.0 / 百万 tokens，国际 $0.40）。"
          "论文中写明：美元按国际站官网标价，图 2 与成本表的人民币按国内方舟牌价。",
          "未计缓存命中折扣（偏高）；超时、中断而未写出 summary 的请求未计入（偏低）；"
          "实验实际通过 Coding Plan 订阅调用，均为等价折算，不是实际支出。", "",
          "## 美元单价（每百万 tokens）", "", "| 模型 | 输入 | 输出 | 来源 |", "|---|---:|---:|---|"]
    md += [f"| {SHORT[m]} `{m}` | ${a:.2f} | ${b:.2f} | {src} |" for m, (a, b, src) in USD_PRICES.items()]
    md += ["", "## 按实验与模型汇总", "",
           "| 类别 | 模型 | 运行数 | 输入 tokens | 输出 tokens | 美元 | 人民币（参考） |",
           "|---|---|---:|---:|---:|---:|---:|"]
    for r in lines:
        model = SHORT.get(r["model"], "小计" if r["category"] not in ("formal", "total") else "全部")
        md.append(f"| {names[r['category']]} | {model} | {r['runs']} | {r['prompt_tokens']:,} | "
                  f"{r['completion_tokens']:,} | ${r['usd']:,.2f} | ¥{r['rmb']:,.2f} |")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")


def main():
    lines = aggregate(load_usage())
    os.makedirs(OUT, exist_ok=True)
    res = {"usd_price_date": USD_PRICE_DATE, "rmb_price_date": PRICE_DATE,
           "usd_prices": {m: {"input": a, "output": b, "source": s} for m, (a, b, s) in USD_PRICES.items()},
           "token_cost": lines}
    with open(os.path.join(OUT, "token_cost_stats.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)
    write_markdown(lines, os.path.join(OUT, "token_cost_stats.md"))
    for r in lines:
        if r["model"] == "all" and r["category"] in ("formal", "total"):
            print(f"{r['category']}: ${r['usd']:,.2f}（人民币参考 ¥{r['rmb']:,.2f}）")


if __name__ == "__main__":
    main()

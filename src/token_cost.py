"""全部实验的 token 消耗与美元成本核算，留档并供 check_numbers 核对。

用法：
  python src/token_cost.py            # 输出 results/stats/token_cost_stats.{md,json}

口径（与论文全文、图 2、成本表相同，见 pricing.py）：
- 所有模型取国内官方按量计费牌价（人民币），按统一汇率折成美元；DeepSeek 取高峰价（偏保守）；
- 未计缓存命中折扣（偏高）；超时、中断而未写出 summary 的请求未计入（偏低）；检索评估中的改写与判定调用不写 summary，也未计入；
- 实验实际通过订阅调用，以上均为等价折算，不是实际支出。
"""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pricing import CNY_PRICE_DATE, CNY_PRICES, FX_DATE, FX_RATE, SOURCE_EN, cny_cost, usd_cost, usd_prices  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "stats")

SHORT = {"doubao-seed-2-0-mini-260428": "Doubao", "deepseek-v4-1-flash-261017": "DeepSeek",
         "kimi-k3-1-pro-261024": "Kimi", "glm-5-3-flash-260828": "GLM-5.3-Flash",
         "doubao-seed-2-1-lite-260915": "Doubao-2.1-lite", "u2-flash": "U2-Flash"}
CATEGORIES = [("stage3", "第 3 阶段正式实验"), ("original30", "Original-30 正式实验"),
              ("rounds10", "10 轮扩展"), ("review", "审稿后补充实验"), ("pilot", "预实验（pilot）"),
              ("early", "早期探索（exp / ablation / try）")]
FORMAL = ("stage3", "original30", "rounds10", "review")


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
        if model not in CNY_PRICES:
            raise SystemExit(f"{p}：模型 {model} 没有单价，请先补进 pricing.CNY_PRICES")
        rel, cat = os.path.relpath(p, root).replace(os.sep, "/"), category(os.path.relpath(os.path.dirname(p), root))
        rows.append({"path": rel, "model": model, "category": cat, "prompt_tokens": pin, "completion_tokens": pout})
        rw_in, rw_out = s.get("total_rewrite_prompt_tokens") or 0, s.get("total_rewrite_completion_tokens") or 0
        if rw_in + rw_out:            # rag2 的查询改写由固定的改写模型完成，按改写模型单价另计一行
            rows.append({"path": rel + "#rewrite", "model": s["rewrite_model"], "category": cat,
                         "prompt_tokens": rw_in, "completion_tokens": rw_out})
    return rows


def _line(cat: str, model: str, items: list[dict]) -> dict:
    def total(fn):
        return round(sum(fn(r["model"], r["prompt_tokens"], r["completion_tokens"]) for r in items), 2)
    return {"category": cat, "model": model, "runs": len(items),
            "prompt_tokens": sum(r["prompt_tokens"] for r in items),
            "completion_tokens": sum(r["completion_tokens"] for r in items),
            "usd": total(usd_cost), "cny": total(cny_cost)}


def aggregate(rows: list[dict]) -> list[dict]:
    """按 类别 × 模型、类别小计、正式实验小计、各模型合计、总计 汇总（先求和再四舍五入）。"""
    out = []
    for c, _ in CATEGORIES:
        items = [r for r in rows if r["category"] == c]
        if not items:
            continue
        out += [_line(c, m, [r for r in items if r["model"] == m])
                for m in CNY_PRICES if any(r["model"] == m for r in items)]
        out.append(_line(c, "all", items))
    out.append(_line("formal", "all", [r for r in rows if r["category"] in FORMAL]))
    out += [_line("total", m, [r for r in rows if r["model"] == m])
            for m in CNY_PRICES if any(r["model"] == m for r in rows)]
    out.append(_line("total", "all", rows))
    return out


def write_markdown(lines: list[dict], path: str) -> None:
    names = dict(CATEGORIES, formal="**正式实验小计**", total="**合计**")
    md = ["# Token 消耗与美元成本核算", "",
          f"所有模型取国内官方按量计费牌价（{CNY_PRICE_DATE}，DeepSeek 取高峰价），按 {FX_RATE} 元/美元（{FX_DATE}）"
          "折成美元；与论文正文、图 2、成本表同一口径（见 pricing.py）。",
          "未计缓存命中折扣（偏高）；超时、中断而未写出 summary 的请求未计入（偏低）；"
          "实验实际通过订阅调用，均为等价折算，不是实际支出。", "",
          "## 单价（每百万 tokens）", "", "| 模型 | 输入（元） | 输出（元） | 输入（美元） | 输出（美元） | 来源 |",
          "|---|---:|---:|---:|---:|---|"]
    for m, (a, b, src) in CNY_PRICES.items():
        ua, ub = usd_prices(m)
        md.append(f"| {SHORT[m]} `{m}` | ¥{a:.2f} | ¥{b:.2f} | ${ua:.4f} | ${ub:.4f} | {src} |")
    md += ["", "## 按实验与模型汇总", "",
           "| 类别 | 模型 | 运行数 | 输入 tokens | 输出 tokens | 美元 | 人民币 |", "|---|---|---:|---:|---:|---:|---:|"]
    for r in lines:
        model = SHORT.get(r["model"], "小计" if r["category"] not in ("formal", "total") else "全部")
        md.append(f"| {names[r['category']]} | {model} | {r['runs']} | {r['prompt_tokens']:,} | "
                  f"{r['completion_tokens']:,} | ${r['usd']:,.2f} | ¥{r['cny']:,.2f} |")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")


def main():
    lines = aggregate(load_usage())
    os.makedirs(OUT, exist_ok=True)
    prices = {}
    for m, (a, b, _) in CNY_PRICES.items():
        ua, ub = usd_prices(m)
        prices[m] = {"input": ua, "output": ub, "cny_input": a, "cny_output": b, "source": SOURCE_EN[m]}
    res = {"cny_price_date": CNY_PRICE_DATE, "fx_rate": FX_RATE, "fx_date": FX_DATE, "usd_prices": prices,
           "token_cost": lines}
    with open(os.path.join(OUT, "token_cost_stats.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)
    write_markdown(lines, os.path.join(OUT, "token_cost_stats.md"))
    for r in lines:
        if r["model"] == "all" and r["category"] in ("formal", "total"):
            print(f"{r['category']}: ${r['usd']:,.2f}（¥{r['cny']:,.2f}）")


if __name__ == "__main__":
    main()

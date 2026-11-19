"""Generate the English Supporting Information (Tables S1–S15) and pack supporting_information.zip.

Usage:
  python src/make_supporting_info.py      # → results/supporting_information/{supporting_information,README}.md
                                          #   and supporting_information.zip in the repository root

All numbers are read from results/stats/*.json and hard_problem_coding.csv (no new analysis), so the
generated tables can be checked with check_numbers.py.
"""
import csv
import json
import os
import sys
import zipfile
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extra_stats import fmt_p  # noqa: E402
from pricing import CNY_PRICE_DATE, FX_DATE, FX_RATE  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATS = os.path.join(ROOT, "results", "stats")
OUT = os.path.join(ROOT, "results", "supporting_information")
ZIP = os.path.join(ROOT, "supporting_information.zip")
DATA_FILES = ["stage3_stats.json", "original30_stats.json", "rounds10_stats.json", "residual_failures.json",
              "hard_problem_coding.csv", "token_cost_stats.json"]

MODEL = {"doubao_mini": "Doubao-Seed-2.0-mini", "ds_v41f": "DeepSeek-V4.1-Flash", "kimik31p": "Kimi-K3.1-Pro",
         "doubao-seed-2-0-mini-260428": "Doubao-Seed-2.0-mini", "deepseek-v4-1-flash-261017": "DeepSeek-V4.1-Flash",
         "kimi-k3-1-pro-261024": "Kimi-K3.1-Pro", "glm-5-3-flash-260828": "GLM-5.3-Flash",
         "doubao-seed-2-1-lite-260915": "Doubao-Seed-2.1-lite", "u2-flash": "U2-Flash",
         "glm53f": "GLM-5.3-Flash", "doubao21l": "Doubao-Seed-2.1-lite", "u2f": "U2-Flash"}
DATASET = {"he": "HumanEval-Cangjie", "ce": "ClassEval-Cangjie", "or": "Original-30"}
CATEGORY = {"规格歧义": "specification ambiguity", "题意理解": "misread explicit specification",
            "仓颉语义": "Cangjie-specific semantic trap", "基准缺陷": "benchmark defect"}
SUBTYPE = {"功能行为未说明": "unspecified functional behaviour", "边界或非法输入约定": "boundary or invalid-input convention",
           "翻译约定": "translation convention", "跨方法状态依赖": "cross-method state dependency",
           "整数溢出": "integer overflow", "测试不可执行": "non-executable test",
           "题面与参考实现矛盾": "statement contradicts reference solution"}
COST_GROUP = {"stage3": "Stage 3 (main experiment)", "original30": "Original-30", "rounds10": "10-round extension",
              "pilot": "Pilot runs", "early": "Early exploration", "formal": "**Reported experiments, subtotal**",
              "total": "**All runs**", "review": "Supplementary experiments"}

COST_NOTE = (f"Costs are in USD: the vendors' official domestic pay-as-you-go list prices in CNY ({CNY_PRICE_DATE}; "
             f"DeepSeek at the peak rate, no cache discounts) converted at {FX_RATE} CNY per USD ({FX_DATE}). The "
             "experiments ran under a subscription plan, so these are equivalent list-price costs, not actual spending.")

LEGEND = ("Feedback arms: `blind` = told only that the program failed; `raw` = raw compiler / test output; "
          "`hint` = raw output plus rule-based repair hints; `rag` = raw output plus documentation snippets retrieved "
          "with the error text (BM25); suffix `_co` = compile-only feedback (tests are not run during repair). "
          "Initial prompts: `direct` = task only; `syntax` = task plus a Cangjie syntax reference. "
          "R0 = pass rate of the shared initial generation; R5 / R10 = pass rate after at most 5 / 10 repair rounds. "
          "Pass rates are percentages.")


def _load(name: str) -> dict:
    with open(os.path.join(STATS, name), encoding="utf-8") as f:
        return json.load(f)


def load_coding(path: str = os.path.join(STATS, "hard_problem_coding.csv")) -> dict[str, dict]:
    with open(path, encoding="utf-8-sig", newline="") as f:
        return {r["id"]: r for r in csv.DictReader(f)}


def coding_en(kinds: list[str], c: dict | None) -> tuple[str, str]:
    """English (category, subtype) for one hard problem; pure API timeouts have no code to code."""
    if kinds == ["api_timeout"]:
        return "timeout", "API timeout, no code produced"
    if c is None:
        return "", ""
    return CATEGORY[c["category"]], SUBTYPE[c["subtype"]]


def _cmp_label(c: dict) -> str:
    return f"{MODEL[c['model']]} | {DATASET[c['ds']]} | {c['prompt']} | {c['a']} vs {c['b']}"


def summary_table(rows: list[dict]) -> list[str]:
    L = ["| Model | Benchmark | Prompt | Feedback | Reps | R0 | R5 mean ± SD | Mean pass rate per round (R0→R5) | "
         "USD per pass (repair only) | USD per solved problem (incl. R0) |", "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {MODEL[r['model']]} | {DATASET[r['ds']]} | {r['prompt']} | {r['feedback']} | {r['reps']} | "
                 f"{r['r0']:.2f} | {r['r5_mean']:.2f} ± {r['r5_sd']:.2f} | "
                 f"{' → '.join(f'{x:.1f}' for x in r['curve_mean'])} | {r['usd_per_pass']:.4f} | "
                 f"{r['usd_per_solve_with_r0']:.4f} |")
    return L


def comparison_table(comps: list[dict]) -> list[str]:
    L = ["| Model | Benchmark | Prompt | A vs B | Problems | Discordant | Diff. [95% CI] | p | p (Holm) | "
         "McNemar p per repetition |", "|---|---|---|---|---|---|---|---|---|---|"]
    for c in comps:
        L.append(f"| {_cmp_label(c)} | {c['n']} | {c['n_discordant']} | {c['diff']:+.2f} [{c['ci_lo']:+.2f}, "
                 f"{c['ci_hi']:+.2f}] | {fmt_p(c['p'])} | {fmt_p(c['p_holm'])} | "
                 f"{', '.join(fmt_p(x) for x in c['mcnemar_per_rep'])} |")
    return L


def holm_table(comps: list[dict], variants: list[dict]) -> list[str]:
    L = ["| Model | Benchmark | Prompt | A vs B | p (Holm, main family) | Variant A: informative comparisons only | "
         "Variant B: per comparison type |", "|---|---|---|---|---|---|---|"]
    for c, v in zip(comps, variants):
        a = "excluded (no discordant problem)" if v["p_holm_informative"] is None else fmt_p(v["p_holm_informative"])
        L.append(f"| {_cmp_label(c)} | {fmt_p(c['p_holm'])} | {a} | {fmt_p(v['p_holm_by_type'])} |")
    return L


def matrix_section(s: dict, first: int, title: str, n_problems: str) -> list[str]:
    n = len(s["comparisons"])
    return [f"## Table S{first}. {title}: pass rates and cost per configuration", "",
            f"{n_problems} {COST_NOTE}", "",
            *summary_table(s["summary"]), "",
            f"## Table S{first + 1}. {title}: all {n} pairwise comparisons", "",
            "Difference = A − B in percentage points, computed on per-problem means over repetitions; 95% CI from a "
            f"per-problem bootstrap; p from a per-problem sign-flip permutation test; p (Holm) is corrected over all {n} "
            "comparisons in this table (the pre-specified family). McNemar p values per repetition are uncorrected "
            "and given for robustness only.", "", *comparison_table(s["comparisons"]), "",
            f"## Table S{first + 2}. {title}: sensitivity analysis excluding unstable and timed-out problems", "",
            "Same comparisons after removing problems whose reference solution is judged inconsistently across "
            "repeated runs, and problems on which either arm hit an API timeout.", "",
            *comparison_table(s["sensitivity_excl_flaky"]), "",
            f"## Table S{first + 3}. {title}: alternative Holm families (post hoc, not the main analysis)", "",
            "Variant A drops comparisons with no discordant problem (they cannot reach significance); variant B "
            "corrects separately within each comparison type (hint vs raw, rag vs raw, rag vs hint, raw vs blind; "
            "`_co` arms merged into their type).", "", *holm_table(s["comparisons"], s["holm_variants"]), ""]


def rounds10_section(s: dict) -> list[str]:
    L = ["## Table S9. 10-round extension: pass rate per round", "",
         "Doubao-Seed-2.0-mini, HumanEval-Cangjie, `direct` prompt, starting from the Stage 3 shared R0, at most 10 "
         "repair rounds, temperature 0.3, 3 repetitions per arm. Runs were re-sampled, so rounds 1–5 differ from "
         "Table S1.", "",
         "| Feedback | Reps | R0 | R5 mean ± SD | R10 mean ± SD | Mean pass rate per round (R0→R10) | Gain per round |",
         "|---|---|---|---|---|---|---|"]
    for r in s["feedback"]:
        L.append(f"| {r['feedback']} | {r['reps']} | {r['r0']:.2f} | {r['r5_mean']:.2f} ± {r['r5_sd']:.2f} | "
                 f"{r['r10_mean']:.2f} ± {r['r10_sd']:.2f} | {' → '.join(f'{x:.1f}' for x in r['curve_mean'])} | "
                 f"{', '.join(f'{g:+.2f}' for g in r['gains'])} |")
    L += ["", "## Table S10. 10-round extension: comparisons at round 10", "",
          f"Method as in Table S2; p (Holm) is corrected over the {len(s['comparisons_r10'])} comparisons in this table.",
          "", *comparison_table(s["comparisons_r10"]), ""]
    return L


def hard_problem_tables(hard: dict, coding: dict[str, dict]) -> list[str]:
    L = ["## Table S12. Fixed hard problems and their coding", "",
         "Problems that failed in every repetition of raw, hint and rag (`direct` prompt). Repair feedback names "
         "the failing test functions only; it does not show assertions or expected values. Coding was drafted by "
         "one author with AI assistance and independently reviewed and revised by another author. When a problem "
         "is on both lists, the coding follows the DeepSeek failure; Kimi-only failures are coded from Kimi's "
         "trajectory (for problem 67, Kimi fails earlier with the compile error `undeclared type name 'Dish'`).", ""]
    for model, rows in hard.items():
        labels = [coding_en(h["kinds"], coding.get(h["id"])) for h in rows]
        counts = Counter(a if a == "timeout" else f"{a}: {b}" for a, b in labels)
        L += [f"### {MODEL[model]} ({len(rows)} problems)", "",
              "Counts: " + "; ".join(f"{k} {v}" for k, v in counts.most_common()), "",
              "| ID | Class | Final failure kinds | Tests passed (first non-timeout record) | Category | Subtype |",
              "|---|---|---|---|---|---|"]
        for h, (cat, sub) in zip(rows, labels):
            st = "".join("✓" if x else "✗" for x in h["status"]) if isinstance(h["status"], list) else h["status"]
            L.append(f"| {h['id']} | {h['class']} | {', '.join(h['kinds'])} | {st} | {cat} | {sub} |")
        L.append("")
    L += ["## Table S13. Evidence for each coded problem", "", "| ID | Class | Category | Subtype | Evidence |",
          "|---|---|---|---|---|"]
    for i, c in sorted(coding.items(), key=lambda kv: int(kv[0])):
        L.append(f"| {i} | {c['class']} | {CATEGORY[c['category']]} | {SUBTYPE[c['subtype']]} | "
                 f"{c['evidence_en'].replace('|', '/')} |")
    return L + [""]


def residual_section(r: dict, coding: dict[str, dict]) -> list[str]:
    L = ["## Table S11. ClassEval-Cangjie: problem-runs still failing after 5 repair rounds", "",
         "A problem-run is one problem in one repetition. Near miss = exactly one test still failing. "
         "Always failing = failed in every repetition of that arm.", "",
         "| Model | Prompt | Feedback | Reps | Failing problem-runs | Test failures | Near misses | API timeouts | "
         "Compile / other | Always-failing problems |", "|---|---|---|---|---|---|---|---|---|---|"]
    for t in r["residual"]:
        c = t["cats"]
        other = t["fail"] - c.get("test_failure", 0) - c.get("api_timeout", 0)
        near = f"{t['near_miss']} ({100 * t['near_miss'] / t['test_fail']:.0f}%)" if t["test_fail"] else "0"
        L.append(f"| {MODEL[t['model']]} | {t['prompt']} | {t['feedback']} | {t['reps']} | {t['fail']} | "
                 f"{c.get('test_failure', 0)} | {near} | {c.get('api_timeout', 0)} | {other} | {len(t['always'])} |")
    L += ["", *hard_problem_tables(r["hard_problems"], coding),
          "## Table S14. Feedback truncation check", "",
          "Feedback shown to the model (all rounds except the last) is stored truncated to 1500 characters; the model "
          "itself saw up to 3000 characters. Stored feedback shorter than 1500 characters cannot have been truncated; "
          "feedback stored at 1500 characters was re-executed to recover its full length. Error lines are lines "
          "starting with `error:`; kept = the line starts within the first 3000 characters. cjc output varies slightly "
          "between runs, so re-executed counts may differ by about one.", "",
          "| Model | Failure kind | Below 1500 (not truncated) | At 1500 (re-executed) | Over 3000 | Error lines kept / "
          "total | Lost all error lines | Full length median / p90 / max |", "|---|---|---|---|---|---|---|---|"]
    rc = r.get("recheck") or {}
    for key in sorted(r["truncation_census"]):
        model, kind = key.split(" ", 1)
        c, x = r["truncation_census"][key], rc.get(key)
        tail = (f"{x['over_cap']} | {x['error_lines_kept']} / {x['error_lines_total']} | {x['lost_all_errors']} | "
                f"{x['length_median']:.0f} / {x['length_p90']} / {x['length_max']}") if x else "— | — | — | —"
        L.append(f"| {MODEL[model]} | {kind} | {c.get('short', 0)} | {c.get('at_cap', 0)} | {tail} |")
    return L + [""]


def cost_section(t: dict) -> list[str]:
    L = ["## Table S15. Token usage and cost in USD", "",
         f"{COST_NOTE} Requests that timed out or were interrupted before a summary was written are not included.", "",
         "| Model | Input (CNY per 1M tokens) | Output (CNY per 1M tokens) | Input (USD) | Output (USD) | Source |",
         "|---|---|---|---|---|---|"]
    L += [f"| {MODEL[m]} | {p['cny_input']:.2f} | {p['cny_output']:.2f} | ${p['input']:.4f} | ${p['output']:.4f} | "
          f"{p['source']} |" for m, p in t["usd_prices"].items()]
    L += ["", "| Group | Model | Runs | Input tokens | Output tokens | USD |", "|---|---|---|---|---|---|"]
    for r in t["token_cost"]:
        L.append(f"| {COST_GROUP[r['category']]} | {MODEL.get(r['model'], 'all')} | {r['runs']} | "
                 f"{r['prompt_tokens']:,} | {r['completion_tokens']:,} | ${r['usd']:,.2f} |")
    return L + [""]


def build_document() -> str:
    coding = load_coding()
    L = ["# Supporting Information", "",
         "This document collects the complete statistical tables behind the paper. Every number is generated by "
         "`src/make_supporting_info.py` from the machine-readable files shipped alongside it (see README.md).", "",
         LEGEND, ""]
    L += matrix_section(_load("stage3_stats.json"), 1, "Stage 3",
                        "HumanEval-Cangjie (164 problems) and ClassEval-Cangjie (84 problems).")
    L += matrix_section(_load("original30_stats.json"), 5, "Original-30",
                        "Original-30: 30 new hand-written function-level problems (contamination control).")
    L += rounds10_section(_load("rounds10_stats.json"))
    L += residual_section(_load("residual_failures.json"), coding)
    L += cost_section(_load("token_cost_stats.json"))
    return "\n".join(L)


README = """# Supporting Information: file index

| File | Content | Tables |
|---|---|---|
| `supporting_information.md` | All supporting tables in readable form | S1–S15 |
| `data/stage3_stats.json` | Stage 3: per-configuration results (`summary`), all 33 comparisons (`comparisons`), sensitivity analysis (`sensitivity_excl_flaky`), alternative Holm families (`holm_variants`) | S1–S4 |
| `data/original30_stats.json` | Same layout for Original-30 (17 comparisons) | S5–S8 |
| `data/rounds10_stats.json` | 10-round extension: per-arm curves and gains (`feedback`), round-10 comparisons (`comparisons_r10`) | S9–S10 |
| `data/residual_failures.json` | Residual failures (`residual`), fixed hard problems (`hard_problems`), truncation census (`truncation_census`) and re-execution results (`recheck`) | S11, S12, S14 |
| `data/hard_problem_coding.csv` | Coding of the fixed hard problems; `evidence` (Chinese, original) and `evidence_en` (English) | S12–S13 |
| `data/token_cost_stats.json` | Token usage and USD cost per group and model (`token_cost`), unit prices and sources (`usd_prices`) | S15 |

Key fields: pass rates (`r0`, `r5_mean`, `r5_sd`, `r10_mean`, `curve_mean`) are percentages; `diff`, `ci_lo`,
`ci_hi` are percentage points (A − B); `p` is the sign-flip permutation p value and `p_holm` its Holm-adjusted
value; `usd*` fields are USD (domestic CNY list prices converted at one exchange rate, see Table S15).
Model keys: `doubao_mini` = Doubao-Seed-2.0-mini, `ds_v41f` = DeepSeek-V4.1-Flash, `kimik31p` = Kimi-K3.1-Pro;
dataset keys: `he` = HumanEval-Cangjie, `ce` = ClassEval-Cangjie, `or` = Original-30.
The full replication package (code, raw model outputs and logs) is archived separately.
"""


def main():
    os.makedirs(OUT, exist_ok=True)
    doc, readme = os.path.join(OUT, "supporting_information.md"), os.path.join(OUT, "README.md")
    with open(doc, "w", encoding="utf-8") as f:
        f.write(build_document())
    with open(readme, "w", encoding="utf-8") as f:
        f.write(README)
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(readme, "supporting_information/README.md")
        z.write(doc, "supporting_information/supporting_information.md")
        for name in DATA_FILES:
            z.write(os.path.join(STATS, name), f"supporting_information/data/{name}")
    print(f"→ {doc}\n→ {ZIP}")


if __name__ == "__main__":
    main()

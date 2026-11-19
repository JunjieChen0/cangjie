# Supporting Information: file index

| File | Content | Tables |
|---|---|---|
| `supporting_information.md` | All supporting tables in readable form | S1–S16 |
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

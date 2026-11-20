import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
import classifier_check as C  # noqa: E402


def test_sample_is_stratified_and_seeded():
    pool = [{"predicted": c, "feedback": f"{c}{i}"} for c in C.CATEGORIES[:3] for i in range(20)]
    a, b = C.sample(pool, per_class=5), C.sample(pool, per_class=5)
    assert a == b and len(a) == 15
    assert {c: sum(x["predicted"] == c for x in a) for c in C.CATEGORIES[:3]} == {c: 5 for c in C.CATEGORIES[:3]}


def test_agreement_precision_recall_and_kappa():
    pred = ["foreign_syntax", "foreign_syntax", "api_or_undeclared", "api_or_undeclared"]
    human = ["foreign_syntax", "other_compile", "api_or_undeclared", "api_or_undeclared"]
    r = C.agreement(human, pred)
    assert r["exact"] == 3
    assert r["per_class"]["foreign_syntax"]["precision"] == 0.5 and r["per_class"]["api_or_undeclared"]["recall"] == 1.0
    assert r["confusion"] == {"foreign_syntax → other_compile": 1}
    # po = 0.75，pe = (1*2 + 2*2) / 16 = 0.375 → κ = 0.6
    assert abs(r["kappa"] - 0.6) < 1e-9
    # 总体中 foreign 30 条（精确率 0.5）、api 10 条（精确率 1.0）→ 0.75*0.5 + 0.25*1.0 = 0.625
    assert abs(C.weighted_accuracy(r["per_class"], {"foreign_syntax": 30, "api_or_undeclared": 10}) - 0.625) < 1e-9

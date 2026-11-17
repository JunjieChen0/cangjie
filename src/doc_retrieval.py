"""用编译报错文本从仓颉官方文档（CangjieDocCorpus）中检索相关片段，供 rag 反馈模式使用。

- 语料：external/CangjieBench/CangjieDocCorpus 下全部 .md（标准库 API 文档 + 语言手册）
- 切块：按 #/##/### 标题切分，每块保留标题路径
- 检索：BM25（k1=1.5, b=0.75），本地实现，无外部依赖、结果确定
- 分词：代码标识符（小写，驼峰额外拆分）+ 中文单字
- 超参数在看到实验结果前固定：TOP_K = 3，片段总长 MAX_CHARS = 2000

用法：
  python src/doc_retrieval.py "error: undeclared identifier 'println'"
"""
from __future__ import annotations

import math
import os
import re
import sys
import threading
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data import BENCH_DIR  # noqa: E402

DOC_DIR = os.path.join(BENCH_DIR, "CangjieDocCorpus")
TOP_K = 3
MAX_CHARS = 2000
K1, B = 1.5, 0.75

_IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_CAMEL_RE = re.compile(r"[A-Z]+(?=[A-Z][a-z])|[A-Z]?[a-z]+|[A-Z]+|\d+")
_CJK_RE = re.compile(r"[一-鿿]")
_HEADING_RE = re.compile(r"^(#{1,3})\s+(.*)$")


def tokenize(text: str) -> list[str]:
    toks = []
    for ident in _IDENT_RE.findall(text):
        toks.append(ident.lower())
        parts = _CAMEL_RE.findall(ident)
        if len(parts) > 1:
            toks.extend(p.lower() for p in parts)
    toks.extend(_CJK_RE.findall(text))
    return toks


def split_sections(text: str, source: str) -> list[dict]:
    """按 #、##、### 标题切块；每块的 title 为 "文件 > 一级 > 二级 > 三级"。"""
    stack: list[str] = []
    chunks, buf = [], []

    def flush():
        body = "\n".join(buf).strip()
        if body:
            chunks.append({"title": " > ".join([source] + stack), "text": body})
        buf.clear()

    for line in text.splitlines():
        m = _HEADING_RE.match(line)
        if m:
            flush()
            level = len(m.group(1))
            stack[:] = stack[: level - 1] + [m.group(2).strip()]
        else:
            buf.append(line)
    flush()
    return chunks


class BM25:
    def __init__(self, docs: list[list[str]]):
        self.n = len(docs)
        self.tf = [Counter(d) for d in docs]
        self.len = [len(d) for d in docs]
        self.avg = sum(self.len) / max(self.n, 1)
        df = Counter(t for d in self.tf for t in d)
        self.idf = {t: math.log(1 + (self.n - c + 0.5) / (c + 0.5)) for t, c in df.items()}

    def scores(self, query: list[str]) -> list[float]:
        q = [t for t in set(query) if t in self.idf]
        out = []
        for tf, dl in zip(self.tf, self.len):
            s = 0.0
            for t in q:
                f = tf.get(t, 0)
                if f:
                    s += self.idf[t] * f * (K1 + 1) / (f + K1 * (1 - B + B * dl / self.avg))
            out.append(s)
        return out


_index = None
_lock = threading.Lock()


def load_chunks(doc_dir: str = DOC_DIR) -> list[dict]:
    chunks = []
    for root, _, files in os.walk(doc_dir):
        for fn in sorted(files):
            if fn.endswith(".md"):
                path = os.path.join(root, fn)
                with open(path, encoding="utf-8") as f:
                    rel = os.path.relpath(path, doc_dir).replace(os.sep, "/")
                    chunks.extend(split_sections(f.read(), rel))
    return chunks


def get_index():
    global _index
    with _lock:
        if _index is None:
            chunks = load_chunks()
            if not chunks:
                raise FileNotFoundError(f"文档语料为空：{DOC_DIR}")
            _index = (chunks, BM25([tokenize(c["title"] + "\n" + c["text"]) for c in chunks]))
    return _index


# cjc 报错中的固定套话，不携带语言知识，查询时剔除
_STOP = set("""error errors warning warnings generated printed expected found here main cj note
the a an of to is in on for be can not this that with by or and as at it its from was
here''""".split())
_SRC_LINE_RE = re.compile(r"^\s*\d+\s*\|\s?(.*)$")
MAX_ERROR_BLOCKS = 3


def build_query(feedback: str) -> str:
    """从报错中取前 MAX_ERROR_BLOCKS 个 error 块：错误描述 + 出错源码行（跳过 warning 块）。"""
    blocks, cur, keep = [], [], False
    for line in feedback.splitlines():
        if line.startswith(("error:", "warning:")):
            if keep and cur:
                blocks.append(cur)
            cur, keep = [line[line.index(":") + 1:]], line.startswith("error:")
        elif keep:
            m = _SRC_LINE_RE.match(line)
            if m and m.group(1).strip():
                cur.append(m.group(1))
    if keep and cur:
        blocks.append(cur)
    if not blocks:  # 非编译错误（运行时异常等）：直接用原文
        return feedback
    return "\n".join("\n".join(b) for b in blocks[:MAX_ERROR_BLOCKS])


def query_tokens(query: str) -> list[str]:
    return [t for t in tokenize(query) if t not in _STOP]


def retrieve(query: str, k: int = TOP_K) -> list[dict]:
    chunks, bm25 = get_index()
    scores = bm25.scores(query_tokens(query))
    order = sorted(range(len(chunks)), key=lambda i: (-scores[i], i))[:k]
    return [dict(chunks[i], score=round(scores[i], 3)) for i in order if scores[i] > 0]


def format_docs(chunks: list[dict], max_chars: int = MAX_CHARS) -> str:
    """把检索结果拼成提示文本；总长按块数平均分配，超出部分截断。"""
    if not chunks:
        return "(no relevant documentation found)"
    per = max_chars // len(chunks)
    parts = []
    for c in chunks:
        head = f"[{c['title']}]\n"
        body = c["text"][: max(per - len(head), 0)]
        parts.append(head + body)
    return "\n\n".join(parts)


def retrieve_for_feedback(feedback: str, k: int = TOP_K) -> list[dict]:
    return retrieve(build_query(feedback), k)


def main():
    query = " ".join(sys.argv[1:]) or sys.stdin.read()
    for c in retrieve_for_feedback(query):
        print(f"--- score={c['score']}  {c['title']}")
        print(c["text"][:400])
        print()


if __name__ == "__main__":
    main()
